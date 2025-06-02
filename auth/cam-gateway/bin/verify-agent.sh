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
