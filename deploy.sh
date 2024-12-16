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

DEPLOY_VOLS=1
BOLT_OPTS="--targets ${DEPLOY_TARGET} --user ${DOCKER_REGISTRY_USERNAME} --password ${DOCKER_REGISTRY_PASSWORD} --sudo-password ${DOCKER_REGISTRY_PASSWORD}"

./build.sh push
dnf install -y https://yum.puppet.com/puppet-release-el-9.noarch.rpm
dnf install -y https://yum.puppet.com/puppet-tools-release-el-9.noarch.rpm
dnf install -y puppet-agent-7.28.0-1.el9 puppet-bolt
update-alternatives --install /usr/bin/puppet puppet-agent /opt/puppetlabs/bin/puppet 10
chmod +t /tmp # workaround ruby need within prep.sh
./puppet/prep.sh
./puppet/apply_remote.sh ${BOLT_OPTS}
BOLT_PROJECT = puppet bolt ${BOLT_OPTS} command run 'docker exec ion-manager ion_ping_peers 1 2 3'
    #  *prep-install-python
pip3 install -r checkout-test/requirements.txt
CHECKOUT_BASE_URL=http://${DEPLOY_TARGET}/ ./checkout-test/run.sh