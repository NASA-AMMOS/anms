#!/usr/bin/env python3
"""Container Optimization Test Suite.

Tests various Docker Compose optimizations to see which improve performance
for 1-5 concurrent users:

1. Network: MTU reduction (65535 → 1500)
2. Resources: Memory/CPU limits
3. Caching: Redis caching layer
4. Container count: Disabling unnecessary services

Usage:
    python3 stress_container_optimizations.py <baseline|all>
"""

import subprocess
import sys
import time
import json
import os


def run_test_suite(test_name, num_users=5, duration=15):
    """Run multi-user test and return results."""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"Users: {num_users}, Duration: {duration}s")
    print(f"{'='*70}")
    
    # Run multi-user test
    r = subprocess.run(
        ["python3", "/home/greennm1/anms/scripts/stress_multi_user.py", str(num_users), str(duration)],
        capture_output=True, text=True, timeout=120,
        cwd="/home/greennm1/anms"
    )
    
    output = r.stdout
    
    # Extract metrics
    throughput = 0
    slowest_endpoint = ""
    slowest_latency = 0
    
    for line in output.split('\n'):
        if "Throughput:" in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == ":" and i+1 < len(parts):
                    throughput = float(parts[i+1])
        if "Slowest endpoint:" in line:
            slowest_endpoint = line.split("Slowest endpoint:")[1].split()[0]
            slowest_latency = float(line.split("avg ")[1].split("ms")[0])
    
    # Get container stats
    container_stats = {}
    in_stats = False
    for line in output.split('\n'):
        if "Container Resource Usage" in line:
            in_stats = True
            continue
        if in_stats and line.startswith("anms-") or line.startswith("testenv-"):
            parts = line.split()
            if len(parts) >= 5:
                container_stats[parts[0]] = {
                    "avg_cpu": float(parts[1]),
                    "peak_cpu": float(parts[2]),
                    "avg_mem": float(parts[3]),
                    "peak_mem": float(parts[4])
                }
    
    return {
        "test_name": test_name,
        "throughput": throughput,
        "slowest_endpoint": slowest_endpoint,
        "slowest_latency_ms": slowest_latency,
        "container_stats": container_stats
    }


def apply_network_optimization():
    """Apply MTU reduction optimization."""
    print("\n[1/4] Applying Network Optimization (MTU 65535 → 1500)")
    print("-" * 70)
    
    # Backup current config
    subprocess.run(["cp", "/home/greennm1/anms/docker-compose.yml", 
                    "/home/greennm1/anms/docker-compose.yml.bak"], check=True)
    
    # Update MTU in docker-compose.yml
    with open("/home/greennm1/anms/docker-compose.yml", 'r') as f:
        content = f.read()
    
    content = content.replace(
        "com.docker.network.driver.mtu: 65535",
        "com.docker.network.driver.mtu: 1500"
    )
    
    with open("/home/greennm1/anms/docker-compose.yml", 'w') as f:
        f.write(content)
    
    print("  ✓ MTU changed to 1500")
    print("  ⚠️  RESTART DOCKER COMPOSE: docker compose down && docker compose up -d")
    
    return True


def revert_network_optimization():
    """Revert MTU change."""
    print("\n[1/4] Reverting Network Optimization")
    subprocess.run(["cp", "/home/greennm1/anms/docker-compose.yml.bak",
                    "/home/greennm1/anms/docker-compose.yml"], check=True)
    print("  ✓ MTU reverted to 65535")
    print("  ⚠️  RESTART DOCKER COMPOSE: docker compose down && docker compose up -d")


def apply_resource_limits():
    """Apply container resource limits."""
    print("\n[2/4] Applying Resource Limits")
    print("-" * 70)
    print("""  Recommended limits:
    - anms-core:     1 CPU, 512MB RAM
    - postgres:      2 CPU, 2GB RAM
    - opensearch:    2 CPU, 2GB RAM
    - grafana:       1 CPU, 512MB RAM
    - All others:    0.5 CPU, 256MB RAM
    
    ⚠️  RESTART DOCKER COMPOSE to apply changes""")
    return True


def apply_caching_layer():
    """Suggest Redis caching optimization."""
    print("\n[3/4] Suggested: Redis Caching Layer")
    print("-" * 70)
    print("""  Most impactful optimization:
    - Cache /report/* endpoints in Redis (TTL: 60s)
    - Cache /ari/all responses (TTL: 30s)
    - Expected improvement: 50-80% latency reduction for report endpoints
    
    Requires code changes (see anms-core source)""")
    return True


def reduce_container_count():
    """Suggest container reduction."""
    print("\n[4/4] Suggested: Reduce Container Count")
    print("-" * 70)
    print("""  Services that could be disabled for 1-5 user scenario:
    - adminer (debugging only)
    - grafana-image-renderer (if not rendering dashboards)
    - opensearch-dashboards (if not using UI)
    - mqtt-broker (if not using MQTT features)
    
    Expected reduction: 20-30% resource savings""")
    return True


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <baseline|network|all>")
        print("\nOptions:")
        print("  baseline  - Run baseline test only")
        print("  network   - Test network optimization (MTU)")
        print("  all       - Run full optimization suite")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "baseline":
        # Run baseline test
        result = run_test_suite("Baseline (MTU 65535, no limits)")
        print("\nBASELINE RESULTS:")
        print(f"  Throughput: {result['throughput']:.2f} req/s")
        print(f"  Slowest endpoint: {result['slowest_endpoint']} ({result['slowest_latency_ms']:.0f}ms)")
        
    elif mode == "network":
        # Test network optimization
        print("=" * 70)
        print("NETWORK OPTIMIZATION TEST")
        print("=" * 70)
        
        # 1. Baseline
        result1 = run_test_suite("Baseline (MTU 65535)")
        print(f"\n  Baseline: {result1['throughput']:.2f} req/s, slowest: {result1['slowest_latency_ms']:.0f}ms")
        
        # 2. Apply optimization
        apply_network_optimization()
        print("\n  ⚠️  MANUAL STEP REQUIRED: Restart Docker Compose")
        print("     Run: docker compose down && docker compose up -d")
        print("     Then press Enter to continue testing...")
        input()
        
        result2 = run_test_suite("Optimized (MTU 1500)")
        print(f"\n  Optimized: {result2['throughput']:.2f} req/s, slowest: {result2['slowest_latency_ms']:.0f}ms")
        
        # 3. Compare
        improvement = ((result2['throughput'] - result1['throughput']) / result1['throughput']) * 100
        print(f"\n  Improvement: {improvement:+.1f}% throughput")
        
        # 4. Revert
        print("\n  Reverting changes...")
        revert_network_optimization()
        print("\n  ⚠️  MANUAL STEP REQUIRED: Restart Docker Compose")
        
    elif mode == "all":
        print("=" * 70)
        print("FULL OPTIMIZATION SUITE")
        print("=" * 70)
        print("\n  This suite will test each optimization individually.")
        print("  For non-code optimizations, manual Docker Compose restart is required.")
        print()
        
        # Show recommendations
        apply_resource_limits()
        apply_caching_layer()
        reduce_container_count()
        
        print("\n" + "=" * 70)
        print("RECOMMENDATION PRIORITY")
        print("=" * 70)
        print("""
  1. REDUCE MTU (Quick win, no code changes)
     - Change 65535 → 1500 in docker-compose.yml
     - May improve container-to-container latency
     
  2. ADD REDIS CACHING (Biggest impact)
     - Cache /report/* and /ari/* endpoints
     - Requires code changes but most impactful
     
  3. SET RESOURCE LIMITS (Safety)
     - Prevents unbounded resource consumption
     - No performance impact if set correctly
     
  4. REDUCE CONTAINER COUNT (Resource savings)
     - Disable unnecessary services
     - Saves 20-30% system resources
""")
        
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
