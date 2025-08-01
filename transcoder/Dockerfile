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
FROM localhost/dtnma-acelib

ENV APP_WORK_DIR=/opt/app


# Copy over all required content (source, data, etc.)
COPY --chown=${APP_USER}:${APP_USER} . ${APP_WORK_DIR}
# Install all python dependencies
RUN ${PIP} install -r ${APP_WORK_DIR}/requirements.txt

# Tune Final Settings
WORKDIR ${APP_WORK_DIR}

# Persist Docker Container
COPY --chmod=755 docker-entrypoint.sh /usr/local/bin/
# Remaining commands as this user
USER ${APP_USER}:${APP_USER}
CMD ["/usr/local/bin/docker-entrypoint.sh"]


