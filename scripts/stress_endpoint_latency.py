#!/usr/bin/env python3
"""Phase B: Per-Endpoint Latency Breakdown.

Measures latency, throughput, and response size for every ANMS endpoint.
In direct mode, no cookies/auth needed (API on port 5555 is unauthenticated).

Usage:
    python3 stress_endpoint_latency.py <direct:0|1> <cookie_file_or_empty> <admin_cookie_file_or_empty> <metrics_dir> <base_port>
"""

import concurrent.futures
import json
import os
import sys
import time
import urllib.error
import urllib.request

from stress_utils import safe_throughput, compute_percentiles

def parse_cookie_file(cookie_file):
    """Parse a Netscape cookie file and extract session cookie value."""
    if not cookie_file or cookie_file == "":
        return ""
    cookie_text = open(cookie_file).read().strip()
    session = ""
    for line in cookie_text.split('\n'):
        if 'session' in line and not line.startswith('#'):
            parts = line.split('\t')
            session = parts[-1]
            break
    if not session:
        session = cookie_text
    return session


# Endpoint definitions: (method, path, display_label)
ENDPOINTS = [
    ("GET", "/nm/version", "nm-version"),
    ("GET", "/hello", "hello"),
    ("GET", "/ari/all", "ari-all"),
    ("GET", "/ari/all/display", "ari-all-display"),
    ("GET", "/agents/all", "agents"),
    ("GET", "/report/page", "report-page"),
    ("GET", "/report/all", "report-all"),
    ("GET", "/sys_status/services", "sys-status"),
    ("PUT", "/alerts/acknowledge/1", "PUT-alerts-ack"),
]

# POST/PUT payloads keyed by (method, path)
PAYLOADS = {
    ("POST", "/logging"): '{"message": "stress-test-heartbeat"}',
    ("POST", "/logging/query"): '{"limit": 10}',
    ("POST", "/adms/load_default"): '',  # no body needed
    ("POST", "/users"): '{"username": "stresstest"}',
}

CONTENT_TYPES = {
    ("POST", "/logging"): "application/json",
    ("POST", "/logging/query"): "application/json",
    ("POST", "/users"): "application/json",
}


def timed_request(method, url, cookie=None, payload=None, content_type=None,
                  concurrency=5, n=50):
    """Time a batch of requests and return structured results."""
    hdrs = {}
    if cookie:
        hdrs["Cookie"] = cookie
    if content_type:
        hdrs["Content-Type"] = content_type
    data = payload.encode() if payload else None
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)

    latencies = []
    body_sizes = []
    codes = {}
    errors = 0
    start = time.monotonic()

    def do_req():
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read()
                return (time.monotonic() - t0, False, r.status, len(body))
        except urllib.error.HTTPError as e:
            return (time.monotonic() - t0, True, e.code, 0)
        except Exception:
            return (time.monotonic() - t0, True, 0, 0)

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = [ex.submit(do_req) for _ in range(n)]
        for f in concurrent.futures.as_completed(futures):
            d, failed, code, size = f.result()
            latencies.append(d)
            body_sizes.append(size)
            codes[code] = codes.get(code, 0) + 1
            if failed:
                errors += 1

    elapsed = time.monotonic() - start
    percentiles = compute_percentiles(latencies, (0.5, 0.95, 0.99))
    p50, p95, p99 = (percentiles + [0, 0, 0])[:3]

    success = n - errors
    return {
        "n": n,
        "ok": success,
        "errors": errors,
        "elapsed_s": round(elapsed, 3),
        "throughput": safe_throughput(success, elapsed),
        "avg_ms": round(
            sum(latencies) / len(latencies) * 1000, 1
        ) if latencies else 0,
        "p50_ms": p50,
        "p95_ms": p95,
        "p99_ms": p99,
        "min_ms": round(min(latencies) * 1000, 1) if latencies else 0,
        "max_ms": round(max(latencies) * 1000, 1) if latencies else 0,
        "avg_body_bytes": round(
            sum(body_sizes) / len(body_sizes), 0
        ) if body_sizes else 0,
        "codes": dict(sorted(codes.items())),
    }


def main():
    # Args: direct cookie_file admin_cookie_file metrics_dir base_port
    args = sys.argv[1:]
    if len(args) != 5:
        print(f"Usage: python3 {sys.argv[0]} <direct:0|1> <cookie_file_or_empty> <admin_cookie_file_or_empty> <metrics_dir> <base_port>", file=sys.stderr)
        sys.exit(1)

    direct = int(args[0])
    cookie_file = args[1]
    admin_cookie_file = args[2]
    metrics_dir = args[3]
    base_port = args[4]

    user_cookie = "" if direct else parse_cookie_file(cookie_file)
    admin_cookie = "" if direct else parse_cookie_file(admin_cookie_file)
    
    mode_str = "direct" if direct else "authnz"
    print(f"  Mode: {mode_str} (port {base_port})")
    
    results = {}

    print("  {:30s} {:>8} {:>6} {:>6} {:>6} {:>6} {:>6}".format(
        "Endpoint", "req/s", "avg", "p50", "p95", "p99", "errors"
    ))

    for method, path, label in ENDPOINTS:
        url = f"http://localhost:{base_port}{path}"
        payload = PAYLOADS.get((method, path))
        content_type = CONTENT_TYPES.get((method, path))
        cookie = user_cookie  # In direct mode, no cookies needed

        r = timed_request(method, url, cookie, payload, content_type)
        results[label] = r
        print(
            f"  {label:30s}"
            f" {r['throughput']:6.1f}"
            f" {r['avg_ms']:5.1f}"
            f" {r['p50_ms']:5.1f}"
            f" {r['p95_ms']:5.1f}"
            f" {r['p99_ms']:5.1f}"
            f" {r['errors']:4d}"
        )

    # Save results
    with open(os.path.join(metrics_dir, "endpoint_results.json"), "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
