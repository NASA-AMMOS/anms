#!/usr/bin/env python3
"""Phase C: OpenSearch Logging Latency.

Measures per-request overhead for the logging write path and the query read path.
Supports direct mode (no cookies) and authnz mode (with cookies).

Usage:
    python3 stress_logging_latency.py <direct:0|1> <cookie_file_or_empty> <metrics_dir> <base_port>
"""

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


def timed_write(base_url, session, n=50):
    """Time sequential logging write requests."""
    url = f"{base_url}/logging"
    data = json.dumps({"message": "stress-test-heartbeat"}).encode()
    headers = {"Content-Type": "application/json"}
    if session:
        headers["Cookie"] = session
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    latencies = []
    codes = {}
    errors = 0
    start = time.monotonic()

    for _ in range(n):
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                r.read()
                latencies.append(time.monotonic() - t0)
                codes[r.status] = codes.get(r.status, 0) + 1
        except urllib.error.HTTPError as e:
            latencies.append(time.monotonic() - t0)
            codes[e.code] = codes.get(e.code, 0) + 1
            errors += 1
        except Exception:
            latencies.append(time.monotonic() - t0)
            errors += 1

    elapsed = time.monotonic() - start
    percentiles = compute_percentiles(latencies, (0.5, 0.95, 0.99))
    p50, p95, p99 = (percentiles + [0, 0, 0])[:3]

    success = n - errors
    return {
        "type": "write",
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
        "codes": dict(sorted(codes.items())),
    }


def timed_query(base_url, session, n=50):
    """Time sequential logging query requests."""
    url = f"{base_url}/logging/query"
    data = json.dumps({"limit": 10}).encode()
    headers = {"Content-Type": "application/json"}
    if session:
        headers["Cookie"] = session
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    latencies = []
    codes = {}
    errors = 0
    start = time.monotonic()

    for _ in range(n):
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read()
                latencies.append(time.monotonic() - t0)
                codes[r.status] = codes.get(r.status, 0) + 1
        except urllib.error.HTTPError as e:
            latencies.append(time.monotonic() - t0)
            codes[e.code] = codes.get(e.code, 0) + 1
            errors += 1
        except Exception:
            latencies.append(time.monotonic() - t0)
            errors += 1

    elapsed = time.monotonic() - start
    percentiles = compute_percentiles(latencies, (0.5, 0.95, 0.99))
    p50, p95, p99 = (percentiles + [0, 0, 0])[:3]

    success = n - errors
    return {
        "type": "query",
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
        "codes": dict(sorted(codes.items())),
    }


def summarize(label, result):
    if not result:
        return ""
    avg = result.get("avg_ms", 0)
    p95 = result.get("p95_ms", 0)
    p99 = result.get("p99_ms", 0)
    tp = result.get("throughput", 0)
    return f"    {label}: avg={avg}ms  p95={p95}ms  p99={p99}ms  {tp} req/s"


def main():
    # Args: direct cookie_file metrics_dir base_port
    args = sys.argv[1:]
    if len(args) != 4:
        print(f"Usage: python3 {sys.argv[0]} <direct:0|1> <cookie_file_or_empty> <metrics_dir> <base_port>", file=sys.stderr)
        sys.exit(1)

    direct = int(args[0])
    cookie_file = args[1]
    metrics_dir = args[2]
    base_port = args[3]

    session = "" if direct else parse_cookie_file(cookie_file)
    base_url = f"http://localhost:{base_port}"
    mode_str = "direct" if direct else "authnz"
    print(f"  Mode: {mode_str} (port {base_port})")

    print("  Sequential write path:")
    write_result = timed_write(base_url, session)
    print(summarize("write", write_result))

    print("  Sequential query path:")
    query_result = timed_query(base_url, session)
    print(summarize("query", query_result))

    write_avg = write_result.get("avg_ms", 0)
    query_avg = query_result.get("avg_ms", 0)

    results = {"write": write_result, "query": query_result}

    with open(os.path.join(metrics_dir, "logging_results.json"), "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n  Logging overhead (write + query): {round(write_avg + query_avg, 1)}ms total")


if __name__ == "__main__":
    main()
