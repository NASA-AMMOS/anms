#!/usr/bin/env bash
##
## Copyright (c) 2023 The Johns Hopkins University Applied Physics
## Laboratory LLC.
##
## This file is part of the Asynchronous Network Management System (ANMS).
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##     http://www.apache.org/licenses/LICENSE-2.0
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## This work was performed for the Jet Propulsion Laboratory, California
## Institute of Technology, sponsored by the United States Government under
## the prime contract 80NM0018D0004 between the Caltech and NASA under
## subcontract 1658085.
##

# start-integration-tests.sh — automatically detect docker vs podman,
# start the appropriate stack with the correct override, then run Playwright tests.
#
# Usage:
#   ./start-integration-tests.sh              # full stack, docker (default)
#   ./start-integration-tests.sh testenv      # lightweight testenv mode
#   DOCKER_CMD=podman ./start-integration-tests.sh   # force podman

set -euo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-full}"

# ─── Detect container runtime ──────────────────────────────────────────────
if [ -n "${DOCKER_CMD:-}" ]; then
    echo "Using DOCKER_CMD=${DOCKER_CMD}"
elif command -v docker &> /dev/null; then
    DOCKER_CMD="docker"
    echo "Detected: docker"
elif command -v podman &> /dev/null; then
    DOCKER_CMD="podman"
    echo "Detected: podman"
else
    echo "ERROR: Neither docker nor podman is installed" >&2
    exit 1
fi

# ─── Select compose file ──────────────────────────────────────────────────
if [ "$MODE" = "testenv" ]; then
    COMPOSE_FILE="docker-compose-testenv.yml"
    PLAYWRIGHT_COMPOSE="docker-compose-testenv.yml"
else
    COMPOSE_FILE="docker-compose-full.yml"
    PLAYWRIGHT_COMPOSE="docker-compose-full.yml"
fi

echo "Mode: $MODE"
echo "Compose file: $COMPOSE_FILE"

# ─── Apply podman override ────────────────────────────────────────────────
COMPOSE_ARGS="-f ${COMPOSE_FILE}"
if [ "$DOCKER_CMD" = "podman" ]; then
    OVERRIDE="${COMPOSE_FILE%-*}-podman-override.yml"
    if [ -f "$TEST_DIR/$OVERRIDE" ]; then
        COMPOSE_ARGS="$COMPOSE_ARGS -f $TEST_DIR/$OVERRIDE"
        echo "Applied podman override: $OVERRIDE"
    else
        echo "WARNING: No podman override found for $COMPOSE_FILE" >&2
    fi
fi

# ─── Teardown any previous stack ─────────────────────────────────────────
echo ""
echo "Tearing down any previous stack..."
$DOCKER_CMD compose $COMPOSE_ARGS down --remove-orphans 2>/dev/null || true

# ─── Start services ───────────────────────────────────────────────────────
echo ""
echo "Starting services..."
$DOCKER_CMD compose $COMPOSE_ARGS up -d

# ─── Wait for services ───────────────────────────────────────────────────
echo ""
echo "Waiting for services to be healthy..."

wait_for_url() {
    local url="$1" desc="$2" timeout="${3:-30}"
    echo -n "  $desc... "
    for i in $(seq 1 "$timeout"); do
        if curl -sSf -o /dev/null "$url" 2>/dev/null; then
            echo "ok"; return 0
        fi
        sleep 1
    done
    echo "timeout (may not be running)"; return 1
}

if [ "$MODE" = "testenv" ]; then
    wait_for_url "http://localhost:9031" "anms-ui" 30
else
    wait_for_url "http://localhost:8084" "authnz" 30
    wait_for_url "http://localhost:9200" "opensearch" 60
    wait_for_url "http://localhost:3000" "grafana" 30
fi

# ─── Run Playwright tests ─────────────────────────────────────────────────
echo ""
echo "Running Playwright tests..."
export INTEGRATION_TEST_COMPOSE="$PLAYWRIGHT_COMPOSE"
cd "$TEST_DIR"
npx playwright test --reporter=list

echo ""
echo "Done. Teardown will happen automatically when Playwright finishes."
