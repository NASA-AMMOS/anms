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
