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

#
# Verify the agnet name and password
#
CURL="curl --tlsv1.2 -k -s"
CAM_JSON="$CAM_SERVER_URL/json"

response=`$CURL -X POST \
  -H "Content-Type: application/json" \
  -H "Accept-API-Version: resource=2.1" \
  -H "X-OpenAM-Username: $AGENT_NAME" \
  -H "X-OpenAM-Password: $AGENT_PASSWORD" \
  "$CAM_JSON/authenticate?authIndexType=module&authIndexValue=Application"`
if [[ $response != *tokenId* ]]; then
  echo "ERROR: Either agent $AGENT_NSME has not been registered or the agent password is wrong"
  exit 1
fi
