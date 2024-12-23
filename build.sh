#!/bin/bash
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
# Environment parameters:
#  AUTHNZ_EMU set to 0 or 1 to enable the CAM Gateway emulator, which defaults to 0
#  DOCKER_IMAGE_TAG set to the tag suffix for generated images, which defaults to the current branch name
#
set -e

AUTHNZ_EMU=${AUTHNZ_EMU:=0}

GITTAG=$(git describe --always --tags --dirty)
GITBRANCH=$(git rev-parse --abbrev-ref HEAD | sed 's/[^a-zA-Z0-9\-\._]/-/g')

# Used by docker compose during up
export ANMS_VERSION=${ANMS_VERSION:=${GITTAG}}
export ANMS_GW_FQDN=$(hostname -f)

mkdir -p grafana/plugins
mkdir -p anms-ui/data

echo "Running image build"
declare -A BASEIMGS=(
    [anms-base]=". -f base.Dockerfile --target anms-base"
    [anms-init]=". -f base.Dockerfile --target anms-init"
    [dtnma-acelib]=". -f base.Dockerfile --target dtnma-acelib"
)
declare -A IMAGES=(
    [authnz]=""
    [anms-nginx]="nginx"
    [mqtt-broker]="mqtt-broker"
    [transcoder]="transcoder"
    [aricodec]="aricodec"
    [anms-ui]="anms-ui"
    [anms-core]="anms-core"
    [amp-sql]="amp-sql"
    [grafana]="grafana"
    [ion-manager]="ion --target ion-manager"
    [ion-agent]="ion --target ion-agent"
)
if [ $AUTHNZ_EMU -ne 0 ]
then
    IMAGES[authnz]="authnz-emu"
else
    IMAGES[authnz]="cam-gateway"
fi
export DOCKER_BUILDKIT=${DOCKER_BUILDIT:=1}
export DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG:=${GITBRANCH}}
for IMGNAME in "${!BASEIMGS[@]}"; do
    BUILDOPTS=${BASEIMGS[$IMGNAME]}
    docker image build -t "${IMGNAME}" ${BUILDOPTS}
done
for IMGNAME in "${!IMAGES[@]}"; do
    BUILDOPTS=${IMAGES[$IMGNAME]}
    echo "Building ${DOCKER_IMAGE_PREFIX}${IMGNAME}:${DOCKER_IMAGE_TAG} from ${BUILDOPTS} ..."
    docker image build -t "${DOCKER_IMAGE_PREFIX}${IMGNAME}:${DOCKER_IMAGE_TAG}" ${BUILDOPTS}
done
if [ "$1" = "buildonly" ]
then
    exit 0
elif [ "$1" = "tar" ]
then
    IMGLIST=""
    for IMGNAME in "${!IMAGES[@]}"; do
        IMGLIST="${IMGLIST} ${DOCKER_IMAGE_PREFIX}${IMGNAME}:${DOCKER_IMAGE_TAG}"
    done
    # Images not built but part of the compose config
    IMGLIST="${IMGLIST} opensearchproject/opensearch:2.0.0"
    IMGLIST="${IMGLIST} opensearchproject/opensearch-dashboards:2.0.0"
    IMGLIST="${IMGLIST} grafana/grafana-image-renderer:3.6.1"
    IMGLIST="${IMGLIST} redis:6.0-alpine"
    IMGLIST="${IMGLIST} adminer:latest"
    OUTFILE="anms-${ANMS_VERSION}-images.tar.gz"
    echo "Saving images to ${OUTFILE} from ${IMGLIST}"
    docker save ${IMGLIST} | gzip -c >${OUTFILE} 
    exit 0
elif [ "$1" = "push" ]
then
    for IMGNAME in "${!IMAGES[@]}"; do
        docker image push "${DOCKER_IMAGE_PREFIX}${IMGNAME}:${DOCKER_IMAGE_TAG}"
    done
    exit 0
fi

echo "Running docker-compose up"
ANMS_COMPOSE_OPTS="-f docker-compose.yml -p anms"
AGENT_COMPOSE_OPTS="-f agent-compose.yml -p agents"
for OPTS_NAME in ANMS_COMPOSE_OPTS AGENT_COMPOSE_OPTS; do
    docker compose ${!OPTS_NAME} up --detach
done

if true; then
    # Restart ducts to cache DNS name resolution after containers are up
    for CTR in ion-manager ion-agent2 ion-agent3; do
        docker exec ${CTR} ion_restart_ducts
    done
fi

if [ "$1" = "check" ]
then
    # The longest "--start-period" of all container HEALTHCHECK
    sleep 10

    TMPFILE=$(mktemp)
    for OPTS_NAME in ANMS_COMPOSE_OPTS AGENT_COMPOSE_OPTS; do
    for BADSTATUS in stopped restarting; do
            docker compose ${!OPTS_NAME} ps --services --filter status=${BADSTATUS} | tee -a "${TMPFILE}"
    done
    done
    # Show hints at what may be wrong
    for SERVNAME in $(cat "${TMPFILE}"); do
        docker logs --tail 50 ${SERVNAME}
    done
    # Fail if any names are in the file
    ! grep '[^[:space:]]' "${TMPFILE}"
    rm "${TMPFILE}"

    # ION connectivity test
    docker exec ion-manager ion_ping_peers 1 2 3
fi

# If 'tar' was passed as a cmd line argument, stop the containers and tar up the images
if [ "$1" = "tar" ]
then

    echo "Sleeping 60s to allow machines to come up"
    sleep 60

    echo "Stopping machines"
    docker stop $(docker ps -q)

else
    echo "The following containers are now running: "
    docker ps
fi

echo "------- Done -------"
