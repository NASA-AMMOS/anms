#!/usr/bin/env python3
"""Scaling Test - Find the breaking point.

Tests 1-100 concurrent users in increments to find:
- Where throughput saturates
- Where error rates spike
- Where latency becomes unacceptable

Usage:
    python3 stress_scaling_test.py [--test-caching] [--no-caching]
"""

import concurrent.futures
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request


USER_ENDPOINTS = [
    {"name": "hello", "url": "/hello", "method": "GET", "weight": 5},
    {"name": "agents", "url": "/agents/all", "method": "GET", "weight": 3},
    {"name": "ari_all", "url": "/ari/all", "method": "GET", "weight": 3},
    {"name": "ari_display", "url": "/ari/all/display", "method": "GET", "weight": 2},
    {"name": "sys_status", "url": "/sys_status/services", "method": "GET", "weight": 2},
    {"name": "version", "url": "/nm/version", "method": "GET", "weight": 1},
    {"name": "report_page", "url": "/report/page", "method": "GET", "weight": 1},
    {"name": "report_all", "url": "/report/all", "method": "GET", "weight": 1},
    {"name": "alerts", "url": "/alerts/acknowledge/1", "method": "PUT", "weight": 1},
]


def get_weighted_url():
    """Select URL based on typical user behavior weights."""
    total_weight = sum(ep["weight"] for ep in USER_ENDPOINTS)
    r = hash(time.monotonic()) % total_weight
    cumulative = 0
    for ep in USER_ENDPOINTS:
        cumulative += ep["weight"]
        if r < cumulative:
            return ep
    return USER_ENDPOINTS[-1]


def timed_request(url, method="GET", timeout=30):
    """Make a single request and measure latency."""
    start = time.monotonic()
    try:
        req = urllib.request.Request(f"http://localhost:5555{url}", method=method)
        if method == "PUT":
            req.data = b""
            req.add_header("Content-Length", "0")
        
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read()
            latency = time.monotonic() - start
            return {
                "status": r.status,
                "latency_ms": round(latency * 1000, 1),
                "error": None
            }
    except Exception as e:
        latency = time.monotonic() - start
        return {
            "status": 0,
            "latency_ms": round(latency * 1000, 1),
            "error": str(type(e).__name__)
        }


def user_session(user_id, duration):
    """Simulate a single user session with realistic behavior."""
    results = []
    start = time.monotonic()
    end = start + duration
    
    while time.monotonic() < end:
        ep = get_weighted_url()
        result = timed_request(ep["url"], ep["method"])
        result["endpoint"] = ep["name"]
        results.append(result)
        
        # Realistic thinking time between requests (1-3 seconds)
        think_time = 1.0 + (hash(user_id) % 2)
        time.sleep(think_time)
    
    return results


def collect_container_stats(duration, interval=2):
    """Collect per-container CPU/memory during test."""
    samples = int(duration / interval)
    stats = {}
    
    for _ in range(samples):
        r = subprocess.run(
            ["docker", "stats", "--no-stream", "--format",
             "{{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}"],
            capture_output=True, text=True, timeout=10
        )
        
        for line in r.stdout.strip().split('\n')[1:]:
            parts = line.split('\t')
            if len(parts) >= 3:
                name = parts[0]
                cpu = float(parts[1].rstrip('%'))
                mem = float(parts[2].rstrip('%'))
                
                if name not in stats:
                    stats[name] = {"cpu": [], "mem": []}
                stats[name]["cpu"].append(cpu)
                stats[name]["mem"].append(mem)
        
        if _ < samples - 1:
            time.sleep(interval)
    
    # Average
    for name in stats:
        stats[name]["avg_cpu"] = round(sum(stats[name]["cpu"]) / len(stats[name]["cpu"]), 1)
        stats[name]["avg_mem"] = round(sum(stats[name]["mem"]) / len(stats[name]["mem"]), 1)
    
    return stats


def run_scaling_test(num_users, duration=15, test_caching=False):
    """Run full scaling test with given user count."""
    print(f"\n{'='*70}")
    print(f"TEST: {num_users} CONCURRENT USERS")
    if test_caching:
        print("MODE: WITH REDIS CACHING ENABLED")
        # Enable caching via redis-cli
        subprocess.run(["docker", "exec", "anms-redis-1", "flushdb"], 
                      capture_output=True, timeout=10)
    else:
        print("MODE: WITHOUT CACHING (baseline)")
    print(f"{'='*70}")
    
    # Start stats collection
    print(f"  Starting {num_users} user sessions...")
    start = time.monotonic()
    
    all_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(user_session, i, duration) for i in range(num_users)]
        for f in concurrent.futures.as_completed(futures):
            all_results.extend(f.result())
    
    elapsed = time.monotonic() - start
    
    # Collect container stats during test
    print(f"  Collecting container stats...")
    container_stats = collect_container_stats(elapsed)
    
    # Analyze results
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    
    # Overall metrics
    total_requests = len(all_results)
    successful = sum(1 for r in all_results if r["error"] is None)
    errors = sum(1 for r in all_results if r["error"] is not None)
    latencies = [r["latency_ms"] for r in all_results if r["error"] is None]
    
    print(f"\nOverall:")
    print(f"  Duration: {elapsed:.1f}s")
    print(f"  Total requests: {total_requests}")
    print(f"  Throughput: {total_requests/elapsed:.2f} req/s")
    print(f"  Success rate: {successful/total_requests*100:.1f}%")
    print(f"  Errors: {errors}")
    
    if latencies:
        latencies_sorted = sorted(latencies)
        n = len(latencies_sorted)
        avg = sum(latencies) / n
        p50 = latencies_sorted[int(n * 0.5)]
        p95 = latencies_sorted[int(n * 0.95)]
        p99 = latencies_sorted[min(int(n * 0.99), n - 1)]
        mx = max(latencies)
        print(f"\nLatency distribution:")
        print(f"  Avg: {avg:.1f}ms")
        print(f"  p50: {p50}ms")
        print(f"  p95: {p95}ms")
        print(f"  p99: {p99}ms")
        print(f"  Max: {mx}ms")
    else:
        avg = 0
        p50 = 0
        p95 = 0
        p99 = 0
        mx = 0
        print(f"\nNo successful requests!")
    
    # Per-endpoint breakdown
    by_endpoint = {}
    for r in all_results:
        ep = r["endpoint"]
        if ep not in by_endpoint:
            by_endpoint[ep] = []
        by_endpoint[ep].append(r)
    
    print(f"\nPer-Endpoint Performance:")
    print(f"{'Endpoint':20s} {'Requests':>10} {'Success%':>10} {'Avg(ms)':>10} {'p95(ms)':>10} {'Errors':>8}")
    print("-" * 70)
    
    for ep in sorted(by_endpoint.keys()):
        ep_results = by_endpoint[ep]
        ep_successful = sum(1 for r in ep_results if r["error"] is None)
        ep_errors = len(ep_results) - ep_successful
        
        ep_latencies = [r["latency_ms"] for r in ep_results if r["error"] is None]
        if ep_latencies:
            ep_latencies_sorted = sorted(ep_latencies)
            n = len(ep_latencies_sorted)
            avg = sum(ep_latencies)/n
            p95 = ep_latencies_sorted[int(n*0.95)] if n > 1 else ep_latencies_sorted[0]
            success_pct = ep_successful/len(ep_results)*100
        else:
            avg = 0
            p95 = 0
            success_pct = 0
        
        print(f"{ep:20s} {len(ep_results):>10} {success_pct:>9.1f}% {avg:>10.1f} {p95:>10.1f} {ep_errors:>8}")
    
    # Container resource usage
    print(f"\nContainer Resource Usage (avg during test):")
    print(f"{'Container':30s} {'Avg CPU%':>10} {'Avg Mem%':>10}")
    print("-" * 55)
    
    for name, stats in sorted(container_stats.items(), key=lambda x: x[1]["avg_cpu"], reverse=True):
        if stats["avg_cpu"] > 0.1 or stats["avg_mem"] > 0.1:
            print(f"{name:30s} {stats['avg_cpu']:>10.1f} {stats['avg_mem']:>10.1f}")
    
    # Check if system is degraded
    print(f"\nSystem Health:")
    if errors > 0:
        print(f"  ⚠️  {errors} errors detected")
    
    if latencies and max(latencies) > 10000:
        print(f"  ⚠️  Request timeout (>10s)")
    
    # Save results
    result_file = f"/tmp/stress-scaling-{num_users}users-caching={int(test_caching)}.json"
    result_data = {
        "num_users": num_users,
        "duration_seconds": round(elapsed, 2),
        "total_requests": total_requests,
        "throughput_rps": round(total_requests/elapsed, 2),
        "error_count": errors,
        "success_rate_pct": round(successful/total_requests*100, 1),
        "latency": {
            "avg_ms": round(sum(latencies)/n, 1) if latencies else 0,
            "p50_ms": latencies_sorted[int(n*0.5)] if latencies else 0,
            "p95_ms": latencies_sorted[int(n*0.95)] if latencies else 0,
            "p99_ms": latencies_sorted[min(int(n*0.99), n-1)] if latencies else 0,
            "max_ms": max(latencies) if latencies else 0
        },
        "by_endpoint": {ep: {
            "total": len(r),
            "errors": len(r) - sum(1 for x in r if x["error"] is None),
            "avg_ms": round(sum(x["latency_ms"] for x in r if x["error"] is None)/
                          max(sum(1 for x in r if x["error"] is None), 1), 1),
        } for ep, r in by_endpoint.items()},
        "container_stats": {name: {
            "avg_cpu": s["avg_cpu"],
            "avg_mem": s["avg_mem"]
        } for name, s in container_stats.items()}
    }
    
    with open(result_file, 'w') as f:
        json.dump(result_data, f, indent=2)
    
    print(f"\nResults saved to {result_file}")
    
    return result_data


def main():
    parser = {
        "num_users": [1, 2, 5, 10, 15, 20, 30, 50, 100],
        "duration": 15
    }
    
    print("=" * 70)
    print("SCALING TEST - Find the breaking point")
    print("=" * 70)
    print("\nThis test will run with increasing user counts to find")
    print("where performance degrades significantly.\n")
    print("Config:")
    for key, value in parser.items():
        print(f"  {key}: {value}")
    print()
    
    # Ask user to confirm
    print("WARNING: This test will stress the system heavily.")
    print("Press Enter to start, or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        sys.exit(0)
    
    # Run tests without caching
    print("\n\n" + "=" * 70)
    print("PHASE 1: BASELINE (WITHOUT CACHING)")
    print("=" * 70)
    
    baseline_results = {}
    for num_users in parser["num_users"]:
        try:
            result = run_scaling_test(num_users, parser["duration"], test_caching=False)
            baseline_results[num_users] = result
        except Exception as e:
            print(f"\nERROR at {num_users} users: {e}")
            break
    
    # Run tests with caching
    print("\n\n" + "=" * 70)
    print("PHASE 2: WITH REDIS CACHING")
    print("=" * 70)
    
    print("\nEnabling Redis caching...")
    # Enable caching in anms-core
    subprocess.run(["docker", "exec", "anms-core-1", "env"], capture_output=True)
    print("Note: To enable caching, set ANMS_USE_REDIS_CACHE=1 in docker-compose-test.yml")
    print("Then restart: docker compose -f docker-compose-test.yml up -d anms-core")
    print()
    print("If caching is NOT enabled, Phase 2 will run with same baseline.\n")
    
    enable_caching = input("Is Redis caching enabled? (y/n): ").lower() == 'y'
    
    if enable_caching:
        # Flush cache
        subprocess.run(["docker", "exec", "anms-redis-1", "flushdb"], 
                      capture_output=True, timeout=10)
        
        for num_users in parser["num_users"]:
            try:
                result = run_scaling_test(num_users, parser["duration"], test_caching=True)
                baseline_results[(num_users, "cached")] = result
            except Exception as e:
                print(f"\nERROR at {num_users} users: {e}")
                break
    
    # Generate comparison
    print("\n\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)
    
    print("\n{'Users':>8} {'Baseline RPS':>15} {'Cached RPS':>15} {'Improvement':>15}")
    print("-" * 55)
    
    for num_users in parser["num_users"]:
        baseline = baseline_results.get(num_users)
        cached = baseline_results.get((num_users, "cached"))
        
        if baseline:
            b_rps = baseline["throughput_rps"]
            if cached:
                c_rps = cached["throughput_rps"]
                improvement = (c_rps - b_rps) / b_rps * 100
                print(f"{num_users:>8} {b_rps:>15.2f} {c_rps:>15.2f} {improvement:>+14.1f}%")
            else:
                print(f"{num_users:>8} {b_rps:>15.2f} {'N/A':>15} {'N/A':>15}")
        else:
            print(f"{num_users:>8} {'ERROR':>15} {'N/A':>15} {'N/A':>15}")
    
    print("\nAll results saved in /tmp/stress-scaling-*.json")


if __name__ == "__main__":
    main()
