#!/usr/bin/env python3
"""Phase D (part 1): Sustained Load Runner.

Runs a 30-second sustained load from multiple endpoints in parallel.
Supports direct mode (no cookies) and authnz mode (with cookies).

Usage:
    python3 stress_sustained_load.py <direct:0|1> <cookie_file_or_empty> <base_port>
"""

import concurrent.futures
import os
import sys
import time
import urllib.error
import urllib.request


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

    urls = [
        f"{base_url}/nm/version",
        f"{base_url}/ari/all",
        f"{base_url}/hello",
        f"{base_url}/agents/all",
        f"{base_url}/report/page",
    ]

    # 30-second sustained load with 50 concurrent workers
    duration = 30
    concurrency = 50
    latencies = []
    start = time.monotonic()
    end = start + duration

    def do_work():
        t0 = time.monotonic()
        try:
            url = urls[hash(time.monotonic()) % len(urls)]
            req = urllib.request.Request(url)
            if session:
                req.add_header("Cookie", session)
            with urllib.request.urlopen(req, timeout=10) as r:
                r.read()
                return time.monotonic() - t0
        except Exception:
            return time.monotonic() - t0

    while time.monotonic() < end:
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
            futures = [ex.submit(do_work) for _ in range(concurrency)]
            for f in concurrent.futures.as_completed(futures):
                latencies.append(f.result())

    total = time.monotonic() - start
    print(f"    {len(latencies)} requests in {round(total, 1)}s")
    print(f"    avg={round(sum(latencies)/len(latencies)*1000, 1)}ms")


if __name__ == "__main__":
    main()
