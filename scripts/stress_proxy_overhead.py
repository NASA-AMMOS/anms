#!/usr/bin/env python3
"""Phase A: Proxy/Direct Overhead Measurement.

Measures round-trip latency through authnz proxy vs direct API.
In direct mode (DIRECT=1), measures baseline API latency without authnz.
In authnz mode, measures proxy overhead via concurrent vs sequential comparison.

Usage:
    python3 stress_proxy_overhead.py <direct:0|1> <cookie_file_or_empty> <metrics_dir> <base_port>
"""

import concurrent.futures
import json
import os
import sys
import time
import urllib.error
import urllib.request

from stress_utils import safe_throughput, compute_percentiles


def timed_request(url, session=None, concurrency=5, n=50):
    """Time a batch of requests and return structured results."""
    latencies = []
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
        "label": "",
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

    session = ""
    if direct == 0:
        session = parse_cookie_file(cookie_file)
        if not session:
            print("ERROR: Could not extract session cookie from file", file=sys.stderr)
            sys.exit(1)
        mode_str = "proxy"
    else:
        mode_str = "direct"

    # Endpoints to measure
    urls = {
        "nm/version": f"http://localhost:{base_port}/nm/version",
        "ari/all": f"http://localhost:{base_port}/ari/all",
        "hello": f"http://localhost:{base_port}/hello",
        "agents": f"http://localhost:{base_port}/agents/all",
    }

    # Grafana only in authnz mode (direct mode doesn't have it on this port)
    if direct == 0:
        urls["grafana/health"] = f"http://localhost:{base_port}/grafana/api/health"

    results = {}

    label_prefix = f"{mode_str}"
    print(f"  Mode: {mode_str} ({base_port})")
    print(f"  --- Sequential (1 concurrent request) ---")
    for label, url in urls.items():
        r = timed_request(url, session, concurrency=1, n=50)
        r["label"] = f"{label_prefix}:{label}"
        results[f"{label_prefix}:{label}"] = r
        print(
            f"    {label_prefix}:{label}: {r['throughput']} req/s"
            f"  avg={r['avg_ms']}ms  p95={r['p95_ms']}ms  err={r['errors']}"
        )

    # Concurrent (5 at a time) — measures overhead
    print(f"  --- Concurrent (5 concurrent requests) ---")
    for label, url in urls.items():
        r = timed_request(url, session, concurrency=5, n=50)
        r["label"] = f"{label_prefix}c:{label}"
        results[f"{label_prefix}c:{label}"] = r
        print(
            f"    {label_prefix}c:{label}: {r['throughput']} req/s"
            f"  avg={r['avg_ms']}ms  p95={r['p95_ms']}ms  err={r['errors']}"
        )

    # Save results
    with open(os.path.join(metrics_dir, "proxy_overhead.json"), "w") as f:
        json.dump(results, f, indent=2)

    # Compute overhead (concurrent vs sequential ratio)
    for ep in ["nm/version", "ari/all", "hello", "agents"] + (["grafana/health"] if direct == 0 else []):
        if direct == 0 and ep == "grafana/health":
            pass  # included in authnz mode
        elif ep not in urls:
            continue
        seq = results.get(f"{label_prefix}:{ep}", {})
        conc = results.get(f"{label_prefix}c:{ep}", {})
        if seq and conc:
            seq_avg = max(seq.get("avg_ms", 1), 1)
            conc_avg = conc.get("avg_ms", 0)
            overhead_pct = round(
                (conc_avg - seq_avg) / seq_avg * 100, 1
            )
            seq_tp = seq.get("throughput", 0)
            conc_tp = max(conc.get("throughput", 1), 0.001)
            print(
                f"\n  OVERHEAD for {ep} ({mode_str} mode):"
                f"\n    Latency: +{overhead_pct}%"
                f" (seq avg={seq_avg}ms vs conc avg={conc_avg}ms)"
                f"\n    Throughput: {seq_tp} vs {conc_tp} req/s"
                f" ({round(100 * (conc_tp / seq_tp), 1)}% of seq)"
            )


if __name__ == "__main__":
    main()
