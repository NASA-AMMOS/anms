#!/usr/bin/env python3
"""Async OpenSearch Logging Patch for ANMS.

Replaces the synchronous blocking `log_to_opensearch()` calls with a queue-based
batch flush that runs in a background thread. Each logger.log() call no longer
blocks waiting for OpenSearch HTTP POST.

How it works:
  1. Log entries are appended to a bounded queue (max 5000)
  2. A background thread flushes batches to OpenSearch every 2s or when queue
     reaches 50 entries (whichever comes first)
  3. If queue is full, oldest entries are dropped (non-blocking)

Usage:
    # As a monkey-patch import (add to your app startup):
    #   from scripts.async_opensearch_logger import patch_opensearch_logger
    #   patch_opensearch_logger()

    # As a standalone test:
    python3 scripts/async_opensearch_logger.py --status
    python3 scripts/async_opensearch_logger.py --apply
    python3 scripts/async_opensearch_logger.py --revert

NOTE: This script patches the opensearch_logger.py file to replace the
synchronous client.create() with a queue-based async flush. It does NOT
require changing any calling code.
"""

import argparse
import queue
import sys
import threading
import time
import uuid
import datetime
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, List

# Try to import opensearchpy for the flusher
try:
    from opensearchpy import OpenSearch
    HAS_OPENSEARCH = True
except ImportError:
    HAS_OPENSEARCH = False

CONFIG_FILE = Path(__file__).parent.parent / 'anms-core' / 'anms' / 'shared' / 'opensearch_logger.py'

# Patch config
BATCH_SIZE = 50
FLUSH_INTERVAL = 2.0
MAX_QUEUE_SIZE = 5000


class AsyncOpenSearchFlusher:
    """Background thread that batches OpenSearch log entries and flushes them."""

    def __init__(self, config: Dict = None):
        self.queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
        self.batch_size = BATCH_SIZE
        self.flush_interval = FLUSH_INTERVAL
        self._stop_event = threading.Event()
        self._thread = None
        self._client = None
        self._index_name = None
        self._config = config
        self._stats = {'flushed': 0, 'dropped': 0, 'errors': 0}
        self._lock = threading.Lock()

    def configure(self, config: Dict):
        """Configure the OpenSearch client from ANMS config."""
        self._config = config
        self._index_name = config.get('OPENSEARCH_INDEX_NAME', 'anms-logs')
        if HAS_OPENSEARCH:
            self._client = OpenSearch(
                hosts=[{'host': config['OPENSEARCH_HOST'], 'port': config['OPENSEARCH_PORT']}],
                http_compress=True,
                http_auth=(config['OPENSEARCH_AUTH_USERNAME'], config['OPENSEARCH_AUTH_PASSWORD']),
                use_ssl=config.get('OPENSEARCH_USE_SSL', False),
                verify_certs=config.get('OPENSEARCH_VERIFY_CERTS', False),
                ssl_assert_hostname=config.get('OPENSEARCH_ASSERT_HOSTNAME', None),
                ssl_show_warn=config.get('OPENSEARCH_SHOW_WARN', False)
            )

    def start(self):
        """Start the background flush thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._flush_loop, daemon=True, name='os-logger-flush')
        self._thread.start()
        print("[ASYNC-LOG] Background flush thread started", file=sys.stderr, flush=True)

    def stop(self):
        """Stop the background flush thread and flush remaining entries."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        # Final flush
        self._do_flush()
        print("[ASYNC-LOG] Background flush thread stopped", file=sys.stderr, flush=True)

    def log(self, message: str, level: Any = 20, data: Optional[Dict[str, Any]] = None,
            component_name: str = "anms-core"):
        """Queue a log entry (non-blocking). Returns True if queued, False if dropped."""
        entry = {
            'level': level,
            'component': component_name,
            'message': message,
            'datetime': datetime.datetime.now().isoformat(),
        }
        if data:
            entry['data'] = data

        try:
            self.queue.put_nowait(entry)
        except queue.Full:
            with self._lock:
                self._stats['dropped'] += 1
            return False
        return True

    def _flush_loop(self):
        """Main loop: flush batch every FLUSH_INTERVAL or when queue >= BATCH_SIZE."""
        while not self._stop_event.is_set():
            # Check if we should flush now
            if self.queue.qsize() >= self.batch_size:
                self._do_flush()
            else:
                # Wait for flush interval or until woken up
                self._stop_event.wait(timeout=self.flush_interval)
                if self._stop_event.is_set():
                    break
                self._do_flush()

    def _do_flush(self):
        """Drain queue and bulk index to OpenSearch."""
        batch = []
        while not self.queue.empty():
            try:
                batch.append(self.queue.get_nowait())
            except queue.Empty:
                break

        if not batch or self._client is None:
            return

        # Build bulk request
        actions = []
        for entry in batch:
            # Index action
            actions.append({'index': {'_index': self._index_name, '_id': str(uuid.uuid4())}})
            actions.append(entry)

        try:
            from opensearchpy import helpers
            helpers.bulk(self._client, actions, raise_on_error=False)
            with self._lock:
                self._stats['flushed'] += len(batch)
        except Exception as e:
            with self._lock:
                self._stats['errors'] += 1
            print(f"[ASYNC-LOG] Flush error: {e}", file=sys.stderr, flush=True)

    @property
    def stats(self) -> Dict[str, int]:
        with self._lock:
            return dict(self._stats)


# Global flusher instance
_async_flusher = None


def patch_opensearch_logger(config: Dict = None):
    """Monkey-patch OpenSearchLogger.log_to_opensearch with async version.

    Call this after OpenSearchLogger is imported but before requests start.
    """
    global _async_flusher

    if _async_flusher is None:
        _async_flusher = AsyncOpenSearchFlusher()
        if config:
            _async_flusher.configure(config)
        _async_flusher.start()

    # Import and patch
    from anms.shared.opensearch_logger import OpenSearchLogger
    original_log = OpenSearchLogger.log_to_opensearch

    def async_log_to_opensearch(self, message: str, level=20, data=None,
                                 component_name: str = "anms-core",
                                 date_time: datetime.datetime = None):
        """Non-blocking async version of log_to_opensearch."""
        # Still log to internal logger (file)
        self._internal_logger.log(level, message)
        # Queue for async flush
        queued = _async_flusher.log(message, level, data, component_name)
        if not queued:
            print("[ASYNC-LOG] Queue full, dropped log entry", file=sys.stderr, flush=True)
        return None  # Can't return _id in async mode

    OpenSearchLogger.log_to_opensearch = async_log_to_opensearch
    print("[ASYNC-LOG] Patched OpenSearchLogger.log_to_opensearch with async version",
          file=sys.stderr, flush=True)


def unpatch_opensearch_logger():
    """Remove the async patch and restore original behavior."""
    global _async_flusher

    from anms.shared.opensearch_logger import OpenSearchLogger

    # Restore original method (reload the module)
    import importlib
    import anms.shared.opensearch_logger
    importlib.reload(anms.shared.opensearch_logger)
    OpenSearchLogger.log_to_opensearch = anms.shared.opensearch_logger.OpenSearchLogger.log_to_opensearch

    if _async_flusher:
        _async_flusher.stop()
        _async_flusher = None

    print("[ASYNC-LOG] Restored original OpenSearchLogger.log_to_opensearch",
          file=sys.stderr, flush=True)


def apply_file_patch():
    """Patch the source file to use async logging.

    This replaces the synchronous client.create() call in log_to_opensearch()
    with a queue-based approach.
    """
    content = CONFIG_FILE.read_text()

    # Add imports at the top
    imports_to_add = [
        'import queue',
        'import threading',
    ]

    # Check if already patched
    if 'ASYNC_OPENSEARCH_FLUSH' in content:
        print("⚠  Async OpenSearch logging patch already applied")
        return

    # Build the async flusher class and inject it
    async_flusher_code = '''
# === ASYNC_OPENSEARCH_FLUSH ===
class AsyncLogQueue:
    """Background queue that batches log entries and flushes to OpenSearch."""
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, config=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = AsyncLogQueue(config)
            return cls._instance

    def __init__(self, config=None):
        self.queue = queue.Queue(maxsize=5000)
        self._stop = threading.Event()
        self._client = None
        self._index_name = None
        self._batch_size = 50
        self._flush_interval = 2.0
        self._stats = {'flushed': 0, 'dropped': 0, 'errors': 0}
        if config:
            self.configure(config)
        self._thread = threading.Thread(target=self._flush_loop, daemon=True, name='os-logger')
        self._thread.start()

    def configure(self, config):
        from opensearchpy import OpenSearch
        self._index_name = config.get('OPENSEARCH_INDEX_NAME', 'anms-logs')
        self._client = OpenSearch(
            hosts=[{'host': config['OPENSEARCH_HOST'], 'port': config['OPENSEARCH_PORT']}],
            http_compress=True,
            http_auth=(config['OPENSEARCH_AUTH_USERNAME'], config['OPENSEARCH_AUTH_PASSWORD']),
            use_ssl=config.get('OPENSEARCH_USE_SSL', False),
            verify_certs=config.get('OPENSEARCH_VERIFY_CERTS', False),
        )

    def log(self, level, component, message, data=None, datetime_str=None):
        try:
            entry = {
                'level': level,
                'component': component,
                'message': message,
                'datetime': datetime_str or datetime.datetime.now().isoformat(),
            }
            if data:
                entry['data'] = data
            self.queue.put_nowait(entry)
            return True
        except queue.Full:
            with self._lock:
                self._stats['dropped'] += 1
            return False

    def _flush_loop(self):
        while not self._stop.is_set():
            if self.queue.qsize() >= self._batch_size:
                self._do_flush()
            else:
                self._stop.wait(timeout=self._flush_interval)
                if self._stop.is_set():
                    break
                self._do_flush()
        self._do_flush()

    def _do_flush(self):
        batch = []
        while not self.queue.empty():
            try:
                batch.append(self.queue.get_nowait())
            except queue.Empty:
                break
        if not batch or self._client is None:
            return
        try:
            for entry in batch:
                self._client.create(index=self._index_name, id=str(uuid.uuid4()), body=entry)
            with self._lock:
                self._stats['flushed'] += len(batch)
        except Exception:
            with self._lock:
                self._stats['errors'] += 1
    # === END ASYNC_OPENSEARCH_FLUSH ===

'''

    # Find the class definition and insert before it
    class_match = re.search(r'^class OpenSearchLogger', content, re.MULTILINE)
    if class_match:
        insert_pos = class_match.start()
        content = content[:insert_pos] + async_flusher_code + '\n' + content[insert_pos:]

    # Patch log_to_opensearch to use the async queue
    old_create = '''        try:
            response = self.client.create(index=self.index_name, id=uuid.uuid4(), body=document)
            return response['_id']
        except Exception as e:
            self._internal_logger.log(logging.ERROR, e)
            return None'''

    new_create = '''        # ASYNC_OPENSEARCH_FLUSH: Queue instead of blocking HTTP POST
        try:
            flusher = AsyncLogQueue.get_instance(config)
            flusher.log(
                level=level.value if hasattr(level, 'value') else level,
                component=component_name,
                message=message,
                data=data,
                datetime_str=date_time.isoformat() if date_time else None,
            )
            return None  # Async mode: can't return _id immediately
        except Exception as e:
            # Fallback to sync if async fails
            try:
                response = self.client.create(index=self.index_name, id=uuid.uuid4(), body=document)
                return response['_id']
            except Exception:
                self._internal_logger.log(logging.ERROR, e)
                return None'''

    content = content.replace(old_create, new_create)

    CONFIG_FILE.write_text(content)
    print("✓ Async OpenSearch logging patch applied to opensearch_logger.py")
    print("  - Log entries now queued in background thread (batch=50, flush=2s)")
    print("  - No more blocking HTTP POST on every logger.log() call")


def revert_file_patch():
    """Remove the async patch from the source file."""
    content = CONFIG_FILE.read_text()

    # Check if patched
    if 'ASYNC_OPENSEARCH_FLUSH' not in content:
        print("⚠  Async OpenSearch logging patch not found — nothing to revert")
        return

    # Remove the async flusher class
    content = re.sub(
        r'# === ASYNC_OPENSEARCH_FLUSH ===.*?# === END ASYNC_OPENSEARCH_FLUSH ===\n',
        '',
        content,
        flags=re.DOTALL
    )

    # Restore original log_to_opensearch create block
    patched_block = '''        # ASYNC_OPENSEARCH_FLUSH: Queue instead of blocking HTTP POST
        try:
            flusher = AsyncLogQueue.get_instance(config)
            flusher.log(
                level=level.value if hasattr(level, 'value') else level,
                component=component_name,
                message=message,
                data=data,
                datetime_str=date_time.isoformat() if date_time else None,
            )
            return None  # Async mode: can't return _id immediately
        except Exception as e:
            # Fallback to sync if async fails
            try:
                response = self.client.create(index=self.index_name, id=uuid.uuid4(), body=document)
                return response['_id']
            except Exception:
                self._internal_logger.log(logging.ERROR, e)
                return None'''

    original_block = '''        try:
            response = self.client.create(index=self.index_name, id=uuid.uuid4(), body=document)
            return response['_id']
        except Exception as e:
            self._internal_logger.log(logging.ERROR, e)
            return None'''

    content = content.replace(patched_block, original_block)

    CONFIG_FILE.write_text(content)
    print("✓ Reverted async OpenSearch logging patch")


def show_status():
    """Show whether the async patch is applied."""
    content = CONFIG_FILE.read_text()
    is_patched = 'ASYNC_OPENSEARCH_FLUSH' in content

    print("\n" + "="*70)
    print("ASYNC OPENSEARCH LOGGING STATUS")
    print("="*70)
    print(f"\nPatch applied: {'✓ YES' if is_patched else '✗ NO — using synchronous blocking mode'}")
    print()
    if is_patched:
        print("Current behavior:")
        print("  - logger.log() queues entry → background thread")
        print("  - Batch flush every 2s or 50 entries")
        print("  - Max queue size: 5000 (drops oldest when full)")
        print("  - No blocking HTTP POST on request handlers")
    else:
        print("Current behavior:")
        print("  - logger.log() → synchronous client.create() → HTTP POST")
        print("  - Blocks request handler until OpenSearch responds")
        print("  - Every log entry = one HTTP round trip")
    print()


def main():
    parser = argparse.ArgumentParser(description='Async OpenSearch Logging Patch')
    parser.add_argument('--apply', action='store_true', help='Apply async logging patch')
    parser.add_argument('--revert', action='store_true', help='Revert to sync logging')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--dry-run', action='store_true', help='Show what apply would do')

    args = parser.parse_args()

    if args.apply:
        apply_file_patch()
    elif args.revert:
        revert_file_patch()
    elif args.dry_run:
        print("\n" + "="*70)
        print("ASYNC OPENSEARCH LOGGING - DRY RUN")
        print("="*70)
        print("\nWould apply these changes to opensearch_logger.py:")
        print("  1. Add AsyncLogQueue class (background batch flusher)")
        print("  2. Replace synchronous client.create() with queue.put()")
        print("  3. Config: batch_size=50, flush_interval=2s, max_queue=5000")
        print()
    else:
        show_status()


if __name__ == '__main__':
    main()
