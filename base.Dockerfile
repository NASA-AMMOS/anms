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
