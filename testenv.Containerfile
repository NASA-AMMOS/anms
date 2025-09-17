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

RUN dnf install -y epel-release && \
    crb enable
RUN dnf install -y \
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


# ION and REFDA images
FROM reftools-buildenv-base AS reftools-buildenv-ion

RUN dnf install -y \
        patch autoconf libtool

COPY deps/dtnma-tools/deps/ion /usr/local/src/nm/deps/ion
COPY deps/dtnma-tools/deps/ion*.patch /usr/local/src/nm/deps/
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

# Install under /usr/local and keep build artifacts for debuginfo
COPY deps/dtnma-tools/deps /usr/local/src/nm/deps
COPY deps/dtnma-tools/cmake /usr/local/src/nm/cmake
COPY deps/dtnma-tools/src /usr/local/src/nm/src
COPY deps/dtnma-tools/CMakeLists.txt /usr/local/src/nm/
RUN cd /usr/local/src/nm && \
    cmake -S . -B build/default \
      -DCMAKE_BUILD_TYPE=Debug \
      -DBUILD_MANAGER=OFF \
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


# This image uses systemd init process to manage local services.
# Derived image targets choose which servies are enabled.
#
FROM registry.access.redhat.com/ubi9/ubi-init:9.2 AS testenv-init

# Optional APL network configuration from
# https://aplprod.servicenowservices.com/sp?id=kb_article&sys_id=c0de6fe91b83d85071b143bae54bcb34
RUN ( \
      curl -sL http://apllinuxdepot.jhuapl.edu/linux/APL-root-cert/JHUAPL-MS-Root-CA-05-21-2038-B64-text.cer -o /etc/pki/ca-trust/source/anchors/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt && \
      update-ca-trust && \
      echo "Root CA added" \
    ) || true
ENV PIP_CERT=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
ENV PIP_DEFAULT_TIMEOUT=300
RUN dnf -y install container-tools
# Container service config
RUN systemctl disable dnf-makecache.timer

COPY --chmod=755 deps/dtnma-tools/systemd/service_is_running.sh /usr/local/bin/service_is_running

# Image for the test environment manager transport with ION node and the
# ion-app-proxy daemon
#
FROM testenv-init AS ion-manager

COPY --from=reftools-buildenv-ion /usr/local /usr/local
RUN echo "/usr/local/lib64" >>/etc/ld.so.conf.d/local.conf && \
    echo "/usr/local/lib" >>/etc/ld.so.conf.d/local.conf && \
    ldconfig

# Systemd services
COPY deps/dtnma-tools/integration-test-ion/tmpfiles.conf /etc/tmpfiles.d/ion.conf
COPY --chmod=644 deps/dtnma-tools/systemd/ion.service deps/dtnma-tools/systemd/ion-app-proxy.service deps/dtnma-tools/systemd/bpecho@.service \
    /usr/local/lib/systemd/system/
RUN systemctl enable ion bpecho@4 ion-app-proxy && \
    mkdir -p /var/run/ion

# Runtime config for this container
COPY deps/dtnma-tools/integration-test-ion/node-*.rc /etc/ion/
COPY deps/test-ion-configs/mgr.rc etc/ion/

# CMD is systemd init
EXPOSE 1113/udp
EXPOSE 4556/udp

HEALTHCHECK --start-period=10s --interval=30s --timeout=5s --retries=5 \
    CMD ["service_is_running", "ion", "ion-app-proxy"]


# Image for the test environment Agents with ION node and REFDA
#
FROM testenv-init AS ion-agent

COPY --from=reftools-buildenv-ion /usr/local /usr/local
RUN echo "/usr/local/lib64" >>/etc/ld.so.conf.d/local.conf && \
    echo "/usr/local/lib" >>/etc/ld.so.conf.d/local.conf && \
    ldconfig

# Systemd services
COPY deps/dtnma-tools/integration-test-ion/tmpfiles.conf /etc/tmpfiles.d/ion.conf
COPY --chmod=644 deps/dtnma-tools/systemd/ion.service deps/dtnma-tools/systemd/refda-ion.service deps/dtnma-tools/systemd/bpecho@.service \
    /usr/local/lib/systemd/system/
RUN systemctl enable ion bpecho@4 refda-ion && \
    mkdir -p /var/run/ion

# Runtime config for this container
# COPY deps/dtnma-tools/integration-test-ion/node-*.rc /etc/ion/
COPY deps/test-ion-configs/agent-2.rc /etc/ion/node-2.rc
COPY deps/test-ion-configs/agent-3.rc /etc/ion/node-3.rc

# CMD is systemd init
EXPOSE 1113/udp
EXPOSE 4556/udp

HEALTHCHECK --start-period=10s --interval=30s --timeout=5s --retries=5 \
    CMD ["service_is_running", "ion", "refda-ion"]
