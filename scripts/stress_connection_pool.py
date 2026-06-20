#!/usr/bin/env python3
"""Phase E: DB Connection Pool Saturation.

Fires concurrent requests at increasing concurrency levels and measures
error rates and latency degradation.

Usage:
    python3 stress_connection_pool.py <direct:0|1> <cookie_file_or_empty> <base_port>
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


def burst(base_url, session, n=100, concurrency=10):
    """Fire a burst of requests and return results."""
    urls = [
        f"{base_url}/nm/version",
        f"{base_url}/ari/all",
        f"{base_url}/actual_objects/all",
        f"{base_url}/agents/all",
        f"{base_url}/report/page",
    ]

    latencies = []
    codes = {}
    errors = 0
    start = time.monotonic()

    def do_req():
        t0 = time.monotonic()
        try:
            url = urls[hash(time.monotonic()) % len(urls)]
            req = urllib.request.Request(url)
            if session:
                req.add_header("Cookie", session)
            with urllib.request.urlopen(req, timeout=10) as r:
                r.read()
                return (time.monotonic() - t0, False, r.status)
        except urllib.error.HTTPError as e:
            return (time.monotonic() - t0, True, e.code)
        except Exception:
            return (time.monotonic() - t0, True, 0)

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = [ex.submit(do_req) for _ in range(n)]
        for f in concurrent.futures.as_completed(futures):
            d, failed, code = f.result()
            latencies.append(d)
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
        "error_pct": round(errors / n * 100, 1) if n > 0 else 0,
        "codes": dict(sorted(codes.items())),
    }


def main():
    # Args: direct cookie_file base_port
    args = sys.argv[1:]
    if len(args) != 3:
        print(f"Usage: python3 {sys.argv[0]} <direct:0|1> <cookie_file_or_empty> <base_port>", file=sys.stderr)
        sys.exit(1)

    direct = int(args[0])
    cookie_file = args[1]
    base_port = args[2]

    session = "" if direct else parse_cookie_file(cookie_file)
    base_url = f"http://localhost:{base_port}"
    mode_str = "direct" if direct else "authnz"
    print(f"  Mode: {mode_str} (port {base_port})")

    # Use the same concurrency levels as the original script
    concurrency_levels = [10, 50, 100, 150, 200]
    results = {}

    print("  {:>10s} {:>10s} {:>10s} {:>10s} {:>10s} {:>10s} {:>10s}".format(
        "Concurrency", "Throughput", "Avg Lat", "p50", "p95", "p99", "Errors"
    ))

    for concurrency in concurrency_levels:
        print(f"\n  --- {concurrency} concurrent workers ---")
        r = burst(base_url, session, n=100, concurrency=concurrency)
        label = f"c{concurrency}"
        results[label] = r
        print(
            f"    {concurrency:>8d}  {r['throughput']:7.1f} req/s"
            f"  {r['avg_ms']:6.1f}ms  {r['p50_ms']:5.1f}"
            f"  {r['p95_ms']:5.1f}  {r['p99_ms']:5.1f}"
            f"  {r['errors']:3d}"
        )

    # Save results
    metrics_dir = os.environ.get("TMP_DIR", "")
    if not metrics_dir:
        metrics_dir = os.path.join(os.path.dirname(__file__), "..", "stress-results")
    os.makedirs(metrics_dir, exist_ok=True)
    with open(os.path.join(metrics_dir, "pool_results.json"), "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
