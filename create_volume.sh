#!/usr/bin/env bash
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
elif command -v docker &> /dev/null; then
    echo "Docker is installed"
    DOCKER_CMD="docker"
else
    echo "Neither Docker nor Podman is installed"
    exit 1
fi


${DOCKER_CMD} volume create ${VOLNAME}

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
${DOCKER_CMD} volume create sockdir    
