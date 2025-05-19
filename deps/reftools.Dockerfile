##
## Copyright (c) 2023 The Johns Hopkins University Applied Physics
## Laboratory LLC.
##
## This file is part of the Delay-Tolerant Networking Management
## Architecture (DTNMA) Tools package.
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

FROM localhost/anms-init AS deps-base
RUN --mount=type=cache,target=/var/cache/yum \
    dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm
RUN --mount=type=cache,target=/var/cache/yum \
    dnf config-manager --set-enabled crb
RUN --mount=type=cache,target=/var/cache/yum \
    dnf install -y epel-release
RUN --mount=type=cache,target=/var/cache/yum \
    dnf install -y  \
    patch \
    cmake ninja-build \
    ruby rsync git \
    systemd systemd-sysv \
    libpq-devel \
    make gcc gcc-c++ \
    libpq-devel civetweb-devel cjson-devel\ 
    gdb less  flex libfl-static

COPY dtnma-tools/deps/QCBOR /usr/local/src/dtnma-tools/deps/QCBOR
RUN cd /usr/local/src/dtnma-tools/deps/QCBOR && \
    make -j$(nproc) && \
    make install && \
    make -j$(nproc) clean

COPY dtnma-tools/deps/mlib /usr/local/src/dtnma-tools/deps/mlib
RUN cd /usr/local/src/dtnma-tools/deps/mlib && \
    make -j$(nproc) && \
    make install && \
    make -j$(nproc) clean

COPY dtnma-tools/deps/timespec /usr/src/nm/deps/timespec
COPY dtnma-tools/deps/timespec-CMakeLists.txt /usr/src/nm/deps/timespec/CMakeLists.txt
RUN cd /usr/src/nm/deps/timespec && \
    cmake -S . -B build \
      -DCMAKE_BUILD_TYPE=Debug && \
    cmake --build build && \
    cmake --install build && \
    ldconfig && \
    rm -rf build


# Helper utilities
RUN --mount=type=cache,target=/var/cache/yum \
    dnf install -y \
    python3 python3-pip \
    gcc python3-devel systemd-devel
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install systemd-python

COPY --chmod=755 dtnma-tools/systemd/service_is_running.sh /usr/local/bin/service_is_running


# Additional ION library install
FROM deps-base AS ion-base
RUN --mount=type=cache,target=/var/cache/yum \
    dnf install -y  \
    autoconf libtool \
    patch autoconf libtool \
    perl-CPAN && \
    PERL_MM_USE_DEFAULT=1 cpan -T JSON REST::Client Expect File::Slurp

COPY dtnma-tools/deps/ion /usr/local/src/dtnma-tools/deps/ion
COPY dtnma-tools/deps/ion*.patch /usr/local/src/dtnma-tools/deps
RUN cd /usr/local/src/dtnma-tools/deps/ion && \
    patch -p1 <../ion-4.1.2-remove-nm.patch && \
    patch -p1 <../ion-4.1.2-local-deliver.patch && \
    patch -p1 <../ion-4.1.2-private-headers.patch && \
    autoreconf -vif && \
    ./configure \
        --prefix=/usr/local --libdir=/usr/local/lib64 && \
    make -j$(nproc) && \
    make install && \
    echo /usr/local/lib64 > /etc/ld.so.conf.d/local.conf && \
    ldconfig 

# Systemd services
# COPY dtnma-tools/systemd/tmpfiles.conf /etc/tmpfiles.d/ion.conf
COPY --chmod=644 dtnma-tools/systemd/ion.service dtnma-tools/systemd/ref*-ion.service dtnma-tools/systemd/bpecho@.service  dtnma-tools/systemd/dumpcap.service /usr/local/lib/systemd/system/
# COPY --chmod=644 dtnma-tools/systemd/ion-stats.timer /usr/local/lib/systemd/system/
RUN systemctl enable ion bpecho@4


# Proxy-isolated manager, no ION
FROM deps-base AS amp-manager

COPY dtnma-tools/deps /usr/local/src/dtnma-tools/deps
COPY dtnma-tools/cmake /usr/local/src/dtnma-tools/cmake
COPY dtnma-tools/src /usr/local/src/dtnma-tools/src
COPY dtnma-tools/test /usr/local/src/dtnma-tools/test
COPY dtnma-tools/CMakeLists.txt /usr/local/src/dtnma-tools/
RUN cd /usr/local/src/dtnma-tools && \
    cmake -S . -B build/default \
    -DCMAKE_BUILD_TYPE=Debug \
    -DBUILD_AGENT=OFF -DBUILD_MANAGER=ON -DBUILD_PROXY=OFF -DTRANSPORT_PROXY_SOCKET=ON -DTRANSPORT_ION_BP=OFF \
    -DBUILD_TESTING=OFF \
    -G Ninja && \
    cmake --build build/default && \
    cmake --install build/default 

COPY --chmod=644 dtnma-tools/systemd/nm-mgr-proxy.service /usr/local/lib/systemd/system/
RUN systemctl enable nm-mgr-proxy && \
    mkdir -p /var/run/ion

HEALTHCHECK --start-period=10s --interval=30s --timeout=5s --retries=5 \
    CMD ["service_is_running", "nm-mgr-proxy"]


# ION and app proxy
FROM ion-base AS ion-manager

# Agent to test
COPY dtnma-tools/deps /usr/local/src/dtnma-tools/deps
COPY dtnma-tools/cmake /usr/local/src/dtnma-tools/cmake
COPY dtnma-tools/src /usr/local/src/dtnma-tools/src
COPY dtnma-tools/test /usr/local/src/dtnma-tools/test
COPY dtnma-tools/CMakeLists.txt /usr/local/src/dtnma-tools/
RUN cd /usr/local/src/dtnma-tools && \
    cmake -S . -B build/default \
    -DCMAKE_BUILD_TYPE=Debug \
    -DBUILD_AGENT=ON -DBUILD_MANAGER=OFF -DBUILD_PROXY=ON -DTRANSPORT_PROXY_SOCKET=OFF -DTRANSPORT_ION_BP=ON \
    -DBUILD_TESTING=OFF \
    -G Ninja && \
    cmake --build build/default && \
    cmake --install build/default 

COPY test-ion-configs/mgr.rc /etc/ion/node-1.rc
COPY --chmod=644 dtnma-tools/systemd/ion-app-proxy.service dtnma-tools/systemd/ion-nm-agent.service /usr/local/lib/systemd/system/
RUN systemctl enable ion-app-proxy ion-nm-agent && \
    mkdir -p /var/run/ion

HEALTHCHECK --start-period=10s --interval=30s --timeout=5s --retries=5 \
    CMD ["service_is_running", "ion", "ion-app-proxy"]


# ION and direct agent
FROM ion-base AS ion-agent

# Agent to test
COPY dtnma-tools/deps /usr/local/src/dtnma-tools/deps
COPY dtnma-tools/cmake /usr/local/src/dtnma-tools/cmake
COPY dtnma-tools/src /usr/local/src/dtnma-tools/src
COPY dtnma-tools/test /usr/local/src/dtnma-tools/test
COPY dtnma-tools/CMakeLists.txt /usr/local/src/dtnma-tools/
RUN cd /usr/local/src/dtnma-tools && \
    cmake -S . -B build/default \
    -DCMAKE_BUILD_TYPE=Debug \
    -DBUILD_AGENT=ON -DBUILD_MANAGER=OFF -DBUILD_PROXY=OFF -DTRANSPORT_PROXY_SOCKET=OFF -DTRANSPORT_ION_BP=ON \
    -DBUILD_TESTING=OFF \
    -G Ninja && \
    cmake --build build/default && \
    cmake --install build/default 

    COPY test-ion-configs/agent-2.rc /etc/ion/node-2.rc
    COPY test-ion-configs/agent-3.rc /etc/ion/node-3.rc
COPY --chmod=644 dtnma-tools/systemd/ion-nm-agent.service /usr/local/lib/systemd/system/
RUN systemctl enable ion-nm-agent && \
    mkdir -p /var/run/ion

HEALTHCHECK --start-period=10s --interval=30s --timeout=5s --retries=5 \
    CMD ["service_is_running", "ion", "ion-nm-agent"]
