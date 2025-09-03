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
# DB_HOST referencing the DNS name of a PostgreSQL server
# DB_USERNAME and DB_PASSWORD for optional authentication
# DB_NAME for the database schema to use
#
FROM localhost/dtnma-acelib

ENV APP_WORK_DIR=/usr/src/anms-core

# Requirement of main module
COPY pyproject.toml ${APP_WORK_DIR}/
RUN cd ${APP_WORK_DIR} && \
    pip-compile --find-links ${PY_WHEEL_DIR} pyproject.toml && \
    ${PIP} install  --ignore-installed  -r requirements.txt
# Actual main package
COPY anms ${APP_WORK_DIR}/anms
RUN ${PIP} install ${APP_WORK_DIR}

RUN mkdir -p /usr/local/share/ace && \
    cp -R /usr/src/dtnma-adms /usr/local/share/ace/adms
COPY anms/agent_parameter.json /usr/local/share/anms/agent_parameter.json

RUN setcap cap_net_raw=ep /usr/bin/ping
COPY --chmod=755 docker-entrypoint.sh /usr/local/bin/
# Remaining commands as the local user
USER ${APP_USER}
CMD ["/usr/local/bin/docker-entrypoint.sh"]

HEALTHCHECK --start-period=10s --interval=60s --timeout=10s --retries=20 \
    CMD ["curl", "-sq", "-o/dev/null", "http://localhost:5555/hello"]
