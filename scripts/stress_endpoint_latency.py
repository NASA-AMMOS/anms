#!/usr/bin/env python3
"""Phase B: Per-Endpoint Latency Breakdown.

Measures latency, throughput, and response size for every ANMS endpoint.

Usage:
    python3 stress_endpoint_latency.py <cookie_file> <metrics_dir> <authnz_port>
"""

import concurrent.futures
import json
import os
import sys
import time
import urllib.error
import urllib.request

from stress_utils import safe_throughput, compute_percentiles

# Endpoint definitions: (method, path, display_label)
ENDPOINTS = [
    ("GET", "/core/hello", "core-hello"),
    ("GET", "/ari/all", "ari-all"),
    ("GET", "/ari/all/display", "ari-all-display"),
    ("GET", "/actual_objects/all", "actual-objects"),
    ("GET", "/formal_objects/all", "formal-objects"),
    ("GET", "/agents/all", "agents"),
    ("GET", "/report/page", "report-page"),
    ("GET", "/report/all", "report-all"),
    ("GET", "/grafana/api/health", "grafana-health"),
    ("GET", "/grafana/api/org", "grafana-org"),
    ("GET", "/grafana/api/search", "grafana-search"),
    ("POST", "/logging", "POST-logging"),
    ("POST", "/logging/query", "POST-logging-query"),
    ("POST", "/adms/load_default", "POST-load-default"),
    ("POST", "/users", "POST-users"),
    ("PUT", "/transcoder/ui/incoming/str", "PUT-transcoder"),
    ("PUT", "/alerts/acknowledge/1", "PUT-alerts-ack"),
]

# POST/PUT payloads keyed by (method, path)
PAYLOADS = {
    ("POST", "/logging"): '{"message": "stress-test-heartbeat"}',
    ("POST", "/logging/query"): '{"limit": 10}',
    ("POST", "/users"): '{"username": "stresstest"}',
}

CONTENT_TYPES = {
    ("POST", "/logging"): "application/json",
    ("POST", "/logging/query"): "application/json",
    ("POST", "/users"): "application/json",
}


def timed_request(method, url, cookie, payload=None, content_type=None,
                  concurrency=5, n=50):
    """Time a batch of requests and return structured results."""
    hdrs = {"Cookie": cookie}
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
    cookie_file = sys.argv[1]
    metrics_dir = sys.argv[2]
    authnz_port = sys.argv[3]

    cookie = open(cookie_file).read().strip()
    results = {}

    print("  {:30s} {:>10} {:>8} {:>8} {:>8} {:>6} {:>8}".format(
        "Endpoint", "req/s", "avg_ms", "p50_ms", "p95_ms", "p99_ms", "errors"
    ))

    for method, path, label in ENDPOINTS:
        url = f"http://localhost:{authnz_port}{path}"
        payload = PAYLOADS.get((method, path))
        content_type = CONTENT_TYPES.get((method, path))

        r = timed_request(method, url, cookie, payload, content_type)
        results[label] = r
        print(
            f"  {label:30s}"
            f" {r['throughput']:8.1f}"
            f" {r['avg_ms']:6.1f}"
            f" {r['p50_ms']:6.1f}"
            f" {r['p95_ms']:6.1f}"
            f" {r['p99_ms']:6.1f}"
            f" {r['errors']:4d}"
        )

    # Save results
    with open(os.path.join(metrics_dir, "endpoint_results.json"), "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
