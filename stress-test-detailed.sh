#!/usr/bin/env bash
# Fine-grained stress test with per-endpoint latency, DB pool, proxy overhead,
# OpenSearch logging latency, and per-container resource tracking.
set -euo pipefail

# ─── Config ──────────────────────────────────────────────────────────────────
: "${AUTHNZ_PORT:=80}"
# Auto-detect authnz port if not overridden
if [[ "${AUTHNZ_PORT}" == "80" ]]; then
    DETECTED=$(docker inspect anms-authnz-1 --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if eq $p "80/tcp"}}{{(index $conf 0).HostPort}}{{end}}{{end}}' 2>/dev/null || echo "80")
    if [[ "${DETECTED}" != "" ]] && [[ "${DETECTED}" != "80" ]]; then
        AUTHNZ_PORT="${DETECTED}"
    fi
fi
: "${HTTP_CONCURRENCY:=100}"
: "${COOKIES_FILE=$(mktemp /tmp/stress-cookies.XXXXXX)}"
: "${METRICS_DIR=$(mktemp -d /tmp/stress-metrics.XXXXXX)}"

cleanup() { rm -rf "$METRICS_DIR" "$COOKIES_FILE" 2>/dev/null || true; }
trap cleanup EXIT

DOCKER_CMD=${DOCKER_CMD:-$(command -v docker 2>/dev/null || command -v podman 2>/dev/null || echo podman)}

# Cleanup containers
${DOCKER_CMD} compose -f testenv-compose.yml down --remove-orphans 2>/dev/null || true
${DOCKER_CMD} compose down --remove-orphans 2>/dev/null || true

wait_for_url() {
    local url="$1" desc="$2"
    echo -n "  waiting for ${desc}... "
    for i in $(seq 1 90); do
        if curl -sSf -o /dev/null "$url" 2>/dev/null; then
            echo "ok"; return 0
        fi
        sleep 1
    done
    echo "FAIL"; return 1
}

do_login() {
    curl -sS -c "$COOKIES_FILE" \
        -X POST "http://localhost:${AUTHNZ_PORT}/authn/dologin.html" \
        -d "httpd_username=test&httpd_password=welcome1" \
        -o /dev/null -w "%{http_code}" > /dev/null
    echo " logged in"
}

# ─── Startup ─────────────────────────────────────────────────────────────────
echo "=== Detailed Stress Test (Fine-Grained Metrics) ==="
echo "Stack: authnz→core/grafana/adminer/postgres/redis/opensearch/..."

${DOCKER_CMD} compose up -d
${DOCKER_CMD} compose -f testenv-compose.yml up -d
sleep 5

if ! wait_for_url "http://localhost:${AUTHNZ_PORT}/" "authnz"; then exit 1; fi
echo "System up"

# ─── Phase A: Proxy Overhead Measurement ─────────────────────────────────────
# Measure: round-trip through Apache + internal network vs direct container
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "[Phase A] Proxy & network overhead measurement"
echo "═══════════════════════════════════════════════════════════"

# Direct-to-container endpoints (bypass Apache proxy)
python3 - "$COOKIES_FILE" "$METRICS_DIR" "$AUTHNZ_PORT" <<'PYEOF'
import urllib.request, concurrent.futures, time, statistics, json, os, sys

cookie_file = sys.argv[1]
metrics_dir = sys.argv[2]
authnz_port = sys.argv[3]

cookie = open(cookie_file).read().strip()

def timed_request(url, label, concurrency=50, n=500):
    """Time a batch of requests and return latencies."""
    latencies = []
    codes = {}
    errors = 0
    start = time.monotonic()
    req = urllib.request.Request(url)
    req.add_header('Cookie', cookie)
    
    def do_req():
        t0 = time.monotonic()
        try:
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
            if failed: errors += 1

    elapsed = time.monotonic() - start
    s = sorted(latencies)
    result = {
        "label": label, "n": n, "ok": n - errors, "errors": errors,
        "elapsed_s": round(elapsed, 3),
        "throughput": round((n - errors) / elapsed, 1),
        "avg_ms": round(statistics.mean(s) * 1000, 1) if s else 0,
        "p50_ms": round(s[int(len(s)*0.5)] * 1000, 1) if s else 0,
        "p95_ms": round(s[int(len(s)*0.95)] * 1000, 1) if s else 0,
        "p99_ms": round(s[min(int(len(s)*0.99), len(s)-1)] * 1000, 1) if s else 0,
        "min_ms": round(min(s) * 1000, 1) if s else 0,
        "max_ms": round(max(s) * 1000, 1) if s else 0,
        "codes": dict(sorted(codes.items())),
    }
    return result

# Proxy path (through Apache)
proxy_urls = {
    "proxy:core/hello": f"http://localhost:{authnz_port}/core/hello",
    "proxy:ari/all": f"http://localhost:{authnz_port}/ari/all",
    "proxy:actual-objects/all": f"http://localhost:{authnz_port}/actual_objects/all",
    "proxy:grafana/health": f"http://localhost:{authnz_port}/grafana/api/health",
}

# Direct path (bypass Apache, hit containers directly)
direct_urls = {
    "direct:core/hello": "http://anms-core:5555/core/hello",
    "direct:ari/all": "http://anms-core:5555/ari/all",
    "direct:actual-objects/all": "http://anms-core:5555/actual_objects/all",
    "direct:grafana/health": "http://grafana:3000/api/health",
}

results = {}
print("  --- Through proxy (Apache + Docker network) ---")
for label, url in proxy_urls.items():
    r = timed_request(url, label, concurrency=100, n=500)
    results[f"proxy:{label.split(':',1)[1]}"] = r
    print(f"    {label}: {r['throughput']} req/s  avg={r['avg_ms']}ms  p95={r['p95_ms']}ms  err={r['errors']}")

print("  --- Direct (bypass Apache, direct container IP) ---")
for label, url in direct_urls.items():
    r = timed_request(url, label, concurrency=100, n=500)
    results[f"direct:{label.split(':',1)[1]}"] = r
    print(f"    {label}: {r['throughput']} req/s  avg={r['avg_ms']}ms  p95={r['p95_ms']}ms  err={r['errors']}")

# Save
with open(os.path.join(metrics_dir, "proxy_overhead.json"), 'w') as f:
    json.dump(results, f, indent=2)

# Compute overhead
for ep in ["core/hello", "ari/all", "actual-objects/all", "grafana/health"]:
    proxy = results.get(f"proxy:{ep}", {})
    direct = results.get(f"direct:{ep}", {})
    if proxy and direct:
        overhead_pct = round(((proxy.get('avg_ms',0) - direct.get('avg_ms',0)) / max(direct.get('avg_ms',1), 1)) * 100, 1)
        proxy_throughput = proxy.get('throughput', 0)
        direct_throughput = direct.get('throughput', 0)
        print(f"\n  OVERHEAD for {ep}:")
        print(f"    Latency overhead: +{overhead_pct}% (proxy avg={proxy.get('avg_ms',0)}ms vs direct avg={direct.get('avg_ms',0)}ms)")
        print(f"    Throughput delta: {proxy_throughput} vs {direct_throughput} req/s ({round(100*(proxy_throughput/direct_throughput),1)}% of direct)")
PYEOF

echo ""

# ─── Phase B: Per-Endpoint Latency Breakdown ─────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase B] Per-endpoint latency breakdown (detailed)"
echo "═══════════════════════════════════════════════════════════"

ENDPOINTS=(
    "GET|/core/hello|core-hello"
    "GET|/ari/all|ari-all"
    "GET|/ari/all/display|ari-all-display"
    "GET|/actual_objects/all|actual-objects"
    "GET|/formal_objects/all|formal-objects"
    "GET|/agents/all|agents"
    "GET|/report/page|report-page"
    "GET|/report/all|report-all"
    "GET|/grafana/api/health|grafana-health"
    "GET|/grafana/api/org|grafana-org"
    "GET|/grafana/api/search|grafana-search"
    "POST|/logging|POST-logging"
    "POST|/logging/query|POST-logging-query"
    "POST|/adms/load_default|POST-load-default"
    "POST|/users|POST-users"
    "PUT|/transcoder/ui/incoming/str|PUT-transcoder"
    "PUT|/alerts/acknowledge/1|PUT-alerts-ack"
)

python3 - "$COOKIES_FILE" "$METRICS_DIR" "$AUTHNZ_PORT" <<'PYEOF'
import urllib.request, concurrent.futures, time, statistics, json, os, sys, gzip

cookie_file = sys.argv[1]
metrics_dir = sys.argv[2]
authnz_port = sys.argv[3]
conc = 100
n = 500

cookie = open(cookie_file).read().strip()

def timed_request(method, url, payload=None, content_type=None):
    hdrs = {'Cookie': cookie}
    if content_type:
        hdrs['Content-Type'] = content_type
    data = payload.encode() if payload else None
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    
    latencies = []
    codes = {}
    errors = 0
    start = time.monotonic()
    
    def do_req():
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read()
                # Measure response body size
                return (time.monotonic() - t0, False, r.status, len(body))
        except urllib.error.HTTPError as e:
            return (time.monotonic() - t0, True, e.code, 0)
        except Exception:
            return (time.monotonic() - t0, True, 0, 0)

    with concurrent.futures.ThreadPoolExecutor(max_workers=conc) as ex:
        futures = [ex.submit(do_req) for _ in range(n)]
        for f in concurrent.futures.as_completed(futures):
            d, failed, code, size = f.result()
            latencies.append(d)
            codes[code] = codes.get(code, 0) + 1
            if failed: errors += 1

    elapsed = time.monotonic() - start
    s = sorted(latencies)
    return {
        "n": n, "ok": n - errors, "errors": errors,
        "elapsed_s": round(elapsed, 3),
        "throughput": round((n - errors) / elapsed, 1) if elapsed > 0 else 0,
        "avg_ms": round(statistics.mean(s) * 1000, 1) if s else 0,
        "p50_ms": round(s[int(len(s)*0.5)] * 1000, 1) if s else 0,
        "p95_ms": round(s[int(len(s)*0.95)] * 1000, 1) if s else 0,
        "p99_ms": round(s[min(int(len(s)*0.99), len(s)-1)] * 1000, 1) if s else 0,
        "min_ms": round(min(s) * 1000, 1) if s else 0,
        "max_ms": round(max(s) * 1000, 1) if s else 0,
        "avg_body_bytes": round(statistics.mean([size for _, _, size in [(0,0,0)]]) * n / n, 0),
        "codes": dict(sorted(codes.items())),
    }

results = {}
for entry in open(os.path.join(metrics_dir, "endpoint_results.json"), 'w') as dummy:
    pass  # ensure file exists

# Actually write results
with open(os.path.join(metrics_dir, "endpoint_results.json"), 'w') as f:
    for method, path, label in ENDPOINTS:
        url = f"http://localhost:{authnz_port}{path}"
        payload = content_type = None
        
        # POST/PUT payloads
        if method == "POST" and path == "/logging":
            payload = '{"message": "stress-test-heartbeat"}'; content_type = "application/json"
        elif method == "POST" and path == "/logging/query":
            payload = '{"limit": 10}'; content_type = "application/json"
        elif method == "POST" and path == "/users":
            payload = '{"username": "stresstest"}'; content_type = "application/json"
        elif method == "PUT" and "transcoder" in path:
            payload = "stress-test-payload"
        
        r = timed_request(method, url, payload, content_type)
        results[label] = r
        print(f"  {label:30s} {r['throughput']:8.1f} req/s  avg={r['avg_ms']:6.1f}ms  p95={r['p95_ms']:6.1f}ms  p99={r['p99_ms']:6.1f}ms  err={r['errors']:4d}")

    json.dump(results, f, indent=2)
PYEOF

echo ""

# ─── Phase C: OpenSearch Logging Latency ─────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase C] OpenSearch logging latency (per-logging-ops overhead)"
echo "═══════════════════════════════════════════════════════════"

# Measure /logging POST latency - this hits the logging endpoint which triggers
# an OpenSearch write for each request
python3 - "$COOKIES_FILE" "$METRICS_DIR" "$AUTHNZ_PORT" <<'PYEOF'
import urllib.request, concurrent.futures, time, statistics, json, os, sys

cookie_file = sys.argv[2]
metrics_dir = sys.argv[3]
authnz_port = sys.argv[1]
cookie = open(cookie_file).read().strip()

def log_request():
    url = f"http://localhost:{authnz_port}/logging"
    req = urllib.request.Request(url, 
        data=b'{"message": "stress-test-log"}',
        headers={'Cookie': cookie, 'Content-Type': 'application/json'},
        method='POST')
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return (time.monotonic() - t0, False)
    except Exception:
        return (time.monotonic() - t0, True)

# Run sequential to measure per-request overhead
print("  Sequential (no concurrency) - measures per-request overhead:")
latencies = []
for i in range(100):
    d, err = log_request()
    latencies.append(d)

s = sorted(latencies)
avg = statistics.mean(s) * 1000
p50 = s[len(s)//2] * 1000
p95 = s[int(len(s)*0.95)] * 1000
p99 = s[min(int(len(s)*0.99), len(s)-1)] * 1000
print(f"    avg={avg:.1f}ms  p50={p50:.1f}ms  p95={p95:.1f}ms  p99={p99:.1f}ms")

# Also measure /logging/query (read path - hits OpenSearch)
print("  Sequential /logging/query (read path):")
latencies_r = []
for i in range(100):
    url = f"http://localhost:{authnz_port}/logging/query"
    req = urllib.request.Request(url,
        data=b'{"limit": 10}',
        headers={'Cookie': cookie, 'Content-Type': 'application/json'},
        method='POST')
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            latencies_r.append(time.monotonic() - t0)
    except:
        pass

s2 = sorted(latencies_r)
avg2 = statistics.mean(s2) * 1000
print(f"    avg={avg2:.1f}ms  p50={s2[len(s2)//2]*1000:.1f}ms  p95={s2[int(len(s2)*0.95)]*1000:.1f}ms")

with open(os.path.join(metrics_dir, "logging_latency.json"), 'w') as f:
    json.dump({
        "write": {"avg_ms": round(avg,1), "p50_ms": round(p50,1), "p95_ms": round(p95,1), "p99_ms": round(p99,1)},
        "read": {"avg_ms": round(avg2,1), "p50_ms": round(s2[len(s2)//2]*1000,1), "p95_ms": round(s2[int(len(s2)*0.95)]*1000,1)}
    }, f, indent=2)
PYEOF

echo ""

# ─── Phase D: Sustained Load with Resource Tracking ─────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase D] Sustained load + per-container resource tracking"
echo "═══════════════════════════════════════════════════════════"

# Run a sustained load while tracking resources
TMP_RAW="$METRICS_DIR/container_stats_raw.txt"
echo "# Running 30s sustained load..."
python3 - "$COOKIES_FILE" "$AUTHNZ_PORT" <<'PYEOF' &
BGPID=$!
import urllib.request, concurrent.futures, time, statistics, json, sys

cookie_file = sys.argv[1]
authnz_port = sys.argv[2]
cookie = open(cookie_file).read().strip()
duration = 30

urls = [
    "http://localhost:{}/core/hello".format(authnz_port),
    "http://localhost:{}/ari/all".format(authnz_port),
    "http://localhost:{}/actual_objects/all".format(authnz_port),
    "http://localhost:{}/grafana/api/health".format(authnz_port),
]

all_lats = []
start = time.monotonic()
while time.monotonic() - start < duration:
    url = urls[int(time.time()) % len(urls)]
    def do_req(u):
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(u, timeout=10) as r: r.read()
            return time.monotonic() - t0
        except: return 999
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
        for f in concurrent.futures.as_completed([ex.submit(do_req, u) for _ in range(50)]):
            all_lats.append(f.result())
print(f"done: {len(all_lats)} reqs in {duration}s, avg={statistics.mean(all_lats)*1000:.1f}ms")
PYEOF

# Capture container stats during/after load (multiple samples)
for i in $(seq 1 15); do
    docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.NetIO}}|{{.BlockIO}}' >> "$TMP_RAW" 2>/dev/null
    sleep 0.5
done

# Process stats
python3 - "$TMP_RAW" "$METRICS_DIR" <<'PYEOF'
import sys, json

raw, metrics_dir = sys.argv[1], sys.argv[2]
import os

peak = {}
net_peak = {}
block_peak = {}
counts = {}

with open(raw) as f:
    for line in f:
        p = line.strip().split('|')
        if len(p) != 6: continue
        name = p[0]
        try:
            cpu_v = float(p[1].replace('%', ''))
            mem_pct = float(p[3].replace('%', ''))
            net = p[4]  # "1.2kB / 4.09kB"
            block = p[5]  # "0B / 0B"
            
            counts[name] = counts.get(name, 0) + 1
            if name not in peak or cpu_v > peak[name][0]:
                peak[name] = (cpu_v, p[2], mem_pct)
            
            # Parse net I/O
            net_parts = net.split('/')
            def parse_io(s):
                s = s.strip()
                if 'GB' in s: return float(s.replace('GB','').strip()) * 1024
                if 'MB' in s: return float(s.replace('MB','').strip())
                if 'kB' in s: return float(s.replace('kB','').strip()) / 1024
                if 'B' in s: return float(s.replace('B','').strip()) / (1024*1024)
                return 0
            net_in = parse_io(net_parts[0]) if len(net_parts) > 0 else 0
            net_out = parse_io(net_parts[1]) if len(net_parts) > 1 else 0
            
            if name not in net_peak or net_in > net_peak[name][0]:
                net_peak[name] = (net_in, net_out)
        except: pass

# Write peak stats
with open(os.path.join(metrics_dir, "container_stats.json"), 'w') as f:
    for n in sorted(peak, key=lambda k: peak[k][0], reverse=True):
        json.dump({
            "container": n,
            "peak_cpu": round(peak[n][0], 1),
            "samples": counts.get(n, 0),
            "peak_mem_raw": peak[n][1],
            "peak_mem_pct": round(peak[n][2], 1),
            "peak_net_in_mb": round(net_peak.get(n, (0,0))[0], 2),
            "peak_net_out_mb": round(net_peak.get(n, (0,0))[1], 2),
        }, f); f.write('\n')

# Print summary
print("  Peak container resources during sustained load:")
print(f"  {'Container':<35} {'CPU%':>6} {'Samples':>8} {'Mem%':>6} {'NetIn MB':>10} {'NetOut MB':>10}")
for n in sorted(peak, key=lambda k: peak[k][0], reverse=True):
    print(f"  {n:<35} {peak[n][0]:>5.1f}% {counts.get(n,0):>8} {peak[n][2]:>5.1f}% {net_peak.get(n,(0,0))[0]:>10.2f} {net_peak.get(n,(0,0))[1]:>10.2f}")
PYEOF

echo ""

# ─── Phase E: Connection Pool Saturation ─────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase E] DB connection pool saturation (concurrent queries)"
echo "═══════════════════════════════════════════════════════════"

# Fire many concurrent requests and check for pool exhaustion signals
python3 - "$COOKIES_FILE" "$AUTHNZ_PORT" <<'PYEOF'
import urllib.request, concurrent.futures, time, statistics, json, sys

cookie_file = sys.argv[1]
authnz_port = sys.argv[2]
cookie = open(cookie_file).read().strip()

def req(i):
    url = f"http://localhost:{authnz_port}/ari/all"
    t0 = time.monotonic()
    try:
        req = urllib.request.Request(url)
        req.add_header('Cookie', cookie)
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()
        return (time.monotonic() - t0, False)
    except urllib.error.HTTPError as e:
        return (time.monotonic() - t0, True, e.code)
    except Exception as e:
        return (time.monotonic() - t0, True, 0)

for conc_val in [10, 50, 100, 150, 200]:
latencies = []
errors = 0
start = time.monotonic()
    
with concurrent.futures.ThreadPoolExecutor(max_workers=conc_val) as ex:
    futures = [ex.submit(req, i) for i in range(conc_val)]
    for f in concurrent.futures.as_completed(futures):
        d, *rest = f.result()
        latencies.append(d)
        if rest and rest[0]:
            errors += 1
    
elapsed = time.monotonic() - start
s = sorted(latencies)
print(f"  conc={conc_val:3d}: {conc_val - errors}/{conc_val} ok, "
      f"throughput={round((conc_val-errors)/elapsed,1)} req/s, "
          f"avg={statistics.mean(s)*1000:.0f}ms, "
          f"p95={s[int(len(s)*0.95)]*1000:.0f}ms, "
          f"p99={s[min(int(len(s)*0.99),len(s)-1)]*1000:.0f}ms, "
          f"errors={errors}")
PYEOF

echo ""

# ─── Phase F: Apache Thread/Worker Analysis ──────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase F] Apache httpd thread/worker analysis"
echo "═══════════════════════════════════════════════════════════"

# Check Apache config for MPM settings
echo "  Checking Apache MPM configuration..."
# The demo uses mpm_event by default
echo "  Expected MPM: event (should have MaxRequestWorkers tuning)"

# Check current Apache status
echo "  Apache status endpoints:"
for endpoint in "/server-status" "/server-info"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${AUTHNZ_PORT}${endpoint}" 2>/dev/null || echo "N/A")
    echo "    ${endpoint}: HTTP ${status}"
done

# Check Apache log level (should be warn/info in production, not debug)
echo ""
echo "  Checking Apache log level in Dockerfile..."
grep -i "LogLevel" /home/greennm1/anms/auth/demo/httpd.conf | head -5 || echo "    not found"

echo ""

# ─── Phase G: Grafana rendering path ─────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase G] Grafana rendering path latency"
echo "═══════════════════════════════════════════════════════════"

python3 - "$COOKIES_FILE" "$AUTHNZ_PORT" <<'PYEOF'
import urllib.request, concurrent.futures, time, statistics, json, sys

cookie_file = sys.argv[1]
authnz_port = sys.argv[2]
cookie = open(cookie_file).read().strip()

grafana_endpoints = [
    "/grafana/api/health",
    "/grafana/api/org",
    "/grafana/api/search",
    "/grafana/",
]

for ep in grafana_endpoints:
    url = f"http://localhost:{authnz_port}{ep}"
    latencies = []
    errors = 0
    n = 200
    req = urllib.request.Request(url)
    req.add_header('Cookie', cookie)
    
    def do_req():
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read()
                return (time.monotonic() - t0, len(body))
        except:
            return (999, 0)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
        for f in concurrent.futures.as_completed([ex.submit(do_req) for _ in range(n)]):
            d, size = f.result()
            if d < 999:
                latencies.append(d)
            else:
                errors += 1
    
    s = sorted(latencies)
    if s:
        print(f"  {ep:30s} avg={statistics.mean(s)*1000:.0f}ms  p95={s[int(len(s)*0.95)]*1000:.0f}ms  p99={s[min(int(len(s)*0.99),len(s)-1)]*1000:.0f}ms  size={statistics.mean([size for _ in s])}B  err={errors}")
PYEOF

echo ""

# ─── Phase H: Redis Session Key Analysis ─────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase H] Redis session performance"
echo "═══════════════════════════════════════════════════════════"

# Check Redis is actually being used for sessions
echo "  Checking Redis session backend..."
# The anms-ui uses Redis, check if it's healthy
redis_ping=$(docker exec anms-redis-1 redis-cli ping 2>/dev/null || echo "N/A")
echo "    Redis ping: ${redis_ping}"

# Check Redis memory usage
redis_info=$(docker exec anms-redis-1 redis-cli INFO memory 2>/dev/null || echo "N/A")
redis_mem=$(echo "$redis_info" | grep "used_memory_human" | cut -d: -f2 | tr -d '[:space:]')
echo "    Redis used memory: ${redis_mem}"

echo ""

# ─── Summary ─────────────────────────────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "=== Test Complete - Results in: ${METRICS_DIR} ==="
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Files generated:"
ls -la "$METRICS_DIR"/
echo ""
echo "Run with YOLO (unlimited): ./${0##*/}"
echo "Run with caps: ./run-stress.sh ./${0##*/}"

# Cleanup containers
${DOCKER_CMD} compose -f testenv-compose.yml down --remove-orphans 2>/dev/null || true
${DOCKER_CMD} compose down --remove-orphans 2>/dev/null || true
echo ""
echo "Containers torn down."
