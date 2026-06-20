import base64
import json
import os
import subprocess
import sys
import ssl
import time
import urllib.error
import urllib.request

from stress_utils import safe_throughput, compute_percentiles

# SSL context for self-signed certificates (testing only)
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

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

def make_basic_auth_header(username, password):
    """Create Basic Auth header value."""
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"

def timed_write(os_url, os_user, os_pass, n=50):
    """Time sequential logging write requests via OpenSearch."""
    log_entry = {"message": "stress-test-heartbeat", "timestamp": time.time()}
    data = json.dumps(log_entry).encode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": make_basic_auth_header(os_user, os_pass),
    }
    url = f"{os_url}/stress-test-logs/_doc"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    latencies = []
    codes = {}
    errors = 0
    start = time.monotonic()

    for _ in range(n):
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as r:
                r.read()
                latencies.append(time.monotonic() - t0)
                codes[r.status] = codes.get(r.status, 0) + 1
        except urllib.error.HTTPError as e:
            latencies.append(time.monotonic() - t0)
            codes[e.code] = codes.get(e.code, 0) + 1
            errors += 1
        except Exception:
            latencies.append(time.monotonic() - t0)
            errors += 1

    elapsed = time.monotonic() - start
    percentiles = compute_percentiles(latencies, (0.5, 0.95, 0.99))
    p50, p95, p99 = (percentiles + [0, 0, 0])[:3]

    success = n - errors
    return {
        "type": "write",
        "n": n,
        "ok": success,
        "errors": errors,
        "elapsed_s": round(elapsed, 3),
        "throughput": safe_throughput(success, elapsed),
        "avg_ms": round(sum(latencies) / len(latencies) * 1000, 1) if latencies else 0,
        "p50_ms": p50,
        "p95_ms": p95,
        "p99_ms": p99,
        "min_ms": round(min(latencies) * 1000, 1) if latencies else 0,
        "max_ms": round(max(latencies) * 1000, 1) if latencies else 0,
        "codes": dict(sorted(codes.items())),
    }

def timed_query(os_url, os_user, os_pass, n=50):
    """Time sequential logging query requests via OpenSearch."""
    query = {"query": {"match_all": {}}, "size": 10}
    data = json.dumps(query).encode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": make_basic_auth_header(os_user, os_pass),
    }
    url = f"{os_url}/stress-test-logs/_search"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    latencies = []
    codes = {}
    errors = 0
    start = time.monotonic()

    for _ in range(n):
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as r:
                body = r.read()
                latencies.append(time.monotonic() - t0)
                codes[r.status] = codes.get(r.status, 0) + 1
        except urllib.error.HTTPError as e:
            latencies.append(time.monotonic() - t0)
            codes[e.code] = codes.get(e.code, 0) + 1
            errors += 1
        except Exception:
            latencies.append(time.monotonic() - t0)
            errors += 1

    elapsed = time.monotonic() - start
    percentiles = compute_percentiles(latencies, (0.5, 0.95, 0.99))
    p50, p95, p99 = (percentiles + [0, 0, 0])[:3]

    success = n - errors
    return {
        "type": "query",
        "n": n,
        "ok": success,
        "errors": errors,
        "elapsed_s": round(elapsed, 3),
        "throughput": safe_throughput(success, elapsed),
        "avg_ms": round(sum(latencies) / len(latencies) * 1000, 1) if latencies else 0,
        "p50_ms": p50,
        "p95_ms": p95,
        "p99_ms": p99,
        "min_ms": round(min(latencies) * 1000, 1) if latencies else 0,
        "max_ms": round(max(latencies) * 1000, 1) if latencies else 0,
        "codes": dict(sorted(codes.items())),
    }

def summarize(label, result):
    if not result:
        return ""
    avg = result.get("avg_ms", 0)
    p95 = result.get("p95_ms", 0)
    p99 = result.get("p99_ms", 0)
    tp = result.get("throughput", 0)
    return f"    {label}: avg={avg}ms  p95={p95}ms  p99={p99}ms  {tp} req/s"

def get_opensearch_password():
    """Get OpenSearch password from env, .env, or docker."""
    # 1. Check environment variable
    password = os.environ.get("OPENSEARCH_PASSWORD", "")
    if password:
        return password
    
    # Try to get from docker container
    try:
        r = subprocess.run(
            ["docker", "exec", "anms-opensearch-1", "printenv", "OPENSEARCH_INITIAL_ADMIN_PASSWORD"],
            capture_output=True, text=True, timeout=5
        )
        return r.stdout.strip()
    except Exception:
        pass
    
    return ""

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

    mode_str = "direct" if direct else "authnz"
    
    # Get OpenSearch credentials
    os_user = "admin"
    os_pass = get_opensearch_password()
    os_url = "https://localhost:9200"
    
    print(f"  Mode: {mode_str} - Testing OpenSearch directly at {os_url}")
    print(f"  User: {os_user} (password: {'*' * 8 if os_pass else 'NOT SET'})")

    if not os_pass:
        print("  ERROR: Could not find OpenSearch password. Set OPENSEARCH_PASSWORD env var.")
        sys.exit(1)

    # Create test index first
    print("  Creating test index...")
    index_data = json.dumps({
        "settings": {"number_of_shards": 1, "number_of_replicas": 0}
    }).encode()
    index_req = urllib.request.Request(
        f"{os_url}/stress-test-logs",
        data=index_data,
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    try:
        urllib.request.urlopen(index_req, timeout=10, context=ssl_ctx)
    except urllib.error.HTTPError as e:
        if e.code == 400:  # Index already exists
            pass
        else:
            print(f"  Warning: Could not create index: {e.code}")

    print("  Sequential write path:")
    write_result = timed_write(os_url, os_user, os_pass)
    print(summarize("write", write_result))

    print("  Sequential query path:")
    query_result = timed_query(os_url, os_user, os_pass)
    print(summarize("query", query_result))

    write_avg = write_result.get("avg_ms", 0)
    query_avg = query_result.get("avg_ms", 0)

    results = {"write": write_result, "query": query_result}

    with open(os.path.join(metrics_dir, "logging_results.json"), "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n  Logging overhead (write + query): {round(write_avg + query_avg, 1)}ms total")
    
    if write_result["errors"] > 0 or query_result["errors"] > 0:
        print("  WARNING: Some requests failed - check OpenSearch credentials")

if __name__ == "__main__":
    main()
