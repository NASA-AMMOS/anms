#!/usr/bin/env python3
"""Scaling test with Redis caching enabled via proxy on port 5556.

Run from terminal:
    cd /home/greennm1/anms && python3 scripts/stress_scaling_cached.py 1 15
    cd /home/greennm1/anms && python3 scripts/stress_scaling_cached.py 5 15
    etc.
"""

import sys
import time
import concurrent.futures
import urllib.request
import json
import subprocess


# Use port 5556 (Redis cache proxy) instead of 5555 (direct)
API_PORT = 5556

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
    """Make a request through the cache proxy and measure latency."""
    start = time.monotonic()
    try:
        req = urllib.request.Request(f"http://localhost:{API_PORT}{url}", method=method)
        if method == "PUT":
            req.data = b""
            req.add_header("Content-Length", "0")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read()
            latency = time.monotonic() - start
            cache_hit = r.getheader("X-Cache") == "HIT"
            return latency * 1000, cache_hit
    except Exception as e:
        return (time.monotonic() - start) * 1000, False


def run_users(num_users, duration):
    print(f"\n{'='*70}")
    print(f"CACHED TEST: {num_users} CONCURRENT USERS")
    print(f"{'='*70}")
    
    all_latencies = []
    cache_hits = []
    endpoint_stats = {}
    
    def user_work(user_id):
        results = []
        start = time.monotonic()
        end = start + duration
        
        while time.monotonic() < end:
            idx = hash(user_id + len(results)) % len(USER_ENDPOINTS)
            url, method = USER_ENDPOINTS[idx]
            
            latency, hit = timed_request(url, method)
            results.append({
                "url": url,
                "method": method,
                "latency_ms": round(latency, 1),
                "cached": hit,
            })
            all_latencies.append(latency)
            cache_hits.append(1 if hit else 0)
            
            # Think time: 1-3 seconds
            time.sleep(1 + (hash(user_id) % 2))
        
        return results
    
    print(f"  Starting {num_users} user sessions for {duration}s...")
    start = time.monotonic()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(user_work, i) for i in range(num_users)]
        for f in concurrent.futures.as_completed(futures):
            results = f.result()
            for r in results:
                key = f"{r['method']} {r['url']}"
                if key not in endpoint_stats:
                    endpoint_stats[key] = {"latencies": [], "hits": 0, "misses": 0}
                endpoint_stats[key]["latencies"].append(r["latency_ms"])
                if r["cached"]:
                    endpoint_stats[key]["hits"] += 1
                else:
                    endpoint_stats[key]["misses"] += 1
    
    elapsed = time.monotonic() - start
    
    # Results
    total_reqs = len(all_latencies)
    total_hits = sum(cache_hits)
    hit_rate = total_hits / max(total_reqs, 1) * 100
    
    print(f"\nResults:")
    print(f"  Duration: {elapsed:.1f}s")
    print(f"  Total requests: {total_reqs}")
    print(f"  Throughput: {total_reqs/elapsed:.2f} req/s")
    print(f"  Cache hit rate: {hit_rate:.1f}% ({total_hits}/{total_reqs})")
    
    # Latency stats
    avg_lat = 0
    p50_lat = 0
    p95_lat = 0
    p99_lat = 0
    max_lat = 0
    
    if all_latencies:
        sorted_lat = sorted(all_latencies)
        n = len(sorted_lat)
        avg_lat = sum(all_latencies) / n
        p50_lat = sorted_lat[int(n*0.5)]
        p95_lat = sorted_lat[int(n*0.95)]
        p99_lat = sorted_lat[min(int(n*0.99), n-1)]
        max_lat = max(sorted_lat)
        
        print(f"\n  Latency (all endpoints):")
        print(f"    Avg: {avg_lat:.0f}ms")
        print(f"    p50: {p50_lat:.0f}ms")
        print(f"    p95: {p95_lat:.0f}ms")
        print(f"    p99: {p99_lat:.0f}ms")
        print(f"    Max: {max_lat:.0f}ms")
    
    print(f"\n  Per-endpoint performance:")
    for key in sorted(endpoint_stats.keys()):
        stats = endpoint_stats[key]
        lats = stats["latencies"]
        ep_n = len(lats)
        if ep_n > 0:
            ep_avg = sum(lats) / ep_n
            sorted_l = sorted(lats)
            p95 = sorted_l[int(ep_n * 0.95)] if ep_n > 1 else lats[0]
            hits = stats["hits"]
            misses = stats["misses"]
            print(f"    {key:30s} n={ep_n:3d} avg={ep_avg:6.0f}ms p95={p95:6.0f}ms  hits={hits} misses={misses}")
    
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
    result_file = f"/tmp/scaling-cached-{num_users}users.json"
    result_data = {
        "num_users": num_users,
        "duration_s": round(elapsed, 2),
        "total_requests": total_reqs,
        "throughput_rps": round(total_reqs / elapsed, 2),
        "cache_hit_rate_pct": round(hit_rate, 1),
        "cache_hits": total_hits,
        "latency_avg_ms": round(avg_lat, 1),
        "latency_p50_ms": round(p50_lat, 1),
        "latency_p95_ms": round(p95_lat, 1),
        "latency_p99_ms": round(p99_lat, 1),
        "endpoint_stats": {k: {
            "count": len(v["latencies"]),
            "avg_ms": round(sum(v["latencies"]) / len(v["latencies"]), 1) if v["latencies"] else 0,
            "hits": v["hits"],
            "misses": v["misses"],
        } for k, v in endpoint_stats.items()}
    }
    
    with open(result_file, 'w') as f:
        json.dump(result_data, f, indent=2)
    
    print(f"\n  Saved to {result_file}")
    
    return {
        "num_users": num_users,
        "throughput_rps": round(total_reqs / elapsed, 2),
        "cache_hit_rate_pct": round(hit_rate, 1),
        "avg_latency_ms": round(avg_lat, 1),
        "p95_latency_ms": round(p95_lat, 1),
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <num_users> <duration_seconds>")
        print("Example: python3 stress_scaling_cached.py 5 15")
        sys.exit(1)
    
    num_users = int(sys.argv[1])
    duration = int(sys.argv[2])
    
    result = run_users(num_users, duration)
    print(f"\n  Final: {result['throughput_rps']} req/s, p95={result['p95_latency_ms']}ms, hit_rate={result['cache_hit_rate_pct']}%")
