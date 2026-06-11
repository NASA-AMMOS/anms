#!/usr/bin/env bash
# Fine-grained stress test with per-endpoint latency, DB pool, proxy overhead,
# OpenSearch logging latency, and per-container resource tracking.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${AUTHNZ_PORT:=8084}"
# Auto-detect authnz port if not overridden
if [[ "${AUTHNZ_PORT}" == "80" ]]; then
    DETECTED=$(docker inspect anms-authnz-1 \
        --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if eq $p "80/tcp"}}{{(index $conf 0).HostPort}}{{end}}{{end}}' \
        2>/dev/null || echo "80")
    if [[ -n "${DETECTED}" ]] && [[ "${DETECTED}" != "80" ]]; then
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
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "[Phase A] Proxy & network overhead measurement"
echo "═══════════════════════════════════════════════════════════"

python3 "${SCRIPT_DIR}/scripts/stress_proxy_overhead.py" \
    "$COOKIES_FILE" "$METRICS_DIR" "$AUTHNZ_PORT"

echo ""

# ─── Phase B: Per-Endpoint Latency Breakdown ─────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase B] Per-endpoint latency breakdown (detailed)"
echo "═══════════════════════════════════════════════════════════"

python3 "${SCRIPT_DIR}/scripts/stress_endpoint_latency.py" \
    "$COOKIES_FILE" "$METRICS_DIR" "$AUTHNZ_PORT"

echo ""

# ─── Phase C: OpenSearch Logging Latency ─────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase C] OpenSearch logging latency (per-logging-ops overhead)"
echo "═══════════════════════════════════════════════════════════"

python3 "${SCRIPT_DIR}/scripts/stress_logging_latency.py" \
    "$COOKIES_FILE" "$METRICS_DIR" "$AUTHNZ_PORT"

echo ""

# ─── Phase D: Sustained Load with Resource Tracking ─────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase D] Sustained load + per-container resource tracking"
echo "═══════════════════════════════════════════════════════════"

TMP_RAW="$METRICS_DIR/container_stats_raw.txt"
echo "  Running 30s sustained load..."

# Start sustained load in background, wait for it to finish, then collect stats
python3 "${SCRIPT_DIR}/scripts/stress_sustained_load.py" \
    "$COOKIES_FILE" "$AUTHNZ_PORT" &
LOAD_PID=$!

# Collect docker stats samples while load is running (and one after)
for i in $(seq 1 15); do
    docker stats --no-stream \
        --format '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.NetIO}}|{{.BlockIO}}' \
        >> "$TMP_RAW" 2>/dev/null
    sleep 0.5
done

# Wait for load process to finish
wait $LOAD_PID 2>/dev/null || true

# Process container stats
python3 "${SCRIPT_DIR}/scripts/stress_container_stats.py" \
    "$TMP_RAW" "$METRICS_DIR"

echo ""

# ─── Phase E: Connection Pool Saturation ─────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase E] DB connection pool saturation (concurrent queries)"
echo "═══════════════════════════════════════════════════════════"

python3 "${SCRIPT_DIR}/scripts/stress_connection_pool.py" \
    "$COOKIES_FILE" "$AUTHNZ_PORT"

echo ""

# ─── Phase F: Apache Thread/Worker Analysis ──────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase F] Apache httpd thread/worker analysis"
echo "═══════════════════════════════════════════════════════════"

echo "  Checking Apache MPM configuration..."
echo "  Expected MPM: event (should have MaxRequestWorkers tuning)"

echo "  Apache status endpoints:"
for endpoint in "/server-status" "/server-info"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" \
        "http://localhost:${AUTHNZ_PORT}${endpoint}" 2>/dev/null || echo "N/A")
    echo "    ${endpoint}: HTTP ${status}"
done

echo ""
echo "  Checking Apache log level in Dockerfile..."
grep -i "LogLevel" /home/greennm1/anms/auth/demo/httpd.conf | head -5 || echo "    not found"

echo ""

# ─── Phase G: Grafana rendering path ─────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase G] Grafana rendering path latency"
echo "═══════════════════════════════════════════════════════════"

python3 "${SCRIPT_DIR}/scripts/stress_grafana_path.py" \
    "$COOKIES_FILE" "$AUTHNZ_PORT"

echo ""

# ─── Phase H: Redis Session Key Analysis ─────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase H] Redis session performance"
echo "═══════════════════════════════════════════════════════════"

echo "  Checking Redis session backend..."
redis_ping=$(docker exec anms-redis-1 redis-cli ping 2>/dev/null || echo "N/A")
echo "    Redis ping: ${redis_ping}"

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
