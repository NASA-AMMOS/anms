#!/usr/bin/env python3
"""Phase G: Grafana Rendering Path Latency.

Measures latency and response sizes for Grafana API and UI endpoints
through the authnz proxy.

Usage:
    python3 stress_grafana_path.py <cookie_file> <authnz_port>
"""

import concurrent.futures
import statistics
import sys
import time
import urllib.request

from stress_utils import safe_mean


def main():
    cookie_file = sys.argv[1]
    authnz_port = sys.argv[2]
    cookie = open(cookie_file).read().strip()

    grafana_endpoints = [
        "/grafana/api/health",
        "/grafana/api/org",
        "/grafana/api/search",
        "/grafana/",
    ]

    for ep in grafana_endpoints:
        url = f"http://localhost:{authnz_port}{ep}"
        latencies = []
        sizes = []
        errors = 0
        n = 200

        def do_req():
            t0 = time.monotonic()
            try:
                req = urllib.request.Request(url)
                req.add_header("Cookie", cookie)
                with urllib.request.urlopen(req, timeout=10) as r:
                    body = r.read()
                    return (time.monotonic() - t0, len(body))
            except Exception:
                return (999, 0)

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
            for f in concurrent.futures.as_completed(
                [ex.submit(do_req) for _ in range(n)]
            ):
                d, size = f.result()
                if d < 999:
                    latencies.append(d)
                    sizes.append(size)
                else:
                    errors += 1

        if latencies:
            s = sorted(latencies)
            avg_ms = round(safe_mean(s) * 1000, 0)
            p95_idx = min(int(len(s) * 0.95), len(s) - 1)
            p95_ms = round(s[p95_idx] * 1000, 0)
            p99_idx = min(int(len(s) * 0.99), len(s) - 1)
            p99_ms = round(s[p99_idx] * 1000, 0)
            avg_size = round(safe_mean(sizes))
        else:
            avg_ms = p95_ms = p99_ms = 0
            avg_size = 0

        if latencies:
            print(
                f"  {ep:30s}"
                f" avg={avg_ms}ms"
                f"  p95={p95_ms}ms"
                f"  p99={p99_ms}ms"
                f"  size={avg_size}B"
                f"  err={errors}"
            )


if __name__ == "__main__":
    main()
