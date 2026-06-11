#!/usr/bin/env python3
"""Phase D (part 1): Sustained Load Runner.

Runs a 30-second sustained load from multiple endpoints in parallel.
Meant to be run in the background while container stats are collected.

Usage:
    python3 stress_sustained_load.py <cookie_file> <authnz_port>
"""

import concurrent.futures
import statistics
import sys
import time
import urllib.request

URLS = [
    "http://localhost:{}/core/hello".format,
    "http://localhost:{}/ari/all".format,
    "http://localhost:{}/actual_objects/all".format,
    "http://localhost:{}/grafana/api/health".format,
]


def main():
    cookie_file = sys.argv[1]
    authnz_port = sys.argv[2]
    cookie = open(cookie_file).read().strip()
    duration = 30

    all_lats = []
    start = time.monotonic()
    idx = 0
    while time.monotonic() - start < duration:
        url = URLS[idx % len(URLS)](authnz_port)
        idx += 1
        t0 = time.monotonic()
        try:
            req = urllib.request.Request(url)
            req.add_header("Cookie", cookie)
            with urllib.request.urlopen(req, timeout=10) as r:
                r.read()
            all_lats.append(time.monotonic() - t0)
        except Exception:
            all_lats.append(999)

    # Safe mean: log 0 if list is empty
    avg_ms = round(sum(all_lats) / len(all_lats) * 1000, 1) if all_lats else 0
    print(
        f"done: {len(all_lats)} reqs in {duration}s,"
        f" avg={avg_ms}ms"
    )


if __name__ == "__main__":
    main()
