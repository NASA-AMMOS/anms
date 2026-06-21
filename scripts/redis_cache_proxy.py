#!/usr/bin/env python3
"""Redis Caching Proxy for ANMS.

Intercepts HTTP requests to anms-core and adds Redis caching for:
- GET /report/* endpoints
- GET /ari/all endpoint
- GET /agents/all endpoint

Usage:
    python3 redis_cache_proxy.py [--port 5556] [--redis-host redis]

Start this as a separate service, then configure clients to hit port 5556 instead of 5555.
"""

import json
import os
import signal
import sys
import time
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import hashlib
import redis


# Redis connection
redis_client = None


def get_redis_client(host='localhost', port=6379, db=0):
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            redis_client.ping()  # Test connection
            print(f"[OK] Redis connected to {host}:{port}", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"[ERR] Redis connection failed: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
            redis_client = None
    return redis_client


# Cache TTLs (seconds)
CACHE_TTLS = {
    '/report/page': 60,
    '/report/all': 60,
    '/report/name': 60,
    '/ari/all': 30,
    '/agents/all': 30,
    '/sys_status/services': 60,
    '/nm/version': 300,  # Rarely changes
}


def get_cache_key(method, path, query=""):
    """Generate cache key from request."""
    key = f"{method}:{path}:{query}"
    return hashlib.md5(key.encode()).hexdigest()


def cached_request(method, path, query="", timeout=30):
    """Make request with Redis caching."""
    # Only cache GET requests
    if method != 'GET':
        return forward_request(method, path, query, timeout)
    
    # Check if this endpoint should be cached
    cache_base = path.split('?')[0]
    ttl = CACHE_TTLS.get(cache_base)
    
    if ttl is None:
        return forward_request(method, path, query, timeout)
    
    cache_key = get_cache_key(method, cache_base, query)
    r = get_redis_client()
    
    if r is None:
        print("[WARN] Redis not available, skipping cache", file=sys.stderr, flush=True)
        return forward_request(method, path, query, timeout)
    
    try:
        # Try to get from cache
        cached = r.get(cache_key)
        if cached:
            cached_result = json.loads(cached)
            cached_result['cached'] = True  # Mark as cache hit
            print(f"[CACHE HIT] {method} {path}", file=sys.stderr, flush=True)
            return cached_result
        print(f"[CACHE MISS] {method} {path}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"[ERR] Redis GET failed: {e}", file=sys.stderr, flush=True)
    
    # Forward request
    result = forward_request(method, path, query, timeout)
    
    # Cache the result if successful
    if result and result.get('status', 0) == 200 and result.get('body'):
        try:
            r.setex(cache_key, ttl, json.dumps(result))
        except Exception as e:
            print(f"[ERR] Redis SET failed: {e}", file=sys.stderr, flush=True)
    
    return result


def forward_request(method, path, query="", timeout=30):
    """Forward request to actual anms-core service."""
    core_url = f"http://localhost:5555{path}"
    if query:
        core_url += f"?{query}"
    
    try:
        req = urllib.request.Request(core_url, method=method)
        if method == 'PUT':
            req.data = b""
            req.add_header("Content-Length", "0")
        
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode('utf-8', errors='replace')
            return {
                'status': r.status,
                'body': body,
                'cached': False,
            }
    except urllib.error.HTTPError as e:
        return {
            'status': e.code,
            'body': e.read().decode('utf-8', errors='replace') if e.read else '',
            'cached': False,
        }
    except Exception as e:
        return {
            'status': 502,
            'body': f"Proxy error: {str(e)}",
            'cached': False,
        }


class CacheProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = parsed.query
        
        result = cached_request('GET', path, query)
        
        self.send_response(result['status'])
        self.send_header('Content-Type', 'application/json')
        if result.get('cached'):
            self.send_header('X-Cache', 'HIT')
        else:
            self.send_header('X-Cache', 'MISS')
        self.end_headers()
        self.wfile.write(result['body'].encode('utf-8'))
    
    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        result = forward_request('PUT', path)
        
        self.send_response(result['status'])
        self.send_header('Content-Type', 'application/json')
        self.send_header('X-Cache', 'BYPASS')
        self.end_headers()
        self.wfile.write(result['body'].encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress request logging."""
        pass


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5556
    
    print(f"Starting Redis caching proxy on port {port}")
    print(f"  Cache TTLs:")
    for path, ttl in CACHE_TTLS.items():
        print(f"    {path}: {ttl}s")
    print(f"  Backend: localhost:5555")
    
    server = HTTPServer(('0.0.0.0', port), CacheProxyHandler)
    print(f"Proxy started. Listening on port {port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
