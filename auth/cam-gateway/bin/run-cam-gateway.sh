#
# CAM Gateway configuration script to be run when docker container starts
#

KEY=/ammos/etc/pki/tls/private/ammos-server-key.pem
CERT=/ammos/etc/pki/tls/certs/ammos-server-cert.pem
CA=/ammos/etc/pki/tls/certs/ammos-ca-bundle.crt

# Get TLS Key/Cert/Chain from ENV they don't exist (mounted volume)
if [ ! -r ${KEY} ]; then
  if [ ! -z "${TLSKEY}" ]; then
    echo "${TLSKEY}" > ${KEY}
    chmod 444 ${KEY}
  else
    echo "Key file not found ${KEY}"
    exit 1
  fi
fi

if [ ! -f ${CERT} ]; then
  if [ ! -z "${TLSCERT}" ]; then
    echo "${TLSCERT}" > ${CERT}
    echo "" >> ${CERT}
    chmod 444 ${CERT}

    if [ ! -z "${TLSCHAIN}" ]; then
      echo "${TLSCHAIN}" >> ${CERT}
    fi
  else
    echo "Cert file not found ${CERT}"
    exit 1
  fi
fi

# userid = uid=0(root) gid=0(root) groups=0(root)
#echo userid = `id`

# verify CAM_SERVER_URL environment variable
if [ -z "$CAM_SERVER_URL" ]; then
  echo ERROR: CAM_SERVER_URL is missing.
  exit 1
elif [[ "$CAM_SERVER_URL" == */ ]]; then
  # remove ending /
  CAM_SERVER_URL=${CAM_SERVER_URL::-1}
fi
if [[ "$CAM_SERVER_URL" != */cam ]]; then
  echo ERROR: CAM_SERVER_URL is not ended with /cam: $CAM_SERVER_URL
  exit 1
fi
# agentadmin needs URL to have port number 
if [[ "$CAM_SERVER_URL" != *443/cam ]]; then
  CAM_SERVER_URL=${CAM_SERVER_URL%/cam}:443/cam
fi

# verify CAM_GW_URL environment variable
if [ -z "$CAM_GW_URL" ]; then
  echo ERROR: CAM_GW_URL is missing.
  exit 1
elif [[ "$CAM_GW_URL" != *443/* ]]; then
  # insert port number as agentadmin needs it
  part1=${CAM_GW_URL#*https://}
  part2=`echo $part1 | cut -d'/' -f 1`
  part3=${part1#*/}
  CAM_GW_URL=https://$part2:443/$part3
fi

if [ -z "$CAM_ADMIN_USER" ]; then
  echo "ERROR: CAM_ADMIN_USER is missing."
  exit 1
fi
if [ -z "$CAM_ADMIN_PASSWORD" ]; then
  echo "ERROR: CAM_ADMIN_PASSWORD is missing."
  exit 1
fi

if [ -z "$AGENT_NAME" ]; then
  AGENT_NAME="gw-`hostname -i`"
  echo "INFO: AGENT_NAME is set to $AGENT_NAME"
fi
if [ -z "$AGENT_PASSWORD" ]; then
  echo "ERROR: AGENT_PASSWORD is missing."
  exit 1
fi

if [ -z "$PROXY_URLS" ]; then
  echo "ERROR: PROXY_URLS is missing."
  exit 1
fi

# check key and cert
if [ ! -r $KEY ]; then
  echo "ERROR: Server Key $KEY is not readable"
  exit 1
fi
if [ ! -r $CERT ]; then
  echo "ERROR: Server Cert $CERT is not readable"
  exit 1
fi
if [ ! -r $CA ]; then
  echo "ERROR: CA Bundle $CA is not readable"
  exit 1
fi

# register the agent at the CAM Server
/ammos/css/bin/register-agent.sh
if [ $? != 0 ]; then
  echo "ERROR: Failed to register agent profile"
  exit 1
fi

# configure the agent
echo "Configure the agent $AGENT_NAME"
echo $AGENT_PASSWORD > /tmp/password 
# chown -R apache:apache /ammos/css/agents/web_agents/apache24_agent
/ammos/css/agents/web_agents/apache24_agent/bin/agentadmin --s \
    /etc/httpd/conf/httpd.conf \
    "$CAM_SERVER_URL" \
    "$CAM_GW_URL" \
    "/" \
    "$AGENT_NAME" \
    /tmp/password \
    --changeOwner --acceptLicence

exit_code=$?

if [ $exit_code -ne 0 ]; then
    cat /ammos/css/agents/web_agents/apache24_agent/log/install*
    exit $exit_code
fi
rm /tmp/password

# Create httpd proxy configuration
echo "Create httpd proxy configuration"
AGENT_HOST=`echo ${CAM_GW_URL} | cut -f3 -d'/' | cut -f1 -d':'`
sed -i -e "s/__AGENT_NAME__/${AGENT_HOST}/" /etc/httpd/site.conf.d/ssl.conf

PROXY_CONFIG=/etc/httpd/site.conf.d/cam_gw_proxy.conf
echo "SSLProxyEngine on" > $PROXY_CONFIG
echo "ProxyRequests off" >> $PROXY_CONFIG
echo "ProxyPreserveHost on" >> $PROXY_CONFIG
echo "SSLProxyCheckPeerName off" >> $PROXY_CONFIG
echo "SSLProxyCACertificateFile $CA" >> $PROXY_CONFIG
echo "" >> $PROXY_CONFIG
for url in $PROXY_URLS; do
  if echo "$url" | grep -q ','; then
    # Used to redirect when the endpoint does not match the destination path
    endpoint=$(echo "$url" | cut -d, -f1)
    url=$(echo "$url" | cut -d, -f2)
  else
    endpoint=$(echo "$url" | cut -d/ -f4-)
    # ensures the slashes are consistent
    url="$(echo "$url" | cut -d/ -f1-3)/${endpoint}"
  fi
  echo "ProxyPass /$endpoint $url" >> $PROXY_CONFIG
  echo "ProxyPassReverse /$endpoint $url" >> $PROXY_CONFIG
done

# Start httpd
echo "Start httpd"
/usr/sbin/httpd -D FOREGROUND
# for debugging httpd if it exits
#while true; do sleep 1000; done
