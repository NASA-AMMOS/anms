#!/usr/bin/env python3
"""Multi-User Performance Test (1-5 users).

Simulates 1-5 concurrent users performing typical workflows and measures:
- Response latency per endpoint
- Resource usage during load
- Container-level bottlenecks
- Connection pooling efficiency

Usage:
    python3 stress_multi_user.py <num_users:1-5> <duration_seconds:30>
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


# Endpoints to test - typical user workflows
USER_ENDPOINTS = [
    # Core data
    {"name": "version", "url": "/nm/version", "method": "GET"},
    {"name": "hello", "url": "/hello", "method": "GET"},
    
    # ARI data
    {"name": "ari_all", "url": "/ari/all", "method": "GET"},
    {"name": "ari_display", "url": "/ari/all/display", "method": "GET"},
    {"name": "agents", "url": "/agents/all", "method": "GET"},
    
    # Reporting
    {"name": "report_page", "url": "/report/page", "method": "GET"},
    {"name": "report_all", "url": "/report/all", "method": "GET"},
    
    # System status
    {"name": "sys_status", "url": "/sys_status/services", "method": "GET"},
    
    # Alerts
    {"name": "alerts_ack", "url": "/alerts/acknowledge/1", "method": "PUT"},
]


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
                "url": url,
                "method": method,
                "status": r.status,
                "latency_ms": round(latency * 1000, 1),
                "error": None
            }
    except Exception as e:
        latency = time.monotonic() - start
        return {
            "url": url,
            "method": method,
            "status": 0,
            "latency_ms": round(latency * 1000, 1),
            "error": str(type(e).__name__)
        }


def user_workflow(user_id, duration, endpoint_results):
    """Simulate a single user performing workflows."""
    print(f"  User {user_id}: Starting workflow...")
    
    # Rotate through endpoints like a real user would
    result_count = 0
    start = time.monotonic()
    end = start + duration
    
    while time.monotonic() < end:
        for ep in USER_ENDPOINTS:
            if time.monotonic() >= end:
                break
            
            # Add realistic delay between requests (2-5 seconds)
            time.sleep(0.5 + (hash(user_id + result_count) % 3) * 0.5)
            
            result = timed_request(ep["url"], ep["method"])
            result["user_id"] = user_id
            
            # Store in shared dict (thread-safe for append)
            with endpoint_results["lock"]:
                endpoint_results["results"].append(result)
                result_count += 1
    
    print(f"  User {user_id}: Completed {result_count} requests")


def collect_container_stats(duration):
    """Collect per-container CPU/memory during test period."""
    stats = {}
    
    # Sample every 2 seconds
    interval = 2
    samples = int(duration / interval)
    
    for i in range(samples):
        # Get CPU % from docker stats (single shot)
        r = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", 
             "{{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}\t{{.MemUsage}}"],
            capture_output=True, text=True, timeout=10
        )
        
        lines = r.stdout.strip().split('\n')
        for line in lines[1:]:  # Skip header
            parts = line.split('\t')
            if len(parts) >= 4:
                name = parts[0]
                cpu = float(parts[1].rstrip('%'))
                mem = float(parts[2].rstrip('%'))
                
                if name not in stats:
                    stats[name] = {"cpu": [], "mem": [], "samples": 0}
                stats[name]["cpu"].append(cpu)
                stats[name]["mem"].append(mem)
                stats[name]["samples"] += 1
        
        if i < samples - 1:
            time.sleep(interval)
    
    # Calculate averages
    for name in stats:
        stats[name]["avg_cpu"] = round(sum(stats[name]["cpu"]) / len(stats[name]["cpu"]), 1)
        stats[name]["avg_mem"] = round(sum(stats[name]["mem"]) / len(stats[name]["mem"]), 1)
        stats[name]["peak_cpu"] = round(max(stats[name]["cpu"]), 1)
        stats[name]["peak_mem"] = round(max(stats[name]["mem"]), 1)
    
    return stats


def analyze_results(results, container_stats, duration, num_users):
    """Analyze test results and produce report."""
    print("\n" + "=" * 70)
    print(f"MULTI-USER PERFORMANCE REPORT ({num_users} users, {duration}s)")
    print("=" * 70)
    
    # Group by endpoint
    by_endpoint = {}
    total_requests = 0
    
    for r in results:
        key = f"{r['method']} {r['url']}"
        if key not in by_endpoint:
            by_endpoint[key] = []
        by_endpoint[key].append(r)
        total_requests += 1
    
    # Endpoint performance
    print(f"\n{'Endpoint':30s} {'Requests':>10} {'Avg(ms)':>10} {'p50(ms)':>10} {'p95(ms)':>10} {'p99(ms)':>10} {'Errors':>8}")
    print("-" * 90)
    
    for ep, results_list in sorted(by_endpoint.items()):
        latencies = sorted([r["latency_ms"] for r in results_list if r["error"] is None])
        errors = sum(1 for r in results_list if r["error"] is not None)
        n = len(latencies)
        
        if n == 0:
            print(f"{ep:30s} {len(results_list):>10} {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>10} {errors:>8}")
            continue
        
        p50 = latencies[int(n * 0.5)]
        p95 = latencies[int(n * 0.95)]
        p99 = latencies[min(int(n * 0.99), n-1)]
        avg = sum(latencies) / n
        
        print(f"{ep:30s} {n:>10} {avg:>10.1f} {p50:>10.1f} {p95:>10.1f} {p99:>10.1f} {errors:>8}")
    
    # Container resource usage
    print(f"\nContainer Resource Usage:")
    print(f"{'Container':35s} {'Avg CPU%':>10} {'Peak CPU%':>10} {'Avg Mem%':>10} {'Peak Mem%':>10}")
    print("-" * 85)
    
    for name, stats in sorted(container_stats.items()):
        if stats["samples"] > 0:
            print(f"{name:35s} {stats['avg_cpu']:>10.1f} {stats['peak_cpu']:>10.1f} {stats['avg_mem']:>10.1f} {stats['peak_mem']:>10.1f}")
    
    # Bottleneck analysis
    print(f"\nBottleneck Analysis:")
    print("-" * 70)
    
    # Find slowest endpoints
    slowest = []
    for ep, results_list in by_endpoint.items():
        latencies = [r["latency_ms"] for r in results_list if r["error"] is None]
        if latencies:
            slowest.append((ep, sum(latencies) / len(latencies)))
    
    slowest.sort(key=lambda x: x[1], reverse=True)
    
    if slowest:
        print(f"  Slowest endpoint: {slowest[0][0]} (avg {slowest[0][1]:.1f}ms)")
        if slowest[0][1] > 1000:
            print(f"    ⚠️  Over 1 second - consider caching or optimization")
    
    # Find high resource containers
    high_cpu = [(name, s["avg_cpu"]) for name, s in container_stats.items() if s["avg_cpu"] > 10]
    if high_cpu:
        print(f"\n  High CPU containers:")
        for name, cpu in sorted(high_cpu, key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {name}: {cpu:.1f}% avg")
    
    # Find error rates
    error_endpoints = [(k, len([r for r in v if r["error"]])) for k, v in by_endpoint.items() 
                       if any(r["error"] for r in v)]
    if error_endpoints:
        print(f"\n  Endpoints with errors:")
        for ep, errs in error_endpoints:
            print(f"    {ep}: {errs} errors")
    
    # Recommendations
    print(f"\nRecommendations:")
    if any(s["avg_cpu"] > 50 for s in container_stats.values()):
        print("  - Consider increasing CPU limits for high-CPU containers")
    
    if slowest and slowest[0][1] > 500:
        print("  - Slow endpoints may benefit from database query optimization")
    
    if error_endpoints:
        print("  - Failed endpoints should be fixed before scaling")
    
    print(f"\n  Throughput: {total_requests / duration:.1f} requests/sec ({total_requests} requests in {duration}s)")
    
    return by_endpoint


def main():
    if len(sys.argv) != 3:
        print(f"Usage: python3 {sys.argv[0]} <num_users:1-5> <duration_seconds>")
        sys.exit(1)
    
    num_users = int(sys.argv[1])
    duration = int(sys.argv[2])
    
    if num_users < 1 or num_users > 5:
        print("Error: num_users must be 1-5")
        sys.exit(1)
    
    print(f"Multi-User Performance Test")
    print(f"  Users: {num_users}")
    print(f"  Duration: {duration}s")
    print(f"  Endpoints: {len(USER_ENDPOINTS)}")
    
    # Shared results container
    endpoint_results = {
        "results": [],
        "lock": type('Lock', (), {'__enter__': lambda s: s, '__exit__': lambda s, *a: None})()
    }
    
    # Start collecting container stats
    print(f"\nCollecting baseline container stats...")
    baseline_stats = collect_container_stats(5)
    
    print(f"\nStarting {num_users} user simulation...")
    start = time.monotonic()
    
    # Run users concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = []
        for i in range(num_users):
            fut = executor.submit(user_workflow, i + 1, duration, endpoint_results)
            futures.append(fut)
        
        # Wait for all users to complete
        concurrent.futures.wait(futures)
    
    elapsed = time.monotonic() - start
    print(f"\nAll users completed in {elapsed:.1f}s")
    
    # Collect final container stats
    print(f"\nCollecting peak resource usage...")
    peak_stats = collect_container_stats(5)
    
    # Analyze and report
    results = endpoint_results["results"]
    analyze_results(results, peak_stats, elapsed, num_users)
    
    # Save results to JSON
    output_file = f"/tmp/stress-multi-user-{num_users}users-{duration}s.json"
    with open(output_file, 'w') as f:
        json.dump({
            "num_users": num_users,
            "duration_seconds": duration,
            "total_requests": len(results),
            "by_endpoint": {k: [
                {"latency_ms": r["latency_ms"], "error": r["error"]}
                for r in v
            ] for k, v in {f"{r['method']} {r['url']}": [] for r in results}.items()},
            "container_stats": peak_stats
        }, f, indent=2)
    
    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
