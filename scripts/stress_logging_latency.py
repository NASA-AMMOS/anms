#!/usr/bin/env python3
"""Phase C: OpenSearch Logging Latency.

Measures per-request overhead for the logging write path and the query read path.

Usage:
    python3 stress_logging_latency.py <cookie_file> <metrics_dir> <authnz_port>
"""

import json
import os
import statistics
import sys
import time
import urllib.request

from stress_utils import safe_mean


def make_log_request(url, cookie):
    """POST a single logging request, return (latency, succeeded)."""
    req = urllib.request.Request(
        url,
        data=b'{"message": "stress-test-log"}',
        headers={
            "Cookie": cookie,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()
            return (time.monotonic() - t0, True)
    except Exception:
        return (time.monotonic() - t0, False)


def make_query_request(url, cookie):
    """POST a logging query, return (latency, succeeded)."""
    req = urllib.request.Request(
        url,
        data=b'{"limit": 10}',
        headers={
            "Cookie": cookie,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()
            return (time.monotonic() - t0, True)
    except Exception:
        return (time.monotonic() - t0, False)


def summarize(latencies, name):
    """Return a dict of ms-converted percentiles for the given latencies."""
    if not latencies:
        return {
            "avg_ms": 0,
            "p50_ms": 0,
            "p95_ms": 0,
            "p99_ms": 0,
            "n": 0,
        }
    s = sorted(latencies)
    n = len(s)
    return {
        "avg_ms": round(sum(s) / n * 1000, 1),
        "p50_ms": round(s[n // 2] * 1000, 1),
        "p95_ms": round(s[min(int(n * 0.95), n - 1)] * 1000, 1),
        "p99_ms": round(s[min(int(n * 0.99), n - 1)] * 1000, 1),
        "n": n,
    }


def main():
    cookie_file = sys.argv[1]
    metrics_dir = sys.argv[2]
    authnz_port = sys.argv[3]
    cookie = open(cookie_file).read().strip()

    # --- Write path: sequential /logging POST ---
    print("  Sequential (no concurrency) - measures per-request overhead:")
    latencies = []
    for i in range(100):
        d, _ = make_log_request(
            f"http://localhost:{authnz_port}/logging", cookie
        )
        latencies.append(d)

    write_result = summarize(latencies, "write")
    print(
        f"    avg={write_result['avg_ms']:.1f}ms"
        f"  p50={write_result['p50_ms']:.1f}ms"
        f"  p95={write_result['p95_ms']:.1f}ms"
        f"  p99={write_result['p99_ms']:.1f}ms"
    )

    # --- Read path: sequential /logging/query POST ---
    print("  Sequential /logging/query (read path):")
    latencies_r = []
    for i in range(100):
        d, _ = make_query_request(
            f"http://localhost:{authnz_port}/logging/query", cookie
        )
        latencies_r.append(d)

    read_result = summarize(latencies_r, "read")
    print(
        f"    avg={read_result['avg_ms']:.1f}ms"
        f"  p50={read_result['p50_ms']:.1f}ms"
        f"  p95={read_result['p95_ms']:.1f}ms"
    )

    # Save results
    with open(os.path.join(metrics_dir, "logging_latency.json"), "w") as f:
        json.dump({"write": write_result, "read": read_result}, f, indent=2)


if __name__ == "__main__":
    main()
