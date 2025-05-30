# Dockerfile to create docker image for ASEC CAM Gateway

FROM redhat/ubi9

MAINTAINER "Kam Tso" <tso@jpl.nasa.gov>

# Optional APL network configuration from
# https://aplprod.servicenowservices.com/sp?id=kb_article&sys_id=c0de6fe91b83d85071b143bae54bcb34
RUN ( \
      curl -sL http://apllinuxdepot.jhuapl.edu/linux/APL-root-cert/JHUAPL-MS-Root-CA-05-21-2038-B64-text.cer -o /etc/pki/ca-trust/source/anchors/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt && \
      update-ca-trust && \
      echo "Root CA added" \
    ) || true
ENV PIP_CERT=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem

RUN yum install -y httpd mod_ssl procps-ng

COPY httpd /etc/httpd
COPY bin /ammos/css/bin

RUN mkdir -p /ammos/css/agents/web_agents/apache24_agent/instances
COPY --chown=apache:apache web_agents /ammos/css/agents/web_agents
RUN chmod 2770 /ammos/css/agents/web_agents/apache24_agent/instances

RUN mkdir -p /ammos/etc/pki/tls/{private,certs}
COPY --chmod=444 files/ammos-ca-bundle.crt /ammos/etc/pki/tls/certs/

WORKDIR /ammos/css/bin
CMD /ammos/css/bin/run-cam-gateway.sh
