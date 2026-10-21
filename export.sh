#!/bin/env bash
##
## Copyright (c) 2026 The Johns Hopkins University Applied Physics
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

set -e

GIT_VERSION=$(git describe --always --tags --dirty)
export DOCKER_IMAGE_TAG=${GIT_VERSION}
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

