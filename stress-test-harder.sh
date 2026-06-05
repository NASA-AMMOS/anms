#!/usr/bin/env bash
set -euo pipefail

# ─── Configuration ───────────────────────────────────────────────────────────
# Defaults are tuned to be safe for use alongside agent sessions.
# Override via env vars for full brutality: e.g. HTTP_CONCURRENCY=100 PHASE1_REQS=5000 ./stress-test-harder.sh
: "${AUTHNZ_PORT:=80}"
: "${HTTP_CONCURRENCY:=25}"
: "${COOKIES_FILE=$(mktemp /tmp/stress-cookies.XXXXXX)}"

# Phase 1
: "${PHASE1_REQS:=1000}"

# Phase 2 — read paths
: "${PHASE2_CONC:=20}"
: "${PHASE2_REQS:=1000}"

# Phase 3 — write paths
: "${PHASE3_CONC:=10}"
: "${PHASE3_REQS:=200}"

# Phase 4 — Grafana API
: "${PHASE4_CONC:=25}"
: "${PHASE4_REQS:=1000}"

# Phase 5 — sustained
: "${PHASE5_CONC:=20}"
: "${PHASE5_DURATION:=60}"

# Detect container runtime
DOCKER_CMD=${DOCKER_CMD:-$(command -v docker 2>/dev/null || command -v podman 2>/dev/null || echo podman)}

# Cleanup
TMP_METRICS=$(mktemp)
TMP_RAW=$(mktemp /tmp/stats.XXXXXX)
TMP_PEAK=$(mktemp)
trap 'rm -f "$TMP_METRICS" "$TMP_RAW" "$TMP_PEAK" "$COOKIES_FILE" 2>/dev/null || true' EXIT

cleanup_containers() {
    ${DOCKER_CMD} compose -f testenv-compose.yml down --remove-orphans 2>/dev/null || true
    ${DOCKER_CMD} compose down --remove-orphans 2>/dev/null || true
}
trap cleanup_containers EXIT

# ─── Helpers ─────────────────────────────────────────────────────────────────

wait_for_url() {
    local url="$1" desc="$2"
    echo -n "  waiting for ${desc}... "
    for i in $(seq 1 90); do
        if curl -sSf -o /dev/null "$url" 2>/dev/null; then
            echo "ok"; return 0
        fi
        sleep 1
    done
    echo "FAIL – ${desc} not ready after 90s"; return 1
}

# Login to authnz and save session cookie
do_login() {
    echo "  logging in as 'test'..."
    curl -sS -c "$COOKIES_FILE" \
        -X POST "http://localhost:${AUTHNZ_PORT}/authn/dologin.html" \
        -d "httpd_username=test&httpd_password=welcome1" \
        -o /dev/null -w "%{http_code}"
    echo ""
}

# HTTP load test supporting GET/POST/PUT/DELETE with cookies and status classification
http_load() {
    local target="$1" method="$2" concurrency="$3" num_requests="$4" label="$5"
    local cookie_file="$6"
    echo "  [load] ${label}: ${num_requests} reqs, ${concurrency} conc, method=${method}"

    local payload=""
    local content_type=""
    if [[ "$num_requests" =~ ^[0-9]+$ ]]; then
        :
    fi

    python3 - "$target" "$method" "$concurrency" "$num_requests" "$label" "$cookie_file" "$payload" "$content_type" "$TMP_METRICS" <<'PYEOF'
import sys, urllib.request, concurrent.futures, time, statistics, json

target   = sys.argv[1]
method   = sys.argv[2]
conc     = int(sys.argv[3])
nreqs    = int(sys.argv[4])
label    = sys.argv[5]
cookie   = sys.argv[6]
payload  = sys.argv[7]
ctype    = sys.argv[8]
outfile  = sys.argv[9]

err = 0
lats = []
codes = {}
start = time.monotonic()

def make_req():
    hdrs = {}
    if cookie:
        hdrs['Cookie'] = open(cookie).read().strip()
    data = payload.encode() if payload else None
    req = urllib.request.Request(target, data=data, headers=hdrs, method=method)
    if ctype:
        req.add_header('Content-Type', ctype)
    return req

def do_req(req):
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()
            return (time.monotonic() - t0, False, r.status)
    except urllib.error.HTTPError as e:
        return (time.monotonic() - t0, True, e.code)
    except Exception:
        return (time.monotonic() - t0, True, 0)

with concurrent.futures.ThreadPoolExecutor(max_workers=conc) as ex:
    futures = [ex.submit(do_req, make_req()) for _ in range(nreqs)]
    for f in concurrent.futures.as_completed(futures):
        d, failed, code = f.result()
        lats.append(d)
        if failed:
            err += 1
        codes[code] = codes.get(code, 0) + 1

elapsed = time.monotonic() - start
ok = nreqs - err
s = sorted(lats)

print(f"  done: {ok}/{nreqs} ok, {err} errors")
print(f"  elapsed: {elapsed:.1f}s  avg: {statistics.mean(lats)*1000:.1f}ms  min: {min(lats)*1000:.1f}ms  max: {max(lats)*1000:.1f}ms" if lats else f"  elapsed: {elapsed:.1f}s (all failed)")
p50 = s[int(len(s)*0.5)]*1000 if s else 0
p95 = s[int(len(s)*0.95)]*1000 if s else 0
p99 = s[min(int(len(s)*0.99), len(s)-1)]*1000 if s else 0
print(f"  p50: {p50:.0f}ms  p95: {p95:.0f}ms  p99: {p99:.0f}ms")

# Error classification
err_by_code = {k: v for k, v in codes.items() if k != 200 and k != 0}
if err_by_code:
    print("  error codes:", dict(sorted(err_by_code.items())))

m = dict(
    label=label, method=method,
    elapsed=round(elapsed,1), ok=ok, errors=err,
    avg_ms=round(statistics.mean(lats)*1000,1) if lats else 0,
    p50_ms=round(s[int(len(s)*0.5)]*1000) if s else 0,
    p95_ms=round(s[int(len(s)*0.95)]*1000) if s else 0,
    p99_ms=round(s[min(int(len(s)*0.99), len(s)-1)]*1000) if s else 0,
    codes=dict(sorted(codes.items())),
    conc=conc
)
with open(outfile, 'a') as f:
    f.write(json.dumps(m) + '\n')
PYEOF
}

# Stats collection: snapshot before/after command for peak tracking
stats_and_run() {
    local outfile="$1"; shift
    # Snapshot before command
    docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}' > "$TMP_RAW" 2>/dev/null
    # Run the command
    "$@" 2>&1
    # Snapshot after (multiple samples to catch peak)
    local i
    for i in $(seq 1 10); do
        docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}' >> "$TMP_RAW" 2>/dev/null
        sleep 0.2
    done
    # Process collected stats
    python3 - "$TMP_RAW" "$outfile" <<'PYEOF'
import sys, json
raw, out = sys.argv[1], sys.argv[2]
peak = {}
with open(raw) as f:
    for line in f:
        p = line.strip().split('|')
        if len(p) != 4: continue
        try:
            name = p[0]
            cpu_v = float(p[1].replace('%', ''))
            mem_v = float(p[3].replace('%', ''))
            mem_raw = p[2]
            if name not in peak or cpu_v > peak[name][0]:
                peak[name] = (cpu_v, mem_v, mem_raw)
        except: pass
with open(out, 'w') as f:
    for n in sorted(peak, key=lambda k: peak[k][0], reverse=True):
        json.dump(dict(container=n, peak_cpu=round(peak[n][0],1), peak_mem=round(peak[n][1],1), mem_raw=peak[n][2]), f)
        f.write('\n')
PYEOF
}

show_stats() {
    if [[ -f "$2" ]] && [[ -s "$2" ]]; then
        echo "─── Container Stats ─── ($1)"
        python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    for line in f:
        d = json.loads(line)
        print('  {:30} CPU: {:5.1f}%  MEM: {:15s} ({:5.1f}%)'.format(d['container'], d['peak_cpu'], d['mem_raw'], d['peak_mem']))
print('---')
print()
" "$2"
    fi
}

# ─── Startup ─────────────────────────────────────────────────────────────────
echo "=== Hard Stress Test ==="
echo "Stack: authnz (port ${AUTHNZ_PORT}), Core API, Grafana, Adminer, NM, OpenSearch, Postgres, Redis"

# Clean up previous runs
${DOCKER_CMD} compose -f testenv-compose.yml down --remove-orphans 2>/dev/null || true
${DOCKER_CMD} compose down --remove-orphans 2>/dev/null || true

${DOCKER_CMD} compose up -d
${DOCKER_CMD} compose -f testenv-compose.yml up -d

sleep 5
if ! wait_for_url "http://localhost:${AUTHNZ_PORT}/" "authnz"; then
    echo "ERROR: authnz not reachable – aborting"; exit 1
fi
echo "System up – beginning load"
echo ""

# ─── Phase 1: Authenticated Session Throughput ──────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[phase] 1/5 – Authenticated session throughput"
echo "  Login, landing, /core/hello, /grafana/"
echo "  Concurrency: ${HTTP_CONCURRENCY}  Reqs/endpoint: ${PHASE1_REQS}"
echo "═══════════════════════════════════════════════════════════"

# Login
do_login
echo ""

# Authnz landing
if ! wait_for_url "http://localhost:${AUTHNZ_PORT}/" "authnz landing"; then exit 1; fi
stats_and_run "$TMP_PEAK" http_load \
    "http://localhost:${AUTHNZ_PORT}/" "GET" "${HTTP_CONCURRENCY}" "${PHASE1_REQS}" "landing-page" "$COOKIES_FILE"
echo ""; show_stats "landing-page" "$TMP_PEAK"

# Core hello
if ! wait_for_url "http://localhost:${AUTHNZ_PORT}/core/hello" "core/hello"; then exit 1; fi
stats_and_run "$TMP_PEAK" http_load \
    "http://localhost:${AUTHNZ_PORT}/core/hello" "GET" "${HTTP_CONCURRENCY}" "${PHASE1_REQS}" "core-hello" "$COOKIES_FILE"
echo ""; show_stats "core-hello" "$TMP_PEAK"

# Grafana UI
if ! wait_for_url "http://localhost:${AUTHNZ_PORT}/grafana/" "grafana"; then exit 1; fi
stats_and_run "$TMP_PEAK" http_load \
    "http://localhost:${AUTHNZ_PORT}/grafana/" "GET" "${HTTP_CONCURRENCY}" "${PHASE1_REQS}" "grafana-ui" "$COOKIES_FILE"
echo ""; show_stats "grafana-ui" "$TMP_PEAK"

echo ""

# ─── Phase 2: Core API Read Paths (Data-Heavy) ──────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[phase] 2/5 – Core API read paths (data-heavy)"
echo "  Concurrency: ${PHASE2_CONC}  Reqs/endpoint: ${PHASE2_REQS}"
echo "  Staggered 2s between endpoints"
echo "═══════════════════════════════════════════════════════════"

ENDPOINTS_P2=(
    "http://localhost:${AUTHNZ_PORT}/ari/all:ARI/all"
    "http://localhost:${AUTHNZ_PORT}/ari/all/display:ARI/all-display"
    "http://localhost:${AUTHNZ_PORT}/actual_objects/all:actual-objects"
    "http://localhost:${AUTHNZ_PORT}/formal_objects/all:formal-objects"
    "http://localhost:${AUTHNZ_PORT}/agents/all:agents"
    "http://localhost:${AUTHNZ_PORT}/report/page:report-page"
    "http://localhost:${AUTHNZ_PORT}/report/all:report-all"
    "http://localhost:${AUTHNZ_PORT}/actual_parameter/all:actual-parameter"
    "http://localhost:${AUTHNZ_PORT}/formal_parameter/all:formal-parameter"
    "http://localhost:${AUTHNZ_PORT}/agents/parameter/definition/all:agents-param-def"
)

for ep_info in "${ENDPOINTS_P2[@]}"; do
    IFS=':' read -r ep label <<< "$ep_info"
    echo ""
    stats_and_run "$TMP_PEAK" http_load \
        "$ep" "GET" "${PHASE2_CONC}" "${PHASE2_REQS}" "read-${label}" "$COOKIES_FILE"
    echo ""; show_stats "read-${label}" "$TMP_PEAK"
    sleep 2
done

echo ""

# ─── Phase 3: Write Operations & State Changes ──────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[phase] 3/5 – Write operations & state changes"
echo "  Concurrency: ${PHASE3_CONC}  Reqs/endpoint: ${PHASE3_REQS}"
echo "═══════════════════════════════════════════════════════════"

# Logging
echo ""
stats_and_run "$TMP_PEAK" http_load \
    "http://localhost:${AUTHNZ_PORT}/logging" "POST" "${PHASE3_CONC}" "${PHASE3_REQS}" \
    "POST /logging" "$COOKIES_FILE" '{"message": "stress-test-heartbeat"}' "application/json"
echo ""; show_stats "POST /logging" "$TMP_PEAK"

# Logging query
echo ""
stats_and_run "$TMP_PEAK" http_load \
    "http://localhost:${AUTHNZ_PORT}/logging/query" "POST" "${PHASE3_CONC}" "${PHASE3_REQS}" \
    "POST /logging/query" "$COOKIES_FILE" '{"limit": 10}' "application/json"
echo ""; show_stats "POST /logging/query" "$TMP_PEAK"

# ADM load default
echo ""
stats_and_run "$TMP_PEAK" http_load \
    "http://localhost:${AUTHNZ_PORT}/adms/load_default" "POST" "${PHASE3_CONC}" "${PHASE3_REQS}" \
    "POST /adms/load_default" "$COOKIES_FILE" "" ""
echo ""; show_stats "POST /adms/load_default" "$TMP_PEAK"

# Users
echo ""
stats_and_run "$TMP_PEAK" http_load \
    "http://localhost:${AUTHNZ_PORT}/users" "POST" "${PHASE3_CONC}" "${PHASE3_REQS}" \
    "POST /users" "$COOKIES_FILE" '{"username": "stresstest"}' "application/json"
echo ""; show_stats "POST /users" "$TMP_PEAK"

# Transcoder
echo ""
stats_and_run "$TMP_PEAK" http_load \
    "http://localhost:${AUTHNZ_PORT}/transcoder/ui/incoming/str" "PUT" "${PHASE3_CONC}" "${PHASE3_REQS}" \
    "PUT /transcoder" "$COOKIES_FILE" "stress-test-payload" ""
echo ""; show_stats "PUT /transcoder" "$TMP_PEAK"

# Alerts acknowledge
echo ""
stats_and_run "$TMP_PEAK" http_load \
    "http://localhost:${AUTHNZ_PORT}/alerts/acknowledge/1" "PUT" "${PHASE3_CONC}" "${PHASE3_REQS}" \
    "PUT /alerts/ack" "$COOKIES_FILE" "" ""
echo ""; show_stats "PUT /alerts/ack" "$TMP_PEAK"

echo ""

# ─── Phase 4: Grafana API + Proxy Chain Stress ──────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[phase] 4/5 – Grafana API + proxy chain"
echo "  Concurrency: ${PHASE4_CONC}  Reqs/endpoint: ${PHASE4_REQS}"
echo "═══════════════════════════════════════════════════════════"

GRAFANA_ENDPOINTS=(
    "http://localhost:${AUTHNZ_PORT}/grafana/api/health:grafana-health"
    "http://localhost:${AUTHNZ_PORT}/grafana/api/org:grafana-org"
    "http://localhost:${AUTHNZ_PORT}/grafana/api/search:grafana-search"
    "http://localhost:${AUTHNZ_PORT}/grafana/:grafana-ui"
)

for ep_info in "${GRAFANA_ENDPOINTS[@]}"; do
    IFS=':' read -r ep label <<< "$ep_info"
    echo ""
    stats_and_run "$TMP_PEAK" http_load \
        "$ep" "GET" "${PHASE4_CONC}" "${PHASE4_REQS}" "grafana-${label}" "$COOKIES_FILE"
    echo ""; show_stats "grafana-${label}" "$TMP_PEAK"
    sleep 1
done

echo ""

# ─── Phase 5: Sustained Load (Duration-Based) ───────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[phase] 5/5 – Sustained load (${PHASE5_DURATION}s at ${PHASE5_CONC} conc)"
echo "  Mix: /core/hello 40%, /grafana/api/health 30%, /ari/all 20%, /report/page 10%"
echo "═══════════════════════════════════════════════════════════"

echo ""
echo "  Starting ${PHASE5_DURATION}s sustained load..."
START_SUSTAINED=$(date +%s)
sustained_end=$((START_SUSTAINED + PHASE5_DURATION))
elapsed=0
req_count=0

python3 - "$COOKIES_FILE" "$TMP_METRICS" "$AUTHNZ_PORT" "$PHASE5_CONC" "$PHASE5_DURATION" <<'PYEOF'
import urllib.request, concurrent.futures, time, statistics, json, sys

cookie_file = sys.argv[1]
outfile = sys.argv[2]
authnz_port = sys.argv[3]
conc = int(sys.argv[4])
duration = int(sys.argv[5])

urls = [
    ("http://localhost:{}/core/hello".format(authnz_port), "sustained-core", 0.40),
    ("http://localhost:{}/grafana/api/health".format(authnz_port), "sustained-grafana-health", 0.30),
    ("http://localhost:{}/ari/all".format(authnz_port), "sustained-ari-all", 0.20),
    ("http://localhost:{}/report/page".format(authnz_port), "sustained-report-page", 0.10),
]

cookie = open(cookie_file).read().strip()
start = time.monotonic()
all_lats = []
all_codes = {}

while time.monotonic() - start < duration:
    # Pick URL based on weighted round-robin
    r = time.time()
    url_name_label = []
    cumulative = 0
    for url, label, weight in urls:
        cumulative += weight
        if r % 1.0 < cumulative or not url_name_label:
            url_name_label.append((url, label))
            break

    req = urllib.request.Request(url_name_label[0][0])
    req.add_header('Cookie', cookie)

    def do_req(req, label):
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                r.read()
                return (time.monotonic() - t0, False, r.status)
        except urllib.error.HTTPError as e:
            return (time.monotonic() - t0, True, e.code)
        except Exception:
            return (time.monotonic() - t0, True, 0)

    with concurrent.futures.ThreadPoolExecutor(max_workers=conc) as ex:
        futures = []
        for i in range(conc):
            url, label = url_name_label[0]
            req = urllib.request.Request(url)
            req.add_header('Cookie', cookie)
            futures.append(ex.submit(do_req, req, label))
        for f in concurrent.futures.as_completed(futures):
            d, failed, code = f.result()
            all_lats.append(d)
            all_codes[code] = all_codes.get(code, 0) + 1

elapsed = time.monotonic() - start
total = len(all_lats)
ok = total - sum(v for k, v in all_codes.items() if k != 200 and k != 0)
s = sorted(all_lats)

print(f"  done: {ok}/{total} ok, {total-ok} errors in {elapsed:.0f}s")
if s:
    print(f"  avg: {statistics.mean(s)*1000:.1f}ms  p50: {s[int(len(s)*0.5)]*1000:.0f}ms  p95: {s[int(len(s)*0.95)]*1000:.0f}ms  p99: {s[min(int(len(s)*0.99),len(s)-1)]*1000:.0f}ms")
err_by_code = {k: v for k, v in all_codes.items() if k != 200}
if err_by_code:
    print(f"  error codes: {dict(sorted(err_by_code.items()))}")

m = dict(
    label="sustained", method="mixed",
    elapsed=round(elapsed,1), ok=ok, errors=total-ok,
    avg_ms=round(statistics.mean(s)*1000,1) if s else 0,
    p50_ms=round(s[int(len(s)*0.5)]*1000) if s else 0,
    p95_ms=round(s[int(len(s)*0.95)]*1000) if s else 0,
    p99_ms=round(s[min(int(len(s)*0.99),len(s)-1)]*1000) if s else 0,
    codes=dict(sorted(all_codes.items())),
    conc=conc,
    duration_s=round(elapsed)
)
with open(outfile, 'a') as f:
    f.write(json.dumps(m) + '\n')
PYEOF

echo ""; show_stats "sustained-load" "$TMP_PEAK"
echo ""

# ─── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Summary"
echo "═══════════════════════════════════════════════════════════"
python3 - "$TMP_METRICS" <<'PYEOF'
import json, sys

with open(sys.argv[1]) as f:
    lines = [l.strip() for l in f if l.strip()]

print('{:<22} {:>6} {:>6} {:>8} {:>5} {:>6} {:>9} {:>7} {:>7} {:>7}'.format(
    'Phase', 'Reqs', 'Conc', 'Dur(s)', 'Ok', 'Err', 'Avg(ms)', 'P50(ms)', 'P95(ms)', 'P99(ms)'))
print('-' * 95)

total_reqs = 0
total_ok = 0
total_errors = 0
for line in lines:
    r = json.loads(line)
    lbl = r.get('label', '?')
    reqs = r.get('ok', 0) + r.get('errors', 0)
    dur = r.get('elapsed', 0)
    conc = r.get('conc', '?')
    total_reqs += reqs
    total_ok += r.get('ok', 0)
    total_errors += r.get('errors', 0)
    print('{:<22} {:>6} {:>6} {:>8.1f} {:>5} {:>6} {:>9.1f} {:>7.0f} {:>7.0f} {:>7.0f}'.format(
        lbl, reqs, conc, dur, r['ok'], r['errors'],
        r['avg_ms'], r['p50_ms'], r['p95_ms'], r['p99_ms']))

print('-' * 95)
print(f'  TOTALS: {total_reqs} reqs, {total_ok} ok, {total_errors} errors ({100*total_errors/max(total_reqs,1):.1f}% error rate)')
PYEOF

echo ""
echo "Hard stress test finished."