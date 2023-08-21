#!/bin/bash
##
## Copyright (c) 2023 The Johns Hopkins University Applied Physics
## Laboratory LLC.
##
## This file is part of the Asynchronous Network Managment System (ANMS).
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

# Update yarn lockfiles from current package versions.
# On RHEL8 the prerequites are:
#  dnf -y module install nodejs:16
#  npm install --global yarn
#
set -e

SELFDIR=$(dirname "${BASH_SOURCE[0]}")

docker image build --tag yarn-base --target yarn-base ${SELFDIR}

mkdir -p "/home/${USER}/.cache/yarn"

for SUBNAME in server public
do
    docker run \
	   -v "/etc/group:/etc/group:ro" \
	   -v "/etc/passwd:/etc/passwd:ro" \
	   -v "/etc/shadow:/etc/shadow:ro" \
	   -u ${UID}:${GID} \
	   -v "/home/${USER}/.cache/yarn:/home/${USER}/.cache/yarn" \
	   -v "${SELFDIR}/${SUBNAME}:/usr/src/app" \
	   yarn-base bash -c "cd /usr/src/app && yarn install"
done
