##
## Copyright (c) 2023 The Johns Hopkins University Applied Physics
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

# Configure an Apache HTTPd to perform cookie-based authentication and
# path-based authorization to emulate the JPL CAM client.
#
FROM registry.access.redhat.com/ubi9/ubi:9.2 AS anms-base

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
ENV PIP_DEFAULT_TIMEOUT=300

# Install Apache
RUN dnf -y install httpd-tools mod_ssl mod_session

# Update Apache Configuration
COPY httpd.conf /etc/httpd/conf/httpd.conf
COPY htpasswd /etc/httpd/conf/htpasswd
COPY html/ /var/www/html/
COPY run_proxy.sh /root/run_proxy.sh

RUN mkdir -p /etc/httpd/site.conf.d

# Start Apache
CMD ["/root/run_proxy.sh"]

EXPOSE 80
