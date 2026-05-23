#!/bin/env bash

set -e

GITTAG=$(git describe --always --tags --dirty)
export ANMS_VERSION=${ANMS_VERSION:=${GITTAG}}
export DOCKER_IMAGE_TAG=${ANMS_VERSION}
OUTFILE="anms-${ANMS_VERSION}-images.tar.gz"

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

# Build or pull images needed
COMPOSE_OPTS="-f docker-compose.yml -f testenv-compose.yml --profile full --profile dev --parallel 1"
${COMPOSE_CMD} ${COMPOSE_OPTS} --podman-build-args='--format docker' build
${COMPOSE_CMD} ${COMPOSE_OPTS} pull

# Get List of Images used
IMAGES=$(${COMPOSE_CMD} ${COMPOSE_OPTS} config | grep --color=auto 'image:' | awk '{print $2}' | sort -u)
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

