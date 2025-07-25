##
## Copyright (c) 2011-2024 The Johns Hopkins University Applied Physics
## Laboratory LLC.
##
## This file is part of the Delay-Tolerant Networking Management
## Architecture (DTNMA) Tools package.
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy dtnma-tools/of the License at
##     http://www.apache.org/licenses/LICENSE-2.0
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
FROM ubuntu:24.04 AS systemd-base
ENV DEBIAN_FRONTEND="noninteractive"

# APL network configuration from
# https://aplprod.servicenowservices.com/sp?id=kb_article&sys_id=c0de6fe91b83d85071b143bae54bcb34
RUN apt-get update && apt-get install -y ca-certificates curl && \
    (curl -sL http://apllinuxdepot.jhuapl.edu/linux/APL-root-cert/JHUAPL-MS-Root-CA-05-21-2038-B64-text.cer -o /usr/local/share/ca-certificates/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt || true) && \
    update-ca-certificates
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt
ENV PIP_DEFAULT_TIMEOUT=300

# Distro upgrade for security patches
RUN apt-get update && apt-get upgrade -y

# Use systemd as top-level process
RUN apt-get update && apt-get install -y systemd systemd-sysv
RUN systemctl mask systemd-logind && \
    systemctl mask console-getty && \
    systemctl disable getty@tty1 && \
    systemctl disable apt-daily.timer apt-daily-upgrade.timer && \
    systemctl disable systemd-timesyncd && \
    systemctl disable systemd-networkd && \
    echo "MulticastDNS=no" >>/etc/systemd/resolved.conf
CMD [ "/sbin/init" ]

# Testing utilities
RUN apt-get update && apt-get install -y \
    net-tools iproute2 iputils-ping \
    lsof iftop gdb valgrind xxd socat jq ruby && \
    gem install cbor-diag


FROM ubuntu:24.04 AS deps-local

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake autoconf libtool && \
    echo "/usr/local/lib" >/etc/ld.so.conf.d/local.conf

COPY dtnma-tools/deps/ion /usr/local/src/nm/deps/ion
COPY dtnma-tools/deps/ion*.patch /usr/local/src/nm/deps/
RUN cd /usr/local/src/nm/deps/ion && \
    patch -p1 <../ion-4.1.2-remove-nm.patch && \
    patch -p1 <../ion-4.1.2-local-deliver.patch && \
    patch -p1 <../ion-4.1.2-private-headers.patch && \
    autoreconf -vif && \
    export CFLAGS="-std=gnu99" && \
    ./configure && \
    make -j$(nproc) && \
    make install && \
    make -j$(nproc) clean

COPY dtnma-tools/deps/QCBOR /usr/local/src/nm/deps/QCBOR
RUN cd /usr/local/src/nm/deps/QCBOR && \
    cmake -S . -B build \
      -DCMAKE_BUILD_TYPE=Debug \
      -DBUILD_SHARED_LIBS=YES && \
    cmake --build build && \
    cmake --install build && \
    ldconfig && \
    rm -rf build

COPY dtnma-tools/deps/mlib /usr/local/src/nm/deps/mlib
RUN cd /usr/local/src/nm/deps/mlib && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    make -j$(nproc) clean

COPY dtnma-tools/deps/timespec /usr/local/src/nm/deps/timespec
COPY dtnma-tools/deps/timespec-CMakeLists.txt /usr/local/src/nm/deps/timespec/CMakeLists.txt
RUN cd /usr/local/src/nm/deps/timespec && \
    cmake -S . -B build \
      -DCMAKE_BUILD_TYPE=Debug && \
    cmake --build build && \
    cmake --install build && \
    ldconfig && \
    rm -rf build


FROM systemd-base AS testenv
COPY --from=deps-local /usr/local /usr/local

# Helper utilities
RUN apt-get update && apt-get install -y \
    python3 python3-pip
COPY --chmod=755 dtnma-tools/systemd/service_is_running.sh /usr/local/bin/service_is_running

# Test tools
RUN apt-get update && apt-get install -y \
    curl git tshark postgresql-client

# REFDA and REFDM to test
RUN apt-get update && apt-get install -y \
    cmake ninja-build ruby pkg-config \
    flex libfl-dev bison libpcre2-dev libpq-dev civetweb libcivetweb-dev libssl-dev libcjson-dev libsystemd-dev
COPY dtnma-tools/deps /usr/local/src/nm/deps
COPY dtnma-tools/cmake /usr/local/src/nm/cmake
COPY dtnma-tools/src /usr/local/src/nm/src
COPY dtnma-tools/CMakeLists.txt /usr/local/src/nm/
RUN ls -lt /usr/local/src/nm/
RUN cd /usr/local/src/nm && \
    cmake -S . -B build/default \
      -DCMAKE_BUILD_TYPE=Debug \
      -DBUILD_ION_PROXY=ON \
      -DTRANSPORT_UNIX_SOCKET=OFF \
      -DTRANSPORT_PROXY_SOCKET=ON \
      -DTRANSPORT_ION_BP=ON \
      -DBUILD_TESTING=OFF \
      -DBUILD_DOCS_API=OFF -DBUILD_DOCS_MAN=OFF \
      -G Ninja && \
    cmake --build build/default && \
    cmake --install build/default && \
    ldconfig
# keep build artifacts for debuginfo


FROM testenv AS amp-manager

# Systemd services
COPY --chmod=644 dtnma-tools/systemd/refdm-proxy.service \
    /usr/local/lib/systemd/system/
RUN systemctl enable refdm-proxy

EXPOSE 8089/tcp

HEALTHCHECK --start-period=10s --interval=30s --timeout=5s --retries=5 \
    CMD ["service_is_running", "refdm-proxy"]


FROM testenv AS ion-manager

# Systemd services
COPY dtnma-tools/integration-test-ion/tmpfiles.conf /etc/tmpfiles.d/ion.conf
COPY --chmod=644 dtnma-tools/systemd/ion.service dtnma-tools/systemd/ion-app-proxy.service dtnma-tools/systemd/bpecho@.service dtnma-tools/systemd/dumpcap.service \
    /usr/local/lib/systemd/system/
RUN systemctl enable ion bpecho@4 ion-app-proxy dumpcap && \
    mkdir -p /var/run/ion

# Runtime config for this container
COPY dtnma-tools/integration-test-ion/node-*.rc /etc/ion/
COPY test-ion-configs/mgr.rc etc/ion/

EXPOSE 1113/udp
EXPOSE 4556/udp

HEALTHCHECK --start-period=10s --interval=30s --timeout=5s --retries=5 \
    CMD ["service_is_running", "ion", "ion-app-proxy"]


FROM testenv AS ion-agent

# Systemd services
COPY dtnma-tools/integration-test-ion/tmpfiles.conf /etc/tmpfiles.d/ion.conf
COPY --chmod=644 dtnma-tools/systemd/ion.service dtnma-tools/systemd/refda-ion.service dtnma-tools/systemd/bpecho@.service dtnma-tools/systemd/dumpcap.service \
    /usr/local/lib/systemd/system/
RUN systemctl enable ion bpecho@4 refda-ion dumpcap && \
    mkdir -p /var/run/ion
    
# Runtime config for this container
# COPY dtnma-tools/integration-test-ion/node-*.rc /etc/ion/
COPY test-ion-configs/agent-2.rc /etc/ion/node-2.rc
COPY test-ion-configs/agent-3.rc /etc/ion/node-3.rc
# COPY test-ion-configs/agent-2.rc etc/ion/
# COPY test-ion-configs/agent-3.rc etc/ion/

EXPOSE 1113/udp
EXPOSE 4556/udp

HEALTHCHECK --start-period=10s --interval=30s --timeout=5s --retries=5 \
    CMD ["service_is_running", "ion", "refda-ion"]
