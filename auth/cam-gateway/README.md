# CAM-Gateway

This Git repo consists a Dockerfile, httpd config files, CAM web agent, and setup scripts.

The Dockerfile is used to create the docker image of the 5.1.0 CAM Gateway.
The image contains:
- Redhat ubi9 (Universal Base Image 9)
- Apache httpd 2.4
- CAM web agent 5.9.1
- CAM Gateway setup scripts

The docker image can be built by the command

```
docker build . -t cam-gateway
```

The docker container is configured with environment variables.  

The following example shows how the container is run:

```
docker run -d --rm -p 443:443 \
  --name cam-gateway \
  -v /ammos/etc/pki/tls:/ammos/etc/pki/tls:ro \
  -e CAM_SERVER_URL=https://asec-dev-vm20.jpl.nasa.gov:443/cam \
  -e CAM_ADMIN_USER=testuser3399 \
  -e CAM_ADMIN_PASSWORD=<admin-password> \
  -e AGENT_NAME=gw-`hostname -s` \
  -e AGENT_PASSWORD=<agent-password> \
  -e CAM_GW_URL=https://`hostname -f`:443/ \
  -e PROXY_URLS="https://asec-dev-vm22.jpl.nasa.gov:8443/demoicmd https://asec-dev-vm22.jpl.nasa.gov:8443/demoserver https://asec-dev-vm23.jpl.nasa.gov/demoweb" \
  -e NOT_ENFORCED_URLS="https://asec-dev-vm22.jpl.nasa.gov:443/favicon.ico https://asec-dev-vm22.jpl.nasa.gov:443/demoserver/*" \
  cam-gateway
```

When the docker container starts, it runs the bin/run-cam-gateway.sh script.
The script will
- configure the httpd proxy
- delete the AGENT\_NAME agent profile at the CAM Server, if exists
- register the agent at the CAM Server (i.e. create an agent profile)
- run agentadmin to configure the agent
- start httpd

Once the container is stopped, it will be deleted.  Remove the "--rm" option in the docker run command above to prevent that from occuring.

## TLS/SSL
The TLS key/certificate files can be mounted as a volume (as shown above with the -v option), or provided as environment variables where that would be preferable.  TLSKEY and TLSCERT can be used to share the data for the key/cert files, and TLSCHAIN can be used optionally to confer the TLS certificate chain if necessary.

When using the environment variables, remove the volume mount (-v /ammos/etc/pki/tls:/ammos/etc/pki/tls:ro) and add the following definitions to the command above, after the NOT_ENFORCED_URLS definition:

```
-e TLSKEY=`cat /path/to/tls_key.pem` \
-e TLSCERT=`cat /path/to/tls_cert.pem` \
-e TLSCHAIN=`cat /path/to/tls_chain.pem` \
```

## Proxy Pass Configuration
The `PROXY_URLS` environment variable typically forwards requests from the path to the full URI. Note that the order of URIs in the env variable matters. The most general should be last in the list (e.g. '/').
```
PROXY_URLS="http://host/endpoint http://host2"
```
Resolves to the following proxy pass config
```
"/endpoint" "http://host/endpoint"
"/"         "http://host2/"
```

If you would like to use a custom proxy path to redirect to a given URL, preceed the URL with the desired endpoint
```
PROXY_URLS="api,http://myapihost admin,http://myadminhost/v1 http://webuihost ui/,http://myuihost/"
```
Resolves to the following proxy pass config
```
"/api"   "http://myapihost"
"/admin" "http://myadminhost/v1"
"/"       "http://webuihost/"
"/ui/"    "http://myuihost/"
```
If the agent profile needs additional attributes, they can be added to the optional AGENT_EXTRA_CONFIG parameter, e.g.
```
AGENT_EXTRA_CONFIG="ssoOnlyMode":"true","fqdnCheck"="true"
```
The list of agent profile attributes can be found in the Java and Web agent profiles under /ammos/cam-server/setup/data/setup/data/config on the CAM Server host.  However, not all the attributes are supported by the Agent Management CAM API.
