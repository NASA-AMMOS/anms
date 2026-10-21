#!/bin/bash
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

# Iterate through a line-oriented file of ARIs and send them to an agent
#
set -e

AGENT_EID=$1
if ! shift 1
then
    echo "Usage: $0 [agent EID]" >/dev/stderr
    exit 1
fi

ACE="python3 -m ace.tools.ace_ari --log-level=warning --outform=cborhex --must-nickname"
CURL="curl --silent --show-error -XPUT -H \"Content-Type: text/plain\" --data-binary @- http://localhost:8089/nm/api/agents/eid/${AGENT_EID}/hex"

while IFS="" read -r LINE || [ -n "$LINE" ]
do
    echo "Sending ${LINE}"
    echo ${LINE} | eval $ACE | tr -d '[[:space:]]' | eval $CURL
    echo # ensure trailing newline
done
