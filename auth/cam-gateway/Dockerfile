# Dockerfile to create docker image for ASEC CAM Gateway

FROM redhat/ubi9

MAINTAINER "Kam Tso" <tso@jpl.nasa.gov>

# ----- optional internal CA -------------------------------------------------
ARG INTERNAL_CERT_URL           # <-- build‑time variable
RUN if [ -n "$INTERNAL_CERT_URL" ]; then \
        echo "🔐 Pulling internal root‑CA from $INTERNAL_CERT_URL …" && \
        curl -fsSL "$INTERNAL_CERT_URL" \
          -o /etc/pki/ca-trust/source/anchors/internal-root-ca.crt && \
        update-ca-trust && \
        echo "✅ Internal root CA added"; \
    else \
        echo "⚙️  INTERNAL_CERT_URL not set – skipping internal CA import"; \
    fi
# ---------------------------------------------------------------------------

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
