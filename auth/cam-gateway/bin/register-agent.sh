# 
# Register the agent at the CAM Server.
#

CA="--cacert /ammos/etc/pki/tls/certs/ammos-ca-bundle.crt"
CURL="curl --tlsv1.2 $CA -sS"
CAM_API="$CAM_SERVER_URL-api"
PATH=/ammos/css/bin:$PATH
echo "Base cmd: $CURL -X POST \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d \{\"username\":\"$CAM_ADMIN_USER\",\"password\":\"$CAM_ADMIN_PASSWORD\"\} \
  '$CAM_API/ssoToken?loginMethod=ldap'"

# Get the CAM Cookie Name and the admin user SSO Token
echo "Get CAM Cookie Name and the admin user SSO Token"
response=`$CURL -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d \{"username":"$CAM_ADMIN_USER","password":"$CAM_ADMIN_PASSWORD"\} \
  "$CAM_API/ssoToken?loginMethod=ldap"`
#echo Authentication response = $response
SSO_TOKEN=`echo $response | JSON.sh -b | grep ssoCookieValue | cut -d$'\t' -f 2 | tr -d '"'`
CAM_COOKIE_NAME=`echo $response | JSON.sh -b | grep ssoCookieName | cut -d$'\t' -f 2 | tr -d '"'`
if [ "$SSO_TOKEN" ]; then
  echo CAM Cookie Name = $CAM_COOKIE_NAME
  #echo SSO Token = $SSO_TOKEN
else
  echo ""
  echo "ERROR: Failed to obtain SSO Token: response = $response"
  exit 1
fi

# Generate data file for creating agent profile
echo "Generate data file for creating agent profile"
AGENT_DATA=/tmp/agent-profile.dat
NOT_ENFORCED_QUOTED="${NOT_ENFORCED_URLS// /\", \"}"
cat <<EOF > $AGENT_DATA
{
  "name": "$AGENT_NAME",
  "password": "$AGENT_PASSWORD",
  "agentUrl": "$CAM_GW_URL",
  "notEnforcedUrls": [
    "$NOT_ENFORCED_QUOTED"
EOF
if [ "$AGENT_EXTRA_CONFIG" ]; then
  echo "  ]," >> $AGENT_DATA
  echo "  $AGENT_EXTRA_CONFIG"
  echo "  $AGENT_EXTRA_CONFIG" >> $AGENT_DATA
else
  echo "  ]" >> $AGENT_DATA
fi
echo "}" >> $AGENT_DATA

# Delete existing agent profile at the CAM Server
echo "Delete agent profile $AGENT_NAME at the CAM Server (just in case it exists)"
response=`$CURL -X DELETE \
  -H "Accept: application/json" \
  -H "ssoToken: $SSO_TOKEN" \
  "$CAM_API/web-agent/$AGENT_NAME"`
echo $response > /tmp/agent-delete.out

# Register agent profile at the CAM Server
echo "Register agent profile $AGENT_NAME at the CAM Server"
response=`$CURL -X POST \
  -H "Content-Type: application/json" \
  -H "Accept-API-Version: resource=1.0" \
  -H "ssoToken: $SSO_TOKEN" \
  -d @$AGENT_DATA \
  "$CAM_API/web-agent"`
echo $response > /tmp/agent-register.out

# Remove $AGENT_DATA as it contains the agent password
rm $AGENT_DATA

# Invaldate the admin user SSO Token
echo "Invaldate the admin user SSO Token"
response=`$CURL -X DELETE \
  --header "Content-Type: application/json" \
  --header "Accept: application/json" \
  --data \{"ssoToken":"$SSO_TOKEN"\} \
  "$CAM_API/ssoToken?action=invalidate"`
