#!/bin/bash
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
