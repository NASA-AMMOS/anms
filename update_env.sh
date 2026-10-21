#!/usr/bin/env bash
##
## Copyright (c) 2026 The Johns Hopkins University Applied Physics
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


# Copy example.env to .env if file doesn't already exist.
[[ -f .env ]] || cp example.env .env

# Add or update GIT_VERSION and GIT_DATE in .env file
GIT_VERSION="$(git describe --tags --always --dirty)"
GIT_DATE="$(git log -1 --format=%cI)"

if grep -q '^GIT_VERSION=' .env; then
    sed -i.bak "s|^GIT_VERSION=.*|GIT_VERSION=${GIT_VERSION}|" .env
else
    echo "GIT_VERSION=${GIT_VERSION}" >> .env
fi

if grep -q '^GIT_DATE=' .env; then
    sed -i.bak "s|^GIT_DATE=.*|GIT_DATE=${GIT_DATE}|" .env
else
    echo "GIT_DATE=${GIT_DATE}" >> .env
fi


source "$(dirname "$0")/gen_password.sh"

# Add OPENSEARCH_INITIAL_ADMIN_PASSWORD if missing.
if ! grep -q '^OPENSEARCH_INITIAL_ADMIN_PASSWORD=' .env; then
    password=$(generate_password)
    echo "OPENSEARCH_INITIAL_ADMIN_PASSWORD=${password}" >> .env
fi
