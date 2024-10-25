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
set -e

# Default creation permission is 777
umask 000


ORIGFILE="/opt/node_app/config_ui_env.js"
OUTFILE="/opt/node_app/release/assets/scripts/config_env.js"

TMPFILE=$(mktemp)
VITE_UI_VERSION=$ENV_UI_VERSION
sed "s/VITE_UI_VERSION_TEMPLATE/$VITE_UI_VERSION/" "${ORIGFILE}" > $OUTFILE

# update for hostnames and ports
sed -i "s/CORE_HOSTNAME_PLACEHOLDER/${ANMS_CORE_NAME:-anms-core}/" "/opt/node_app/config.yaml"
sed -i "s/CORE_PORT_PLACEHOLDER/${ANMS_CORE_HTTP_PORT:-5555}/" "/opt/node_app/config.yaml"
sed -i "s/REDIS_HOSTNAME_PLACEHOLDER/${REDIS_NAME:-redis}/" "/opt/node_app/config.yaml"
sed -i "s/REDIS_PORT_PLACEHOLDER/${REDIS_PORT:-6379}/" "/opt/node_app/config.yaml"

exec "$@"
