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
FROM anms-init AS systemd-base
ENV DEBIAN_FRONTEND="noninteractive"


# Use systemd as top-level process
RUN dnf install -y systemd systemd-sysv
# RUN systemctl mask systemd-logind && \
#     systemctl mask console-getty && \
#     systemctl disable getty@tty1 && \
#     systemctl disable apt-daily.timer apt-daily-upgrade.timer && \
#     systemctl disable systemd-timesyncd && \
#     systemctl disable systemd-networkd && \
#     echo "MulticastDNS=no" >>/etc/systemd/resolved.conf
# CMD [ "/sbin/init" ]

# Testing utilities
# RUN dnf install -y \
#     net-tools iproute2 iputils-ping \
#     lsof iftop gdb valgrind socat


FROM registry.access.redhat.com/ubi9/ubi:9.2 as deps-local
RUN ( \
      curl -sL http://apllinuxdepot.jhuapl.edu/linux/APL-root-cert/JHUAPL-MS-Root-CA-05-21-2038-B64-text.cer -o /etc/pki/ca-trust/source/anchors/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt && \
      update-ca-trust && \
      echo "Root CA added" \
    ) || true
ENV PIP_CERT=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
ENV PIP_DEFAULT_TIMEOUT=300

RUN dnf install -y \
    autoconf libtool \
    cmake ninja-build \
    ruby rsync  \
    systemd systemd-sysv \
    patch autoconf libtool \
    make gcc gcc-c++ libpq-devel \
    perl-CPAN \
    gdb less && \
    dnf clean all && rm -rf /var/cache/yum && \
    PERL_MM_USE_DEFAULT=1 cpan -T JSON REST::Client Expect File::Slurp
COPY src/deps/ion /usr/src/nm/deps/ion
COPY src/deps/ion*.patch /usr/src/nm/deps/
RUN cd /usr/src/nm/deps/ion && \
    patch -p1 <../ion-4.1.2-remove-nm.patch && \
    patch -p1 <../ion-4.1.2-local-deliver.patch && \
    patch -p1 <../ion-4.1.2-private-headers.patch && \
    autoreconf -vif && \
    ./configure && \
    make -j$(nproc) && \
    make install && \
    make -j$(nproc) clean

COPY src/deps/QCBOR /usr/src/nm/deps/QCBOR
COPY src/deps/qcbor*.patch /usr/src/nm/deps/
RUN cd /usr/src/nm/deps/QCBOR && \
    patch -p1 <../qcbor-install.patch && \
    patch -p2 <../qcbor-expose-private.patch && \
    make -j$(nproc) && \
    make install && \
    make -j$(nproc) clean

COPY src/deps/mlib /usr/src/nm/deps/mlib
RUN cd /usr/src/nm/deps/mlib && \
    make -j$(nproc) && \
    make install && \
    make -j$(nproc) clean


FROM systemd-base as ion-base
COPY --from=deps-local /usr/local /usr/local

RUN dnf install -y \
    autoconf libtool \
    cmake ninja-build \
    ruby rsync  \
    systemd systemd-sysv \
    patch autoconf libtool \
    make gcc gcc-c++ libpq-devel \
    perl-CPAN \
    gdb less && \
    dnf clean all && rm -rf /var/cache/yum && \
    PERL_MM_USE_DEFAULT=1 cpan -T JSON REST::Client Expect File::Slurp
    
# Helper utilities
RUN dnf install -y \
    python3 python3-pip \
    gcc systemd-devel pkg-config && \
    dnf clean all && rm -rf /var/cache/yum && \
    pip3 install --upgrade pip && \
    pip3 install systemd-python

# # Test tools
# RUN dnf install -y \
#     curl git && \
#     pip3 install git+https://github.com/NASA-AMMOS/anms-ace.git

# Agent to test
RUN dnf install -y \
    cmake ninja-build ruby \
    patch autoconf libtool make gcc gcc-c++ libpq-devel 
COPY src/deps /usr/src/nm/deps
COPY src/cmake /usr/src/nm/cmake
COPY src/src /usr/src/nm/src
COPY src/test /usr/src/nm/test
COPY src/CMakeLists.txt /usr/src/nm/
RUN ls -lt /usr/src/nm/
RUN cd /usr/src/nm && \
    cmake -S . -B build/default \
      -DCMAKE_BUILD_TYPE=Debug \
      -G Ninja && \
    cmake --build build/default && \
    cmake --install build/default

COPY --chmod=755 utils/ion_nm_wrap.py /usr/local/bin/ion_nm_wrap
COPY --chmod=755 utils/service_is_running.sh /usr/local/bin/service_is_running
COPY --chmod=755 utils/ion_restart_ducts.sh /usr/local/bin/ion_restart_ducts
COPY --chmod=755 utils/ion_ping_peers.sh /usr/local/bin/ion_ping_peers

# Systemd services
COPY tmpfiles.conf /etc/tmpfiles.d/ion.conf
COPY --chmod=644 systemd/ion.service systemd/ion-nm-*.service systemd/bpecho@.service /usr/local/lib/systemd/system/
RUN systemctl enable ion bpecho@4 ion-nm-mgr ion-nm-agent && \
    mkdir -p /var/run/ion

# Runtime config for this container
# COPY src/testenv/node-1.rc /etc/ion/
COPY src/adms /usr/local/share/ace/adms

FROM ion-base AS ion-manager
COPY configs/simple-2-node/mgr.rc /etc/ion.rc

COPY --chmod=644 systemd/ion-nm-mgr.service systemd/ion-nm-agent.service /usr/local/lib/systemd/system/
RUN systemctl enable ion-nm-mgr ion-nm-agent

HEALTHCHECK --start-period=10s --interval=30s --timeout=5s --retries=5 \
    CMD ["service_is_running", "ion", "ion-nm-mgr"]


FROM ion-base AS ion-agent
COPY configs/simple-2-node/agent.rc.in /etc/ion.rc

COPY --chmod=644 systemd/ion-nm-agent.service /usr/local/lib/systemd/system/
RUN systemctl enable ion-nm-agent

HEALTHCHECK --start-period=10s --interval=30s --timeout=5s --retries=5 \
    CMD ["service_is_running", "ion", "ion-nm-agent"]