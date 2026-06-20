#!/usr/bin/env python3
"""Phase G: Grafana/rendering path latency.

Measures latency and response sizes for Grafana API and UI endpoints.
Supports direct mode (no cookies) and authnz mode (with cookies).

Usage:
    python3 stress_grafana_path.py <direct:0|1> <cookie_file_or_empty> <base_port>
"""

import concurrent.futures
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


def timed_get(base_url, session, path, n=50):
    """Time a batch of GET requests."""
    url = f"{base_url}{path}"
    latencies = []
    body_sizes = []
    codes = {}
    errors = 0
    start = time.monotonic()

    def do_req():
        t0 = time.monotonic()
        try:
            req = urllib.request.Request(url)
            if session:
                req.add_header("Cookie", session)
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read()
                return (time.monotonic() - t0, False, r.status, len(body))
        except urllib.error.HTTPError as e:
            return (time.monotonic() - t0, True, e.code, 0)
        except Exception:
            return (time.monotonic() - t0, True, 0, 0)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
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

    # Grafana is not on port 5555 in direct mode; skip if not found
    grafana_paths = [
        "/grafana/api/health",
        "/grafana/api/org",
        "/grafana/api/search",
        "/grafana",
    ]
    
    # In direct mode (port 5555), Grafana is on a different port (3000)
    # Only test Grafana in authnz mode or if port maps to Grafana
    if direct and base_port == 5555:
        print("  Skipping Grafana tests (not exposed on direct API port 5555)")
        return

    paths = grafana_paths
    print(f"  GET endpoint through {mode_str} proxy:")
    print(f"  {'Endpoint':30s} {'req/s':>8} {'avg':>6} {'p95':>6} {'p99':>6} {'body':>8} {'err':>4}")

    for path in paths:
        r = timed_get(base_url, session, path)
        ep = path.split('/')[-1] or path
        print(
            f"  {ep:30s}"
            f" {r['throughput']:8.1f}"
            f" {r['avg_ms']:6.1f}"
            f" {r['p95_ms']:6.1f}"
            f" {r['p99_ms']:6.1f}"
            f" {int(r.get('avg_body_bytes', 0)):8d}"
            f" {r['errors']:4d}"
        )


if __name__ == "__main__":
    main()
