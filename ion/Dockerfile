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

FROM anms-init AS ion-base

# Dependencies for NM Mgr tests/dotest
RUN dnf -y install \
    cmake ninja-build \
    ruby rsync  \
    patch autoconf libtool \
    make gcc gcc-c++ libpq-devel \
    perl-CPAN \
    gdb less && \
    dnf clean all && rm -rf /var/cache/yum && \
    PERL_MM_USE_DEFAULT=1 cpan -T JSON REST::Client Expect File::Slurp

# Build from added source
# COPY src *.patch /usr/src/ion-ios/
# RUN cd /usr/src/ion-ios && \
    # patch -p1 <ion-4.1.1-anms-db.patch && \
    # patch -p1 <ion-4.1.2-local-deliver.patch && \
    # patch -p1 <ion-4.1.1-amp-filestructure.patch && \
    # patch -p1 <dtnma-tools-nm_rest.patch && \
    # autoreconf -vif && \
    # ./prep.sh &&\
    # ./build.sh install 
    # ./configure --with-postgresql --enable-nmrest && \
    # make -j$(nproc) && \
    # make install && \
    # ldconfig && \
    # rm -rf /usr/src/ion-ios
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

COPY src  /usr/src/ion-ios/
RUN cd /usr/src/ion-ios && \
    # ./build.sh install 
    cmake -S . -B build/default \
      -DCMAKE_BUILD_TYPE=Debug \
      -G Ninja && \
    cmake --build build/default && \
    cmake --install build/default

RUN dnf -y install \
    python3 python3-pip \
    gcc python3-devel systemd-devel && \
    dnf clean all && rm -rf /var/cache/yum && \
    pip3 install systemd-python
COPY --chmod=755 utils/ion_nm_wrap.py /usr/local/bin/ion_nm_wrap
COPY --chmod=755 utils/service_is_running.sh /usr/local/bin/service_is_running
COPY --chmod=755 utils/ion_restart_ducts.sh /usr/local/bin/ion_restart_ducts
COPY --chmod=755 utils/ion_ping_peers.sh /usr/local/bin/ion_ping_peers

# Service configuration
COPY tmpfiles.conf /etc/tmpfiles.d/ion.conf
COPY --chmod=644 systemd/ion.service systemd/ion-stats.service systemd/bpecho@.service /usr/local/lib/systemd/system/
COPY --chmod=644 systemd/ion-stats.timer /usr/local/lib/systemd/system/
RUN systemctl enable ion bpecho@4

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
