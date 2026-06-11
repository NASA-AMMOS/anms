#!/usr/bin/env python3
"""Phase A: Proxy Overhead Measurement.

Measures round-trip latency through Apache (authnz) vs direct container access,
then computes overhead percentages.

Usage:
    python3 stress_proxy_overhead.py <cookie_file> <metrics_dir> <authnz_port>
"""

import concurrent.futures
import json
import os
import sys
import time
import urllib.error
import urllib.request

from stress_utils import safe_throughput, compute_percentiles


def timed_request(url, label, cookie, concurrency=5, n=50):
    """Time a batch of requests and return structured results."""
    latencies = []
    codes = {}
    errors = 0
    start = time.monotonic()

    def do_req():
        t0 = time.monotonic()
        try:
            req = urllib.request.Request(url)
            req.add_header("Cookie", cookie)
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
        "label": label,
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


def main():
    cookie_file = sys.argv[1]
    metrics_dir = sys.argv[2]
    authnz_port = sys.argv[3]

    cookie = open(cookie_file).read().strip()

    # Proxy path (through Apache)
    proxy_urls = {
        "core/hello": f"http://localhost:{authnz_port}/core/hello",
        "ari/all": f"http://localhost:{authnz_port}/ari/all",
        "actual-objects/all": f"http://localhost:{authnz_port}/actual_objects/all",
        "grafana/health": f"http://localhost:{authnz_port}/grafana/api/health",
    }

    # Direct path (bypass Apache, hit containers directly)
    direct_urls = {
        "core/hello": "http://anms-core:5555/core/hello",
        "ari/all": "http://anms-core:5555/ari/all",
        "actual-objects/all": "http://anms-core:5555/actual_objects/all",
        "grafana/health": "http://grafana:3000/api/health",
    }

    results = {}

    print("  --- Through proxy (Apache + Docker network) ---")
    for label, url in proxy_urls.items():
        r = timed_request(url, label, cookie, concurrency=5, n=50)
        results[f"proxy:{label}"] = r
        print(
            f"    proxy:{label}: {r['throughput']} req/s"
            f"  avg={r['avg_ms']}ms  p95={r['p95_ms']}ms  err={r['errors']}"
        )

    print("  --- Direct (bypass Apache, direct container IP) ---")
    for label, url in direct_urls.items():
        r = timed_request(url, label, cookie, concurrency=5, n=50)
        results[f"direct:{label}"] = r
        print(
            f"    direct:{label}: {r['throughput']} req/s"
            f"  avg={r['avg_ms']}ms  p95={r['p95_ms']}ms  err={r['errors']}"
        )

    # Save results
    with open(os.path.join(metrics_dir, "proxy_overhead.json"), "w") as f:
        json.dump(results, f, indent=2)

    # Compute and print overhead
    for ep in ["core/hello", "ari/all", "actual-objects/all", "grafana/health"]:
        proxy = results.get(f"proxy:{ep}", {})
        direct = results.get(f"direct:{ep}", {})
        if proxy and direct:
            direct_avg = max(direct.get("avg_ms", 1), 1)  # avoid div by zero
            overhead_pct = round(
                (proxy.get("avg_ms", 0) - direct.get("avg_ms", 0))
                / direct_avg
                * 100,
                1,
            )
            proxy_tp = proxy.get("throughput", 0)
            direct_tp = max(direct.get("throughput", 1), 0.001)  # avoid div by zero
            print(
                f"\n  OVERHEAD for {ep}:"
                f"\n    Latency overhead: +{overhead_pct}%"
                f" (proxy avg={proxy.get('avg_ms', 0)}ms"
                f" vs direct avg={direct.get('avg_ms', 0)}ms)"
                f"\n    Throughput delta:"
                f" {proxy_tp} vs {direct_tp} req/s"
                f" ({round(100 * (proxy_tp / direct_tp), 1)}% of direct)"
            )


if __name__ == "__main__":
    main()
