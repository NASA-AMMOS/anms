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

# The yarn-base image is used by prep_packages script externally
FROM anms-base AS yarn-base
ENV NODE_OPTIONS=--use-openssl-ca

# Install System Level Dependencies
# Yarn cannot be installed via RPM because of FIPS-mode restrictions
RUN dnf -y  install  https://rpm.nodesource.com/pub_16.x/el/9/x86_64/nodesource-release-el9-1.noarch.rpm && \
    dnf -y  install nodejs && \
    dnf clean all && rm -rf /var/cache/yum && \
    npm install --global yarn && \
    yarn config set --global cafile ${PIP_CERT}


# Actual installation
FROM yarn-base AS anms-ui
ENV APP_WORK_DIR=/opt/node_app
ENV PM2_HOME=${APP_WORK_DIR}/.pm2

# Install NodeJS Global Dependencies
RUN --mount=type=cache,target=/root/.cache/yarn \
    yarn global add pm2 @vue/cli

# Remaining commands as this user
USER ${APP_USER}:${APP_USER}

# Install NodeJS Server Dependencies
COPY --chown=${APP_USER}:${APP_USER} server/package.json server/yarn.lock ${APP_WORK_DIR}/server/
RUN --mount=type=cache,uid=9999,gid=9999,target=/home/${APP_USER}/.cache/yarn \
    cd ${APP_WORK_DIR}/server && \
    yarn install --immutable --immutable-cache

# Install NodeJS UI Dependencies
COPY --chown=${APP_USER}:${APP_USER} public/package.json public/yarn.lock ${APP_WORK_DIR}/public/
RUN --mount=type=cache,uid=9999,gid=9999,target=/home/${APP_USER}/.cache/yarn \
    cd ${APP_WORK_DIR}/public && \
    yarn install --immutable --immutable-cache

# Build Backend/Frontend
# These copies do not overwrite node_modules
COPY --chown=${APP_USER}:${APP_USER} server ${APP_WORK_DIR}/server/
COPY --chown=${APP_USER}:${APP_USER} public ${APP_WORK_DIR}/public/
RUN --mount=type=cache,uid=9999,gid=9999,target=/home/${APP_USER}/.cache/yarn \
    cd ${APP_WORK_DIR}/public && \
    yarn run build && \
    rm -rf ${APP_WORK_DIR}/public/node_modules && \
    yarn install --immutable --immutable-cache --production


COPY --chmod=755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint
ENTRYPOINT ["docker-entrypoint"]

# Tune Final Settings
WORKDIR ${APP_WORK_DIR}
COPY --chown=${APP_USER}:${APP_USER} config.yaml process.yml config_ui_env.js data/ ${APP_WORK_DIR}

CMD ["pm2-docker", "process.yml", "--env", "production"]

HEALTHCHECK --start-period=10s --interval=60s --timeout=60s --retries=20 \
    CMD ["pm2", "pid", "anms"]

EXPOSE 9030
