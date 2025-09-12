#!/usr/bin/env bash
# ANMS Quick Start Script for first-time users
#
# WARNING: This script is NOT intended for usage in production environments.  See README and/or Product Guide for details.
#
# NOTE: If using podman, this script will automatically uncomment the
# #AUTHNZ_*PORT lines in .env to avoid permission issues binding to
# low-numbered default ports.
#
#
# ENV variables can be used to configure this script:
#
# DOCKER_CMD can be used to explicitly specify usage of DOCKER or
# PODMAN. If omitted, it will automatically detect which is installed
# (defaulting to Podman if both are present)
#
#   DOCKER_CMD=podman ./quickstart.sh
#
# USE_TESTENV specifies whether the sample testenv is automatically
# built and started. This is the default behavior. To disable, specify
#   USE_TESTEENV=n ./quickstart.sh
#
#
# USE_ALT_HTTP_PORT=[y|n] If 'y', or if using rootless podman and 'n'
# is not specified the #AUTHNZ_* lines in .env will be uncommented to
# use ports that do not require root permissions.
#
# Note: This script was created with assistance from openai/gpt-oss-120b
set -e

# Determine base command (docker or podman)
if [ -n "$DOCKER_CMD" ]; then
    echo "Using defined DOCKER_CMD=${DOCKER_CMD}"
elif command -v podman &> /dev/null; then
    echo "Podman is installed"
    DOCKER_CMD="podman"
elif command -v docker &> /dev/null; then
    echo "Docker is installed"
    DOCKER_CMD="docker"
else
    echo "Neither Docker nor Podman is installed"
    exit 1
fi

# If running rootless, update .env to avoid port binding errors
if [[ ${DOCKER_CMD:-} == podman ]]; then
    echo "Rootless ${DOCKER_CMD} → updating .env …"
    # ----------------------------------------------------------------
    # 3️⃣  In‑place edit: strip the leading “#” only on lines that
    #     begin with "#AUTHNZ_".  All other lines stay untouched.
    # ----------------------------------------------------------------
    #   - ^#AUTHNZ_   → matches a line whose first character is # followed
    #                    by the literal string AUTHNZ_
    #   - s/^#//      → replace the first # with nothing (i.e. delete it)
    #
    #   GNU sed (Linux/macOS‑brew) supports -i without an extension.
    #   For macOS *without* GNU‑sed you need: sed -i '' … 
    # ----------------------------------------------------------------
    if sed --version >/dev/null 2>&1; then   # GNU‑sed test (Linux, most BSDs with gsed)
        sed -i '/^#AUTHNZ_/ s/^#//' .env
    else                                     # macOS/BSD “sed -i” needs an empty backup suffix
        sed -i '' '/^#AUTHNZ_/ s/^#//' .env
    fi    
fi

# Set profiles to full in .env file for easy use
if sed --version >/dev/null 2>&1; then   # GNU‑sed test (Linux, most BSDs with gsed)
    sed -i '/^#COMPOSE_PROFILES/ s/^#//' .env
else                                     # macOS/BSD “sed -i” needs an empty backup suffix
    sed -i '' '/^#COMPOSE_PROFILES/ s/^#//' .env
fi    

# Load env variables (after we've made any tweaks for test configuration)
source .env

# Disable Security Labels for simplified quick start setup
# TODO: Can we verify if this is necessary? ie: If security_opt labels are used by system, have not been defined, and we cannot define them as part of this quickstart
cp docker-compose.no-security-override.yml docker-compose.override.yml

# Create default volumes
./create_volume.sh ./puppet/modules/apl_test/files/anms/tls

# Build system
${DOCKER_CMD} compose build

# Start testenv (unless disabled)
if [[ ${USE_TESTENV:-} != n ]]; then
    ${DOCKER_CMD} compose -f testenv-compose.yml up -d
fi

# Start ANMS
${DOCKER_CMD} compose up -d

echo "ANMS Startup Complete (Quickstart Demo Mode)"
echo "  WARNING: This startup procedure is NOT intended for usage on production systems"

# Echo complete and usage tips
echo "------------------"
echo " Startup complete. "
echo "-------------------"
echo "   Reminder: This quick start procedure is intended for test and demo purposes only."
echo "ANMS Documentation can be found in the README (https://github.com/NASA-AMMOS/anms/) and Guides (https://nasa-ammos.github.io/anms-docs/)"
echo "ANMS-CORE REST API reference can be found at http://localhost:${ANMS_CORE_HTTP_PORT}"
echo "Adminer (for DB inspection) can be found at http://localhost:${ADMINER_PORT}"
echo "Primary UI can be accessed at http://localhost:${AUTHNZ_PORT} "
echo ""
echo " Note: It my take a minute for all services to complete startup. Run '${DOCKER_CMD} compose ps' to see container status"
echo " To shutdown, run '${DOCKER_CMD} compose -f docker-compose.yml -f testenv-compose.yml down'"
echo " To restart later, run '${DOCKER_CMD} compose -f testenv-compose.yml up -d' and '${DOCKER_CMD} compose up -d'"
echo ""
