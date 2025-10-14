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

# The base image is just RHEL-9 OS with configuration for all ANMS containers.
#
FROM registry.access.redhat.com/ubi9/ubi:9.2 AS anms-base

# Optional APL network configuration from
# https://aplprod.servicenowservices.com/sp?id=kb_article&sys_id=c0de6fe91b83d85071b143bae54bcb34
RUN ( \
      curl -sL http://apllinuxdepot.jhuapl.edu/linux/APL-root-cert/JHUAPL-MS-Root-CA-05-21-2038-B64-text.cer -o /etc/pki/ca-trust/source/anchors/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt && \
      update-ca-trust && \
      echo "Root CA added" \
    ) || true
ENV PIP_CERT=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
ENV PIP_DEFAULT_TIMEOUT=300

# Explicit User (top of file to avoid conflicts down the line with IDs)
ENV APP_USER=anms
RUN groupadd -r -g 9999 ${APP_USER} && \
    useradd -m -r -g ${APP_USER} -u 9999 ${APP_USER}

# This image includes common libraries used by the aricodec and anms-core
# containers.
# Sets environment:
#  PY_WHEEL_DIR to local PIP wheel search path
#
FROM anms-base AS dtnma-acelib


# Install System Level Dependencies
RUN --mount=type=cache,target=/var/cache/yum \
    dnf -y install gcc-c++ python-devel python3-pip python3-wheel python3-setuptools iputils && \
    pip3 install pip-tools

# Use specific OS python version
ENV PIP=pip3
ENV PYTHON=python3
# Submodules with dependencies
ENV PY_WHEEL_DIR=/usr/local/lib/wheels

RUN ${PIP} install --upgrade pip

COPY deps/dtnma-ace /usr/src/dtnma-ace
RUN ${PIP} -v wheel /usr/src/dtnma-ace -w ${PY_WHEEL_DIR} --no-deps

COPY deps/dtnma-camp /usr/src/dtnma-camp
RUN ${PIP} wheel /usr/src/dtnma-camp -w ${PY_WHEEL_DIR} --no-deps

COPY deps/dtnma-adms /usr/src/dtnma-adms


# This is a postgres stateful database with data definition startup SQL scripts
FROM postgres:14 AS anms-sql

COPY deps/anms_db_tables/*.sql /docker-entrypoint-initdb.d/
COPY deps/dtnma-tools/refdb-sql/postgres/Database_Scripts/*.sql /docker-entrypoint-initdb.d/

# This is used for testing, it is easier to delete the amp_agent after inserting it using adm_amp_agent.sql instead of removing the script since other scripts are also relying on amp_agent
# COPY postgres/Database_Scripts/Routines/amp_agent_delete.sql /docker-entrypoint-initdb.d/31-amp_agent_delete.sql

HEALTHCHECK --start-period=10s --interval=10s --timeout=5s --retries=5 \
    CMD ["pg_isready", "-U", "healthcheck"]


# The yarn-base image is used by prep_packages script externally
FROM anms-base AS yarn-base
ENV NODE_OPTIONS=--use-openssl-ca

# Install System Level Dependencies
# Yarn cannot be installed via RPM because of FIPS-mode restrictions
RUN --mount=type=cache,target=/var/cache/yum \
    dnf install -y https://rpm.nodesource.com/pub_16.x/el/9/x86_64/nodesource-release-el9-1.noarch.rpm && \
    dnf install -y nodejs && \
    npm install --ignore-scripts --global yarn && \
    yarn config set --global cafile ${PIP_CERT}


# Actual installation
FROM yarn-base AS anms-ui
ENV APP_WORK_DIR=/opt/node_app
ENV PM2_HOME=${APP_WORK_DIR}/.pm2

# Install NodeJS Global Dependencies
RUN --mount=type=cache,target=/root/.cache/yarn \
    yarn global --ignore-engines add pm2 @vue/cli

# Remaining commands as this user
USER ${APP_USER}:${APP_USER}

# Install NodeJS Server Dependencies
COPY --chown=${APP_USER}:${APP_USER} \
    anms-ui/server/package.json anms-ui/server/yarn.lock ${APP_WORK_DIR}/server/
RUN --mount=type=cache,uid=9999,gid=9999,target=/home/${APP_USER}/.cache/yarn \
    cd ${APP_WORK_DIR}/server && \
    yarn install --ignore-scripts --immutable --immutable-cache

# Install NodeJS UI Dependencies
COPY --chown=${APP_USER}:${APP_USER} \
    anms-ui/public/package.json anms-ui/public/yarn.lock ${APP_WORK_DIR}/public/
RUN --mount=type=cache,uid=9999,gid=9999,target=/home/${APP_USER}/.cache/yarn \
    cd ${APP_WORK_DIR}/public && \
    yarn install --ignore-scripts --immutable --immutable-cache

# Build Backend/Frontend
# These copies do not overwrite node_modules
COPY --chown=${APP_USER}:${APP_USER} anms-ui/server ${APP_WORK_DIR}/server/
COPY --chown=${APP_USER}:${APP_USER} anms-ui/public ${APP_WORK_DIR}/public/
RUN --mount=type=cache,uid=9999,gid=9999,target=/home/${APP_USER}/.cache/yarn \
    cd ${APP_WORK_DIR}/public && \
    yarn run build && \
    rm -rf ${APP_WORK_DIR}/public/node_modules && \
    yarn install --ignore-scripts --immutable --immutable-cache --production

COPY --chmod=755 anms-ui/docker-entrypoint.sh /usr/local/bin/docker-entrypoint
ENTRYPOINT ["docker-entrypoint"]

# Tune Final Settings
WORKDIR ${APP_WORK_DIR}

# NOTE: wildcard allows handling case when data directory has not been created locally
COPY --chown=${APP_USER}:${APP_USER} \
    anms-ui/config.yaml anms-ui/process.yml anms-ui/config_ui_env.js anms-ui/data* ${APP_WORK_DIR}

CMD ["pm2-docker", "process.yml", "--env", "production"]
EXPOSE 9030

HEALTHCHECK --start-period=10s --interval=60s --timeout=10s --retries=20 \
    CMD ["pm2", "pid", "anms"]


# Local grafana configuration
#
FROM docker.io/grafana/grafana:9.1.3 AS grafana

# Optional APL network configuration from
# https://aplprod.servicenowservices.com/sp?id=kb_article&sys_id=c0de6fe91b83d85071b143bae54bcb34
USER root
RUN ( \
      wget http://apllinuxdepot.jhuapl.edu/linux/APL-root-cert/JHUAPL-MS-Root-CA-05-21-2038-B64-text.cer -O /usr/local/share/ca-certificates/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt && \
      update-ca-certificates && \
      echo "Root CA added" \
    ) || true
USER grafana

COPY --chown=grafana grafana/grafana_vol /var/lib/grafana
COPY grafana/provisioning /etc/grafana/provisioning
COPY grafana/plugins /var/lib/grafana/plugins
COPY grafana/grafana.ini /etc/grafana/grafana.ini


# Embed configuration for the broker in the image
#
FROM docker.io/library/eclipse-mosquitto:2.0 AS mqtt-broker

COPY mqtt-broker/mosquitto.conf /mosquitto/config/mosquitto.conf

EXPOSE 1883

HEALTHCHECK --start-period=5s --interval=10s --timeout=1s --retries=5 \
    CMD ["mosquitto_sub", "-t", "$SYS/broker/version", "-C", "1"]


# Transcoder uses the local MQTT broker for all IPC
#
FROM dtnma-acelib AS transcoder

ENV APP_WORK_DIR=/opt/app

# Copy over all required content (source, data, etc.)
COPY --chown=${APP_USER}:${APP_USER} transcoder ${APP_WORK_DIR}
# Install all python dependencies
RUN ${PIP} install -r ${APP_WORK_DIR}/requirements.txt

# Tune Final Settings
WORKDIR ${APP_WORK_DIR}

# Persist Docker Container
COPY --chmod=755 transcoder/docker-entrypoint.sh /usr/local/bin/
# Remaining commands as this user
USER ${APP_USER}:${APP_USER}
CMD ["/usr/local/bin/docker-entrypoint.sh"]


# The runtime requires these environment variables:
# MQTT_HOST referencing the DNS name of the MQTT broker
# DB_URI referencing the sqlalchemy URI for the DNS name of a PostgreSQL server
#
FROM dtnma-acelib AS aricodec

ENV APP_WORK_DIR=/usr/local/src/aricodec

# Requirement of main package
COPY aricodec/pyproject.toml ${APP_WORK_DIR}/
RUN --mount=type=cache,target=/root/.cache/pip \
    cd ${APP_WORK_DIR} && \
    mkdir src && \
    pip-compile --find-links ${PY_WHEEL_DIR} pyproject.toml -vv && \
    ${PIP} install -r requirements.txt
# Actual main package
COPY aricodec/src ${APP_WORK_DIR}/src
RUN --mount=type=cache,target=/root/.cache/pip \
    ${PIP} install ${APP_WORK_DIR}

COPY --chmod=755 aricodec/docker-entrypoint.sh /usr/local/bin/
ENV SQLALCHEMY_SILENCE_UBER_WARNING=1
# Remaining commands as the local user
USER ${APP_USER}
CMD ["/usr/local/bin/docker-entrypoint.sh"]


# The runtime requires these environment variables:
# DB_HOST referencing the DNS name of a PostgreSQL server
# DB_USERNAME and DB_PASSWORD for optional authentication
# DB_NAME for the database schema to use
#
FROM dtnma-acelib AS anms-core

ENV APP_WORK_DIR=/usr/src/anms-core

# Requirement of main module
COPY anms-core/pyproject.toml ${APP_WORK_DIR}/
RUN cd ${APP_WORK_DIR} && \
    pip-compile --find-links ${PY_WHEEL_DIR} pyproject.toml && \
    ${PIP} install  --ignore-installed  -r requirements.txt
# Actual main package
COPY anms-core/anms ${APP_WORK_DIR}/anms
RUN ${PIP} install ${APP_WORK_DIR}

RUN mkdir -p /usr/local/share/ace && \
    cp -R /usr/src/dtnma-adms /usr/local/share/ace/adms
COPY anms-core/anms/agent_parameter.json /usr/local/share/anms/agent_parameter.json
RUN touch /usr/local/share/anms/alerts.json
RUN chmod go+w  /usr/local/share/anms/alerts.json

RUN setcap cap_net_raw=ep /usr/bin/ping
COPY --chmod=755 anms-core/docker-entrypoint.sh /usr/local/bin/
# Remaining commands as the local user
USER ${APP_USER}
CMD ["/usr/local/bin/docker-entrypoint.sh"]
EXPOSE 5555/tcp

HEALTHCHECK --start-period=10s --interval=60s --timeout=10s --retries=20 \
    CMD ["curl", "-sq", "-o/dev/null", "http://localhost:5555/hello"]

# for anms-core integration test
FROM yarn-base AS anms-core-integration

# Install node+yarn from upstream
RUN npm install --ignore-scripts -g newman

COPY anms-core/integration_test /root/
WORKDIR /root
CMD ["./run_test.sh"]


# Build on more permissive CentOS image
# Run on RHEL UBI image
FROM quay.io/centos/centos:stream9 AS reftools-buildenv-base

# Optional APL network configuration from
# https://aplprod.servicenowservices.com/sp?id=kb_article&sys_id=c0de6fe91b83d85071b143bae54bcb34
RUN ( \
      curl -sL http://apllinuxdepot.jhuapl.edu/linux/APL-root-cert/JHUAPL-MS-Root-CA-05-21-2038-B64-text.cer -o /etc/pki/ca-trust/source/anchors/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt && \
      update-ca-trust && \
      echo "Root CA added" \
    ) || true
ENV PIP_CERT=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
ENV PIP_DEFAULT_TIMEOUT=300


RUN --mount=type=cache,target=/var/cache/yum \
    dnf install -y epel-release && \
    crb enable
RUN --mount=type=cache,target=/var/cache/yum \
    dnf install -y \
        gcc g++ \
        cmake ninja-build ruby pkg-config \
        flex libfl-static bison pcre2-devel civetweb civetweb-devel openssl-devel cjson-devel libpq-devel systemd-devel && \
    echo "/usr/local/lib64" >/etc/ld.so.conf.d/local.conf && \
    ldconfig

COPY deps/dtnma-tools/deps/QCBOR /usr/local/src/nm/deps/QCBOR
RUN cd /usr/local/src/nm/deps/QCBOR && \
    cmake -S . -B build \
        -DCMAKE_BUILD_TYPE=Debug \
        -DBUILD_SHARED_LIBS=YES && \
    cmake --build build && \
    cmake --install build && \
    ldconfig && \
    rm -rf build

COPY deps/dtnma-tools/deps/mlib /usr/local/src/nm/deps/mlib
RUN cd /usr/local/src/nm/deps/mlib && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    make -j$(nproc) clean

COPY deps/dtnma-tools/deps/timespec /usr/local/src/nm/deps/timespec
COPY deps/dtnma-tools/deps/timespec-CMakeLists.txt /usr/local/src/nm/deps/timespec/CMakeLists.txt
RUN cd /usr/local/src/nm/deps/timespec && \
    cmake -S . -B build \
        -DCMAKE_BUILD_TYPE=Debug && \
    cmake --build build && \
    cmake --install build && \
    ldconfig && \
    rm -rf build


# REFDM only without ION
FROM reftools-buildenv-base AS reftools-buildenv-refdm

# Install under /usr/local and keep build artifacts for debuginfo
COPY deps/dtnma-tools/deps /usr/local/src/nm/deps
COPY deps/dtnma-tools/cmake /usr/local/src/nm/cmake
COPY deps/dtnma-tools/src /usr/local/src/nm/src
COPY deps/dtnma-tools/CMakeLists.txt /usr/local/src/nm/
RUN cd /usr/local/src/nm && \
    cmake -S . -B build/default \
      -DCMAKE_BUILD_TYPE=Debug \
      -DBUILD_AGENT=OFF \
      -DBUILD_ION_PROXY=OFF \
      -DTRANSPORT_UNIX_SOCKET=OFF \
      -DTRANSPORT_PROXY_SOCKET=ON \
      -DTRANSPORT_ION_BP=OFF \
      -DBUILD_UNITTEST=OFF \
      -DBUILD_DOCS_API=OFF -DBUILD_DOCS_MAN=OFF \
      -G Ninja && \
    cmake --build build/default && \
    cmake --install build/default && \
    ldconfig


# Runtime image for REFDM
FROM anms-base AS amp-manager

RUN --mount=type=cache,target=/var/cache/yum \
    dnf install -y https://download.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm && \
    crb enable && \
    dnf install -y \
        pcre2 civetweb openssl-libs cjson libpq

COPY --from=reftools-buildenv-refdm /usr/local /usr/local
RUN echo "/usr/local/lib64" >>/etc/ld.so.conf.d/local.conf && \
    ldconfig

CMD ["sh", "-c", "refdm-proxy -l ${DTNMA_LOGLEVEL} -a ${AMP_PROXY_SOCKET}"]
EXPOSE 8089/tcp

HEALTHCHECK --start-period=10s --interval=60s --timeout=60s --retries=20 \
    CMD ["curl", "-sq", "-o/dev/null", "http://localhost:8089/nm/api/"]
