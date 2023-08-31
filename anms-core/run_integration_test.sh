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

# Execute integration tests from a fresh container.
set -e

SELFDIR=$(dirname "${BASH_SOURCE[0]}")
# Parent path git branch
pushd "${SELFDIR}/.."
GITBRANCH=$(git rev-parse --abbrev-ref HEAD | sed 's/[^a-zA-Z0-9\-\._]/-/g')
popd

export DOCKER_BUILDKIT=${DOCKER_BUILDIT:=1}
export DOCKER_CTR_PREFIX=${DOCKER_CTR_PREFIX:=}
export DOCKER_IMAGE_PREFIX=${DOCKER_IMAGE_PREFIX:=}
export DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG:=${GITBRANCH}}

COMPOSE_OPTS="-f ${SELFDIR}/integration_test/docker-compose.yml -p test"
docker-compose ${COMPOSE_OPTS} build
docker-compose ${COMPOSE_OPTS} run test-fixture "$@"
