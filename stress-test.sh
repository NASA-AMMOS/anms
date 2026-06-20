#!/usr/bin/env bash
set -euo pipefail

# Safety checks
RAM_GB=$(grep -E '^MemTotal' /proc/meminfo 2>/dev/null | awk '{printf "%.0f", $2/1048576}') || true
if [[ -n "${RAM_GB:-}" ]] && (( RAM_GB < 8 )); then
  echo "WARNING: system RAM is ${RAM_GB} GB (< 8 GB) – reduced concurrency" >&2
fi
CORES=$(nproc 2>/dev/null) || true
if [[ -n "${CORES:-}" ]] && (( CORES < 4 )); then
  echo "WARNING: system has ${CORES} core(s) (< 4) – reduced concurrency" >&2
fi

# Source .env early so config values are available (including dry-run)
set -a && . .env && set +a

# Detect container runtime early (needed for cleanup)
DOCKER_CMD=${DOCKER_CMD:-$(command -v docker 2>/dev/null || command -v podman 2>/dev/null || echo podman)}

# Clean up any leftover containers from previous runs
${DOCKER_CMD} compose -f testenv-compose.yml down --remove-orphans 2>/dev/null || true
${DOCKER_CMD} compose down --remove-orphans 2>/dev/null || true

# Globals
: "${AUTHNZ_PORT:=80}"
: "${HTTP_CONCURRENCY:=100}"
: "${LANDING_REQS:=3000}"
: "${CORE_API_REQS:=2000}"
: "${GRAFANA_REQS:=2000}"
: "${GRAFANA_REQS:=2000}"

# Wait for a URL to respond (up to 90s, 1s interval)
wait_for_url() {
  local url="$1" desc="$2"
  echo -n "  waiting for ${desc}..."
  for i in $(seq 1 90); do
    if curl -sSf -o /dev/null "$url" 2>/dev/null; then
      echo " ok"; return 0
    fi
    sleep 1
  done
  echo " FAIL – ${desc} not ready after 90s"; return 1
}

# Startup
DOCKER_CMD=${DOCKER_CMD:-$(command -v docker 2>/dev/null || command -v podman 2>/dev/null || echo podman)}
${DOCKER_CMD} compose up -d
${DOCKER_CMD} compose -f testenv-compose.yml up -d

# Restart amp-manager after compose up. Known issue: amp-manager does not
# properly re-establish its connection to the Docker bridge network on its
# first start after the stack comes up, so a restart is required.
# amp-manager is defined in the main docker-compose.yml (not testenv).
${DOCKER_CMD} compose restart amp-manager
sleep 5

# Wait for UI
sleep 5
if ! wait_for_url "http://localhost:${AUTHNZ_PORT}/" "authnz"; then
  echo "ERROR: authnz not reachable – aborting"; exit 1
fi
echo "System up – beginning load"

TMP_METRICS=$(mktemp)
TMP_RAW=$(mktemp /tmp/stats.XXXXXX)
TMP_PEAK=$(mktemp)


cleanup() {
  rm -f "$TMP_METRICS" "$TMP_RAW" "$TMP_PEAK" 2>/dev/null || true
  ${DOCKER_CMD} compose -f testenv-compose.yml down --remove-orphans 2>/dev/null || true
  ${DOCKER_CMD} compose down --remove-orphans 2>/dev/null || true
}
trap cleanup EXIT

# HTTP load test
http_load() {
  local target="$1" concurrency="$2" num_requests="$3" label="$4"
  echo "[load] ${label}: ${num_requests} reqs, ${concurrency} conc"
  python3 -c "
import urllib.request, concurrent.futures, time, statistics, json
target,concurrency,num_requests,label='$1','$2','$3','$4'
err=0; lats=[]; start=time.monotonic()
def req(_):
    t0=time.monotonic()
    try:
        with urllib.request.urlopen(urllib.request.Request(target), timeout=10) as r: r.read()
    except: return (time.monotonic()-t0, True)
    return (time.monotonic()-t0, False)
with concurrent.futures.ThreadPoolExecutor(max_workers=int(concurrency)) as ex:
    for f in concurrent.futures.as_completed([ex.submit(req,None) for _ in range(int(num_requests))]):
        d,e=f.result(); lats.append(d); err+=e
el=time.monotonic()-start; ok=int(num_requests)-err; s=sorted(lats)
if lats:
    print('  done: {}/{} ok, {} errors'.format(ok,int(num_requests), err))
    print('  elapsed: {:.1f}s  avg: {:.1f}ms  min: {:.1f}ms  max: {:.1f}ms'.format(el, statistics.mean(lats)*1000, min(lats)*1000, max(lats)*1000))
    p50=s[int(len(s)*0.5)]*1000; p95=s[int(len(s)*0.95)]*1000; p99=s[min(int(len(s)*0.99),len(s)-1)]*1000
    print('  p50: {:.0f}ms  p95: {:.0f}ms  p99: {:.0f}ms'.format(p50,p95,p99))
else:
    print('  done: {}/{} ok, {} errors (all failed)'.format(ok,int(num_requests), err))
    print('  elapsed: {:.1f}s'.format(el))
m=dict(label=label, elapsed=round(el,1), ok=ok, errors=err,
    avg_ms=round(statistics.mean(lats)*1000,1) if lats else 0,
    p50_ms=round(s[int(len(s)*0.5)]*1000) if lats else 0,
    p95_ms=round(s[int(len(s)*0.95)]*1000) if lats else 0,
    p99_ms=round(s[min(int(len(s)*0.99),len(s)-1)]*1000) if lats else 0)
with open('$TMP_METRICS','a') as f: f.write(json.dumps(m)+'\n')
" 2>/dev/null || true
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

# Display stats
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

# Phase 1
echo ""; echo "[phase] 1/3 – Landing page load"
if ! wait_for_url "http://localhost:${AUTHNZ_PORT}/" "authnz landing"; then exit 1; fi
stats_and_run "$TMP_PEAK" http_load "http://localhost:${AUTHNZ_PORT}/" "${HTTP_CONCURRENCY}" "${LANDING_REQS}" "landing"
echo ""; show_stats "landing" "$TMP_PEAK"

# Phase 2
echo "[phase] 2/3 – Core API load"
if ! wait_for_url "http://localhost:${AUTHNZ_PORT}/core/hello" "authnz core/hello"; then exit 1; fi
stats_and_run "$TMP_PEAK" http_load "http://localhost:${AUTHNZ_PORT}/core/hello" "${HTTP_CONCURRENCY}" "${CORE_API_REQS}" "core API"
echo ""; show_stats "core API" "$TMP_PEAK"

# Phase 3
echo "[phase] 3/3 – Grafana load"
if ! wait_for_url "http://localhost:${AUTHNZ_PORT}/grafana/" "authnz grafana"; then exit 1; fi
stats_and_run "$TMP_PEAK" http_load "http://localhost:${AUTHNZ_PORT}/grafana/" "${HTTP_CONCURRENCY}" "${GRAFANA_REQS}" "grafana"
echo ""; show_stats "grafana" "$TMP_PEAK"

# Summary
echo ""; echo "Summary:"
python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    lines = [l.strip() for l in f if l.strip()]
reqs = {'landing': sys.argv[2], 'core API': sys.argv[3], 'grafana': sys.argv[4]}
print('{:<10} {:>8} {:>11} {:>8} {:>6} {:>8} {:>9} {:>7} {:>7} {:>7}'.format('Phase','Requests','Concurrency','Duration','Ok','Errors','Avg(ms)','P50(ms)','P95(ms)','P99(ms)'))
print('-' * 95)
for line in lines:
    r = json.loads(line)
    lbl = r.get('label','?')
    print('{:<10} {:>8} {:>11} {:>8.1f}s {:>6} {:>8} {:>9.1f} {:>7.0f} {:>7.0f} {:>7.0f}'.format(lbl, reqs.get(lbl,'?'), 100, r['elapsed'], r['ok'], r['errors'], r['avg_ms'], r['p50_ms'], r['p95_ms'], r['p99_ms']))
print('-' * 95)
" "$TMP_METRICS" "${LANDING_REQS}" "${CORE_API_REQS}" "${GRAFANA_REQS}"
echo ""; echo "Stress test finished"
