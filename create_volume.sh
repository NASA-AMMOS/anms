#!/usr/bin/env bash
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

# Construct and fill volumes needed by the ANMS compose config.
# Use:
#  ./create_volume {optional tls file source path}
#
set -e
set -x

# Full name of the volume
VOLNAME=ammos-tls
# Directory to which the volume is mounted, and from which files are copied
VOLPATH=/ammos/etc/pki/tls

SRCPATH=$1
if [ -z "${SRCPATH}" ]
then
    SRCPATH=$VOLPATH
elif [ ! -e "$SRCPATH" ]; then
    echo "Error: '$SRCPATH' does not exist."
    exit 1
fi


# Determine base command (docker or podman)
if [ -n "$DOCKER_CMD" ]; then
    echo "Using defined DOCKER_CMD=${DOCKER_CMD}"
elif command -v podman &> /dev/null; then
    echo "Podman is installed"
    DOCKER_CMD="podman"
    EXTRA_FLAGS="--ignore"
elif command -v docker &> /dev/null; then
    echo "Docker is installed"
    DOCKER_CMD="docker"
else
    echo "Neither Docker nor Podman is installed"
    exit 1
fi


${DOCKER_CMD} volume create ${EXTRA_FLAGS} ${VOLNAME}

# Delete our created volume if there is an error to prevent issues on retry
trap '${DOCKER_CMD} volume rm ${VOLNAME}' ERR

CTRNAME=$(${DOCKER_CMD} run --detach --rm \
          -v ${VOLNAME}:${VOLPATH} \
          docker.io/redhat/ubi9 tail -f /dev/null)

# Ensure container is stopped with script, even if there is an error
trap '${DOCKER_CMD} stop ${CTRNAME} >/dev/null' EXIT

${DOCKER_CMD} exec ${CTRNAME} rm -rf ${VOLPATH}/*
for FN in ${SRCPATH}/*
do
    echo "Copying from ${FN}"
    ${DOCKER_CMD} cp ${FN} ${CTRNAME}:${VOLPATH}/
done

# creating socket volume 
${DOCKER_CMD} volume create ${EXTRA_FLAGS} sockdir    
