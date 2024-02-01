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

docker volume create ${VOLNAME}
CTRNAME=$(docker run --detach --rm \
		 -v ${VOLNAME}:${VOLPATH} -it \
		 redhat/ubi9 tail -f /dev/null)

docker exec ${CTRNAME} rm -rf ${VOLPATH}/*
for FN in ${SRCPATH}/*
do
    echo "Copying from ${FN}"
    docker cp ${FN} ${CTRNAME}:${VOLPATH}/
done

docker stop ${CTRNAME} >/dev/null
