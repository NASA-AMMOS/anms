#!/bin/sh
# Construct and fill volumes needed by the ANMS compose config.
# Use:
#  ./create_volume {optional tls file source path}
#
set -e

# Full name of the volume
VOLNAME=ammos-tls
# Directory to which the volume is mounted, and from which files are copied
VOLPATH=/ammos/etc/pki/tls

SRCPATH=$1
if [ -z "${SRCPATH}" ]
then
    SRCPATH=$VOLPATH
fi

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


${DOCKER_CMD} volume create ${VOLNAME}
CTRNAME=$(${DOCKER_CMD} run --detach --rm \
		 -v ${VOLNAME}:${VOLPATH} -it \
		 docker.io/redhat/ubi9 tail -f /dev/null)

${DOCKER_CMD} exec ${CTRNAME} rm -rf ${VOLPATH}/*
for FN in ${SRCPATH}/*
do
    echo "Copying from ${FN}"
    ${DOCKER_CMD} cp ${FN} ${CTRNAME}:${VOLPATH}/
done

${DOCKER_CMD} stop ${CTRNAME} >/dev/null
