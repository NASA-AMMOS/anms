#!/usr/bin/env bash
# Fine-grained stress test with per-endpoint latency, DB pool, proxy overhead,
# OpenSearch logging latency, and per-container resource tracking.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Mode selection: DIRECT=1 bypasses authnz entirely, hits API on port 5555 directly
# This is the recommended mode for stress testing (authnz is for production only)
: "${DIRECT:=0}"
if [[ "${DIRECT}" == "1" ]]; then
    BASE_PORT=5555
    echo "=== Direct Mode (bypassing authnz, hitting API on port 5555) ==="
else
    : "${AUTHNZ_PORT:=8084}"
    BASE_PORT=${AUTHNZ_PORT}
    echo "=== Authnz Mode (hitting API through authnz proxy on port ${AUTHNZ_PORT}) ==="
fi

: "${HTTP_CONCURRENCY:=100}"
: "${COOKIES_FILE=$(mktemp /tmp/stress-cookies.XXXXXX)}"
: "${ADMIN_COOKIES_FILE=$(mktemp /tmp/stress-admin-cookies.XXXXXX)}"
: "${METRICS_DIR=$(mktemp -d /tmp/stress-metrics.XXXXXX)}"

cleanup() {
    rm -rf "$METRICS_DIR" "$COOKIES_FILE" "$ADMIN_COOKIES_FILE" 2>/dev/null || true
    # Teardown containers — runs on EXIT whether normal or abnormal
    compose down --remove-orphans 2>/dev/null || true
}
trap cleanup EXIT

DOCKER_CMD=${DOCKER_CMD:-$(command -v docker 2>/dev/null || command -v podman 2>/dev/null || echo podman)}

# Auto-apply podman override for docker-compose.yml and testenv-compose.yml
COMPOSE_DEFAULTS="-f docker-compose.yml -f testenv-compose.yml"
COMPOSE_OVERRIDE=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "${DOCKER_CMD}" = "podman" ]; then
    for override in docker-compose-podman-override.yml testenv-compose-podman-override.yml; do
        if [ -f "${SCRIPT_DIR}/${override}" ]; then
            COMPOSE_OVERRIDE="${COMPOSE_OVERRIDE} -f ${SCRIPT_DIR}/${override}"
        fi
    done
fi

# compose() wrapper — runs compose with auto-applied podman override
compose() {
    ${DOCKER_CMD} compose $COMPOSE_DEFAULTS $COMPOSE_OVERRIDE "$@"
}

# stats() wrapper — runs stats for both compose stacks
stats() {
    ${DOCKER_CMD} stats "$@"
}

# ─── Startup ─────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "=== Detailed Stress Test (Fine-Grained Metrics) ==="
echo "═══════════════════════════════════════════════════════════"
echo ""

if [[ "${DIRECT}" == "1" ]]; then
    # Direct mode: just start core services, no authnz needed
    echo "Starting core services (no authnz)..."
    compose down --remove-orphans 2>/dev/null || true
    compose up -d
    sleep 5
    compose restart amp-manager
    sleep 5
    
    if ! curl -sSf -o /dev/null "http://localhost:5555/nm/version" 2>/dev/null; then
        echo "ERROR: API on port 5555 not responding"
        exit 1
    fi
    echo "API available on port 5555 (direct mode)"
else
    # Authnz mode: full stack with authnz
    echo "Starting full stack with authnz..."
    compose down --remove-orphans 2>/dev/null || true
    compose up -d
    sleep 5
    compose restart amp-manager
    sleep 5
    
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
    
    if ! wait_for_url "http://localhost:${AUTHNZ_PORT}/" "authnz"; then exit 1; fi
    echo "authnz ready"

    # Fix htpasswd in the authnz container so test/welcome1 and admin/admin123 work.
    # Use compose exec (-T disables pseudo-tty so stdin can be piped) for Docker/Podman portability.
    printf 'test:$apr1$2zghinWB$72p5X2nRUcyVTrGOIq8dN/\\nadmin:$apr1$9ggw5TmZ$Gv36l7GlE8lP6zta9VySb.\\n' | \
        compose exec -T authnz sh -c "cat > /etc/httpd/conf/htpasswd"
    echo "htpasswd fixed"

    # Log in as both test and admin users
    curl -sS -c "$COOKIES_FILE" \
        -X POST "http://localhost:${AUTHNZ_PORT}/authn/dologin.html" \
        -d "httpd_username=test&httpd_password=welcome1&httpd_location=/" \
        -o /dev/null -w "%{http_code}" > /dev/null
    curl -sS -c "$ADMIN_COOKIES_FILE" \
        -X POST "http://localhost:${AUTHNZ_PORT}/authn/dologin.html" \
        -d "httpd_username=admin&httpd_password=admin123&httpd_location=/" \
        -o /dev/null -w "%{http_code}" > /dev/null
    echo "Logged in as test and admin users"
fi
echo ""

# ─── Phase A: Proxy Overhead Measurement ─────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "[Phase A] Proxy & network overhead measurement"
echo "═══════════════════════════════════════════════════════════"

python3 "${SCRIPT_DIR}/scripts/stress_proxy_overhead.py" \
    "${DIRECT}" "$COOKIES_FILE" "$METRICS_DIR" "$BASE_PORT"

echo ""

# ─── Phase B: Per-Endpoint Latency Breakdown ─────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase B] Per-endpoint latency breakdown (detailed)"
echo "═══════════════════════════════════════════════════════════"

python3 "${SCRIPT_DIR}/scripts/stress_endpoint_latency.py" \
    "${DIRECT}" "$COOKIES_FILE" "$ADMIN_COOKIES_FILE" "$METRICS_DIR" "$BASE_PORT"

echo ""

# ─── Phase C: OpenSearch Logging Latency ─────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase C] OpenSearch logging latency (per-logging-ops overhead)"
echo "═══════════════════════════════════════════════════════════"

python3 "${SCRIPT_DIR}/scripts/stress_logging_latency.py" \
    "${DIRECT}" "$COOKIES_FILE" "$METRICS_DIR" "$BASE_PORT"

echo ""

# ─── Phase D: Sustained Load with Resource Tracking ─────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase D] Sustained load + per-container resource tracking"
echo "═══════════════════════════════════════════════════════════"

TMP_RAW="$METRICS_DIR/container_stats_raw.txt"
echo "  Running 30s sustained load..."

# Start sustained load in background, wait for it to finish, then collect stats
python3 "${SCRIPT_DIR}/scripts/stress_sustained_load.py" \
    "${DIRECT}" "$COOKIES_FILE" "$BASE_PORT" &
LOAD_PID=$!

# Collect docker stats samples while load is running (and one after)
for i in $(seq 1 15); do
    stats --no-stream \
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

TMP_DIR="$METRICS_DIR" python3 "${SCRIPT_DIR}/scripts/stress_connection_pool.py" \
    "${DIRECT}" "$COOKIES_FILE" "$BASE_PORT"

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
        "http://localhost:${BASE_PORT}${endpoint}" 2>/dev/null || echo "N/A")
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

# Grafana is on port 3000 regardless of mode
GRAFANA_PORT=3000
python3 "${SCRIPT_DIR}/scripts/stress_grafana_path.py" \
    "${DIRECT}" "$COOKIES_FILE" "$GRAFANA_PORT"

echo ""

# ─── Phase H: Redis Session Key Analysis ─────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "[Phase H] Redis session performance"
echo "═══════════════════════════════════════════════════════════"

echo "  Checking Redis session backend..."
redis_ping=$(compose exec redis redis-cli ping 2>/dev/null || echo "N/A")
echo "    Redis ping: ${redis_ping}"

redis_info=$(compose exec redis redis-cli INFO memory 2>/dev/null || echo "N/A")
redis_mem=$(echo "$redis_info" | grep "used_memory_human" | cut -d: -f2 | tr -d '[:space:]')
echo "    Redis used memory: ${redis_mem}"

# Check Redis keys
echo ""
echo "  Redis key counts (top 10 by type):"
if [[ "${DIRECT}" == "1" ]]; then
    # In direct mode, Redis is still used for session by core app
    redis_keys=$(compose exec redis redis-cli KEYS "*" 2>/dev/null | head -20)
    if [ -z "$redis_keys" ]; then
        echo "    (no keys found)"
    else
        echo "$redis_keys" | while read key; do
            echo "    $key: $(compose exec redis redis-cli TYPE "$key" 2>/dev/null)"
        done
    fi
else
    redis_keys=$(compose exec redis redis-cli KEYS "*" 2>/dev/null | head -20)
    if [ -z "$redis_keys" ]; then
        echo "    (no keys found)"
    else
        echo "$redis_keys" | while read key; do
            echo "    $key: $(compose exec redis redis-cli TYPE "$key" 2>/dev/null)"
        done
    fi
fi

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
