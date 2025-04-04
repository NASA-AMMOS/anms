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

# The runtime requires these environment variables:
# MQTT_HOST referencing the DNS name of the MQTT broker
# DB_URI referencing the sqlalchemy URI for the DNS name of a PostgreSQL server
#
FROM localhost/dtnma-acelib

ENV APP_WORK_DIR=/usr/src/aricodec

# Requirement of main package
COPY pyproject.toml ${APP_WORK_DIR}/
RUN --mount=type=cache,target=/root/.cache/pip \
    cd ${APP_WORK_DIR} && \
    mkdir src && \
    pip-compile --find-links ${PY_WHEEL_DIR} pyproject.toml -vv && \
    pip3 install -r requirements.txt
# Actual main package
COPY src ${APP_WORK_DIR}/src
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install ${APP_WORK_DIR}

COPY --chmod=755 docker-entrypoint.sh /root/docker-entrypoint.sh
#USER ${APP_USER}
ENV SQLALCHEMY_SILENCE_UBER_WARNING=1
CMD ["/root/docker-entrypoint.sh"]
