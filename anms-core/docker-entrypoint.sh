#!/usr/bin/env sh
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

# Ensure local account $APP_USER has membership in docker socket group
set -e

SOCKFILE="/var/run/docker.sock"
if [ -e "$SOCKFILE" ]
then
    chmod g+rw "${SOCKFILE}"

    FILE_GID=$(stat -c '%g' "${SOCKFILE}")
    getent group ${FILE_GID} || groupadd -r -g ${FILE_GID} docker
    usermod -a -G ${FILE_GID} ${APP_USER}
fi

# initialize DB state
runuser -u ${APP_USER} -- python3 -m anms.init_adms

exec runuser -u ${APP_USER} -- python3 -m anms.run_gunicorn
