#!/usr/bin/env python3
"""Benchmark Harness for ANMS Optimization Patches.

Applies patches one at a time, runs stress tests, and compares results.
Patches tested independently so we can measure each contribution.

Usage:
    # Run all patches
    python3 scripts/benchmark_patches.py

    # Run specific patch
    python3 scripts/benchmark_patches.py --patch db_pool

    # Dry run (show what would happen)
    python3 scripts/benchmark_patches.py --dry-run

    # Custom endpoint (default: /report/page)
    python3 scripts/benchmark_patches.py --endpoint /report/page --workers 20

    # Use DIRECT mode (port 5555) or PROXY mode (port 5556 through Redis proxy)
    python3 scripts/benchmark_patches.py --direct
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.request
import urllib.error
import concurrent.futures
import statistics
from pathlib import Path
from datetime import datetime

# Scripts
BASE_DIR = Path(__file__).parent
ANMS_DIR = BASE_DIR.parent

PATCHES = {
    'db_pool': {
        'name': 'DB Pool Optimization',
        'apply': str(BASE_DIR / 'db_pool_optimizer.py'),
        'revert': str(BASE_DIR / 'db_pool_optimizer.py'),
        'apply_arg': '--apply',
        'revert_arg': '--revert',
        'status_arg': '--status',
        'requires_restart': True,  # config.py changes need service restart
    },
    'async_opensearch': {
        'name': 'Async OpenSearch Logging',
        'apply': str(BASE_DIR / 'async_opensearch_logger.py'),
        'revert': str(BASE_DIR / 'async_opensearch_logger.py'),
        'apply_arg': '--apply',
        'revert_arg': '--revert',
        'status_arg': '--status',
        'requires_restart': True,  # code changes need service restart
    },
    'redis_proxy': {
        'name': 'Redis Cache Proxy',
        'apply': str(BASE_DIR / 'redis_cache_proxy.py'),
        'revert': None,  # Start/stop script
        'apply_arg': '',  # Run directly
        'revert_arg': '',
        'status_arg': '',
        'requires_restart': False,  # Proxy is a separate process
        'notes': 'Requires Redis running on port 6379. Test through port 5556.',
    },
}


def timed_request(url, method="GET", timeout=30):
    """Make a request and measure latency."""
    start = time.monotonic()
    try:
        req = urllib.request.Request(url, method=method)
        if method == "PUT":
            req.data = b""
            req.add_header("Content-Length", "0")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read()
            latency = (time.monotonic() - start) * 1000
            cache_hit = r.getheader("X-Cache") == "HIT"
            return latency, 200, cache_hit
    except urllib.error.HTTPError as e:
        return (time.monotonic() - start) * 1000, e.code, False
    except Exception as e:
        return (time.monotonic() - start) * 1000, 0, False


def run_endpoint_benchmark(base_url, endpoint, num_requests=100, max_workers=20, direct=False):
    """Benchmark a single endpoint."""
    url = f"{base_url}{endpoint}"
    latencies = []
    errors = []
    hits = []

    def make_request(i):
        latency, status, hit = timed_request(url)
        if status != 200:
            errors.append(status)
        if hit:
            hits.append(1)
        return latency

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]
        for f in concurrent.futures.as_completed(futures):
            latencies.append(f.result())

    # Sort for percentiles
    latencies.sort()
    n = len(latencies)

    return {
        'endpoint': endpoint,
        'num_requests': n,
        'avg_ms': round(statistics.mean(latencies), 1),
        'median_ms': round(statistics.median(latencies), 1),
        'p95_ms': round(latencies[int(n * 0.95)], 1),
        'p99_ms': round(latencies[int(n * 0.99)], 1),
        'min_ms': round(latencies[0], 1),
        'max_ms': round(latencies[-1], 1),
        'errors': len(errors),
        'cache_hits': len(hits),
        'req_per_sec': round(n / (latencies[-1] / 1000 * n / max_workers), 1) if latencies else 0,
    }


def run_full_benchmark(base_url, direct=False):
    """Run benchmarks on all key endpoints."""
    endpoints = [
        '/report/page',
        '/report/page?page=2',
        '/agents/all',
        '/ari/all',
        '/sys_status/services',
    ]

    results = {}
    for ep in endpoints:
        print(f"  Benchmarking {ep}...", file=sys.stderr)
        results[ep] = run_endpoint_benchmark(base_url, ep)
        time.sleep(0.5)  # Brief cooldown between endpoints

    return results


def apply_patch(patch_name):
    """Apply a patch."""
    patch = PATCHES[patch_name]
    print(f"\n{'='*60}")
    print(f"Applying: {patch['name']}")
    print(f"{'='*60}")

    if patch_name == 'redis_proxy':
        # Start Redis proxy as background process
        proc = subprocess.Popen(
            [sys.executable, patch['apply'], '5556'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        time.sleep(2)  # Wait for startup
        return proc
    else:
        result = subprocess.run(
            [sys.executable, patch['apply'], patch['apply_arg']],
            capture_output=True, text=True, timeout=30
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return None


def revert_patch(patch_name, proc=None):
    """Revert a patch."""
    patch = PATCHES[patch_name]
    print(f"\nReverting: {patch['name']}")

    if patch_name == 'redis_proxy' and proc:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        return

    if patch['revert']:
        result = subprocess.run(
            [sys.executable, patch['revert'], patch['revert_arg']],
            capture_output=True, text=True, timeout=30
        )
        print(result.stdout)


def main():
    parser = argparse.ArgumentParser(description='Benchmark ANMS Optimization Patches')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be tested')
    parser.add_argument('--patch', type=str, default='all', help='Patch to test (db_pool, async_opensearch, redis_proxy, or all)')
    parser.add_argument('--endpoint', type=str, default='/report/page', help='Endpoint to benchmark')
    parser.add_argument('--num-requests', type=int, default=100, help='Requests per endpoint')
    parser.add_argument('--workers', type=int, default=20, help='Concurrent workers')
    parser.add_argument('--direct', action='store_true', help='Use direct port 5555 (default)')
    parser.add_argument('--proxy-port', type=int, default=5556, help='Redis proxy port (default: 5556)')
    parser.add_argument('--output', type=str, default=None, help='Save results to JSON file')

    args = parser.parse_args()

    if args.dry_run:
        print("\n" + "="*70)
        print("BENCHMARK PATCHES - DRY RUN")
        print("="*70)
        for name, patch in PATCHES.items():
            print(f"\n  {name}: {patch['name']}")
            print(f"    Script: {patch['apply']}")
            print(f"    Requires restart: {'YES' if patch['requires_restart'] else 'NO'}")
            if patch.get('notes'):
                print(f"    Notes: {patch['notes']}")
        print(f"\n  Endpoint: {args.endpoint}")
        print(f"  Workers: {args.workers}")
        print(f"  Requests: {args.num_requests}")
        print()
        return

    # Determine base URL
    if args.proxy_port and args.patch == 'redis_proxy':
        base_url = f"http://localhost:{args.proxy_port}"
    else:
        base_url = "http://localhost:5555"

    # Run baseline first
    print("\n" + "="*70)
    print("BASELINE (no patches)")
    print("="*70)
    baseline = run_endpoint_benchmark(base_url, args.endpoint, args.num_requests, args.workers)
    print(json.dumps(baseline, indent=2))

    # Run each patch
    patches_to_test = [args.patch] if args.patch != 'all' else ['db_pool', 'async_opensearch']

    results = {'baseline': baseline}
    procs = {}

    for patch_name in patches_to_test:
        if patch_name not in PATCHES:
            print(f"Unknown patch: {patch_name}", file=sys.stderr)
            continue

        # Apply patch
        proc = apply_patch(patch_name)
        if proc:
            procs[patch_name] = proc

        # Note: For patches requiring restart, user needs to restart the service
        # For now, we just apply the patch and run the benchmark
        patch = PATCHES[patch_name]
        if patch['requires_restart']:
            print(f"\n⚠  {patch['name']} requires service restart to take effect.")
            print(f"   Restart anms-core, then run: python3 {sys.argv[0]} --patch {patch_name} --no-restart")
            # Revert before moving on
            revert_patch(patch_name)
            continue

        # Run benchmark with patch applied
        test_base = f"http://localhost:{args.proxy_port}" if patch_name == 'redis_proxy' else base_url
        print(f"\n{'='*60}")
        print(f"WITH {patch['name'].upper()}")
        print(f"{'='*60}")
        patched = run_endpoint_benchmark(test_base, args.endpoint, args.num_requests, args.workers)
        results[patch_name] = patched
        print(json.dumps(patched, indent=2))

        # Revert
        revert_patch(patch_name, procs.get(patch_name))

    # Print comparison
    print(f"\n{'='*70}")
    print("COMPARISON")
    print(f"{'='*70}")
    print(f"\n{'Patch':<25} {'Avg (ms)':<12} {'Median (ms)':<14} {'P95 (ms)':<12} {'P99 (ms)':<12} {'Errors'}")
    print("-"*85)
    for name, result in results.items():
        label = name.upper() if name != 'baseline' else 'BASELINE'
        print(f"{label:<25} {result['avg_ms']:<12} {result['median_ms']:<14} {result['p95_ms']:<12} {result['p99_ms']:<12} {result['errors']}")

    # Save results
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to {output_path}")


if __name__ == '__main__':
    main()
