#!/usr/bin/env python3
"""Quick scaling test - run from 1 to N users.

Run from terminal:
    cd /home/greennm1/anms && python3 scripts/stress_scaling_quick.py 1 15
    cd /home/greennm1/anms && python3 scripts/stress_scaling_quick.py 5 15
    cd /home/greennm1/anms && python3 scripts/stress_scaling_quick.py 10 15
    etc.
"""

import sys
import time
import concurrent.futures
import urllib.request
import urllib.error
import json
import subprocess
import os


USER_ENDPOINTS = [
    ("/hello", "GET"),
    ("/agents/all", "GET"),
    ("/ari/all", "GET"),
    ("/ari/all/display", "GET"),
    ("/sys_status/services", "GET"),
    ("/nm/version", "GET"),
    ("/report/page", "GET"),
    ("/report/all", "GET"),
    ("/alerts/acknowledge/1", "PUT"),
]


def timed_request(url, method="GET", timeout=30):
    start = time.monotonic()
    try:
        req = urllib.request.Request(f"http://localhost:5555{url}", method=method)
        if method == "PUT":
            req.data = b""
            req.add_header("Content-Length", "0")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read()
            return time.monotonic() - start
    except Exception:
        return time.monotonic() - start


def run_users(num_users, duration):
    print(f"\n{'='*70}")
    print(f"TEST: {num_users} CONCURRENT USERS")
    print(f"{'='*70}")
    
    all_latencies = []
    endpoint_latencies = {}
    
    def user_work(user_id):
        results = []
        start = time.monotonic()
        end = start + duration
        
        while time.monotonic() < end:
            idx = hash(user_id + len(results)) % len(USER_ENDPOINTS)
            url, method = USER_ENDPOINTS[idx]
            
            latency = timed_request(url, method)
            results.append({
                "url": url,
                "method": method,
                "latency_ms": round(latency * 1000, 1),
            })
            
            # Think time: 1-3 seconds
            time.sleep(1 + (hash(user_id) % 2))
        
        return results
    
    print(f"  Starting {num_users} user sessions for {duration}s...")
    start = time.monotonic()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(user_work, i) for i in range(num_users)]
        for f in concurrent.futures.as_completed(futures):
            results = f.result()
            all_latencies.extend([r["latency_ms"] for r in results])
            for r in results:
                key = f"{r['method']} {r['url']}"
                if key not in endpoint_latencies:
                    endpoint_latencies[key] = []
                endpoint_latencies[key].append(r["latency_ms"])
    
    elapsed = time.monotonic() - start
    
    # Results
    total_reqs = len(all_latencies)
    print(f"\nResults:")
    print(f"  Duration: {elapsed:.1f}s")
    print(f"  Total requests: {total_reqs}")
    print(f"  Throughput: {total_reqs/elapsed:.2f} req/s")
    
    if all_latencies:
        sorted_lat = sorted(all_latencies)
        n = len(sorted_lat)
        avg = sum(all_latencies) / n
        print(f"\n  Latency (all endpoints):")
        print(f"    Avg: {avg:.0f}ms")
        print(f"    p50: {sorted_lat[int(n*0.5)]}ms")
        print(f"    p95: {sorted_lat[int(n*0.95)]}ms")
        print(f"    p99: {sorted_lat[min(int(n*0.99), n-1)]}ms")
        print(f"    Max: {max(sorted_lat)}ms")
    else:
        sorted_lat = []
        n = 0
        avg = 0
    
    print(f"\n  Per-endpoint performance:")
    for key in sorted(endpoint_latencies.keys()):
        lats = endpoint_latencies[key]
        ep_n = len(lats)
        ep_avg = sum(lats) / ep_n if ep_n > 0 else 0
        sorted_l = sorted(lats)
        p95 = sorted_l[int(ep_n * 0.95)] if ep_n > 1 else lats[0] if lats else 0
        print(f"    {key:30s} n={ep_n:3d} avg={ep_avg:6.0f}ms p95={p95:6.0f}ms")
    
    # Container stats
    print(f"\n  Container stats (avg CPU%):")
    r = subprocess.run(
        ["docker", "stats", "--no-stream", "--format", "{{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}"],
        capture_output=True, text=True, timeout=10
    )
    for line in r.stdout.strip().split('\n')[1:]:
        parts = line.split('\t')
        if len(parts) >= 3 and float(parts[1].rstrip('%')) > 0.5:
            print(f"    {parts[0]:30s} CPU={parts[1].strip():>6s} MEM={parts[2].strip():>6s}")
    
    # Save to file
    result_file = f"/tmp/scaling-{num_users}users.json"
    with open(result_file, 'w') as f:
        json.dump({
            "num_users": num_users,
            "duration_s": round(elapsed, 2),
            "total_requests": total_reqs,
            "throughput_rps": round(total_reqs / elapsed, 2),
            "latency_avg_ms": round(avg, 1) if all_latencies else 0,
            "latency_p50_ms": sorted_lat[int(n * 0.5)] if all_latencies else 0,
            "latency_p95_ms": sorted_lat[int(n * 0.95)] if all_latencies else 0,
            "latency_p99_ms": sorted_lat[min(int(n * 0.99), n - 1)] if all_latencies else 0,
        }, f, indent=2)
    
    print(f"\n  Saved to {result_file}")
    
    return {
        "num_users": num_users,
        "throughput_rps": round(total_reqs / elapsed, 2),
        "avg_latency_ms": round(avg, 1) if all_latencies else 0,
        "p95_latency_ms": sorted_lat[int(n * 0.95)] if all_latencies else 0,
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <num_users> <duration_seconds>")
        print("Example: python3 stress_scaling_quick.py 5 15")
        sys.exit(1)
    
    num_users = int(sys.argv[1])
    duration = int(sys.argv[2])
    
    result = run_users(num_users, duration)
    print(f"\n  Final: {result['throughput_rps']} req/s, p95={result['p95_latency_ms']}ms")
