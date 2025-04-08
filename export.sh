#!/bin/env bash

set -e

GITTAG=$(git describe --always --tags --dirty)
ANMS_VERSION=${ANMS_VERSION:=${GITTAG}}
OUTFILE="anms-${ANMS_VERSION}-images.tar.gz"

# Get List of Images
if command -v podman-compose &> /dev/null; then
    COMPOSE_CMD="podman-compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "Neither docker-compose nor podman-compose is installed"
    exit 1
fi

IMAGES=$(${COMPOSE_CMD} -f docker-compose.yml -f agent-compose.yml config | grep --color=auto 'image:' | awk '{print $2}' | sort -u | less)
echo "${COMPOSE_CMD} reports the following images: ${IMAGES}"

# Determine base command (docker or podman)
if command -v podman &> /dev/null; then
    echo "Exporting via Podman"
    podman image save -m -o ${OUTFILE} ${IMAGES}
elif command -v docker &> /dev/null; then
    echo "Exporting via Docker"
    docker image save -o ${OUTFILE} ${IMAGES}
else
    echo "Neither Docker nor Podman is installed"
    exit 1
fi

