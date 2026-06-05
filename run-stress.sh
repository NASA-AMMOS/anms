#!/usr/bin/env bash
# Run a stress-test script inside a resource-limited cgroup so it
# can't starve agent sessions.  Drop any stress-test script (or any
# other command) as arguments — it all gets cgroup-bound.
#
# Usage:
#   ./run-stress.sh ./stress-test-harder.sh       # normal run
#   ./run-stress.sh ./stress-test.sh               # lighter run
#   ./run-stress.sh ./stress-test-harder.sh       # env overrides still work
#     HTTP_CONCURRENCY=100 ./run-stress.sh ./stress-test-harder.sh
#
# Hard limits:
#   CPU    — 200 % (2 cores) — leaves at least one core for the agent
#   Memory — 4 GB — kernel OOM-killer reclaims before containers starve
#   I/O    — weight 50 (out of 100) — idle-ish disk access

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Validate: need at least one command to run
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <stress-script> [args...]"
    echo "  e.g. $0 ./stress-test-harder.sh"
    echo "  e.g. PHASE5_DURATION=30 $0 ./stress-test-harder.sh"
    exit 1
fi

# Resolve the script path relative to this file's directory
CMD_PATH="$SCRIPT_DIR/$1"
shift

# Verify script exists and is executable
if [[ ! -f "$CMD_PATH" ]]; then
    echo "ERROR: script not found: $CMD_PATH"
    exit 1
fi

echo "=== Resource-limited stress test ==="
echo "  CGroup limits: CPU=200%, Memory=4G, I/O=weight 50"
echo "  Script: $CMD_PATH $@"
echo "  (Override with env vars before calling this script)"
echo ""

# systemd-run --scope runs in a transient scope unit.
# --wait waits for the scope to finish (like running the command directly).
# --setenv passes through all parent env vars.
exec systemd-run --scope \
    --setenv=DOCKER_CMD=docker \
    -p CPUQuota=200% \
    -p MemoryMax=4G \
    -p IOWeight=50 \
    "$CMD_PATH" "$@"
