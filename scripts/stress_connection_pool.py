#!/usr/bin/env python3
"""Phase E: DB Connection Pool Saturation.

Fires concurrent requests at increasing concurrency levels and measures
error rates and latency degradation.

Usage:
    python3 stress_connection_pool.py <cookie_file> <authnz_port>
"""

import concurrent.futures
import statistics
import sys
import time
import urllib.error
import urllib.request

from stress_utils import safe_throughput


def make_request(cookie):
    """Fire a single /ari/all request, return (latency, failed, code)."""
    url = "http://localhost:8084/ari/all"  # overridden by --authnz-port
    t0 = time.monotonic()
    try:
        req = urllib.request.Request(url)
        req.add_header("Cookie", cookie)
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()
        return (time.monotonic() - t0, False)
    except urllib.error.HTTPError as e:
        return (time.monotonic() - t0, True, e.code)
    except Exception:
        return (time.monotonic() - t0, True, 0)


def main():
    cookie_file = sys.argv[1]
    authnz_port = sys.argv[2]

    # Patch the URL function to use the given port
    global make_request
    orig_cookie = sys.argv[1]

    def make_ported_request():
        url = f"http://localhost:{authnz_port}/ari/all"
        t0 = time.monotonic()
        try:
            req = urllib.request.Request(url)
            req.add_header("Cookie", orig_cookie)
            with urllib.request.urlopen(req, timeout=10) as r:
                r.read()
            return (time.monotonic() - t0, False)
        except urllib.error.HTTPError as e:
            return (time.monotonic() - t0, True, e.code)
        except Exception:
            return (time.monotonic() - t0, True, 0)

    cookie = open(orig_cookie).read().strip()

    for conc_val in [10, 50, 100, 150, 200]:
        latencies = []
        errors = 0
        start = time.monotonic()

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=conc_val
        ) as ex:
            futures = [
                ex.submit(make_ported_request) for _ in range(conc_val)
            ]
            for f in concurrent.futures.as_completed(futures):
                result = f.result()
                d, *rest = result
                latencies.append(d)
                if rest and rest[0]:
                    errors += 1

        elapsed = time.monotonic() - start
        success = conc_val - errors
        s = sorted(latencies)

        if s:
            avg_ms = round(sum(s) / len(s) * 1000, 0)
            p95_idx = min(int(len(s) * 0.95), len(s) - 1)
            p95_ms = round(s[p95_idx] * 1000, 0)
            p99_idx = min(int(len(s) * 0.99), len(s) - 1)
            p99_ms = round(s[p99_idx] * 1000, 0)
        else:
            avg_ms = p95_ms = p99_ms = 0

        tp = safe_throughput(success, elapsed)
        print(
            f"  conc={conc_val:3d}:"
            f" {success}/{conc_val} ok,"
            f" throughput={tp} req/s,"
            f" avg={avg_ms}ms,"
            f" p95={p95_ms}ms,"
            f" p99={p99_ms}ms,"
            f" errors={errors}"
        )


if __name__ == "__main__":
    main()
