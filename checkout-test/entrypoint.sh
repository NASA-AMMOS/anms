#!/usr/bin/env bash
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

# Run similar to:
#  COMPOSE_PROFILES=full CHECKOUT_BASE_URL=https://authnz/ ./entrypoint.sh
set -e

export COMPOSE_PROFILES
export CHECKOUT_BASE_URL

SELFDIR=$(realpath $(dirname "${BASH_SOURCE[0]}"))
TIMELIMIT=30

CURLOPTS=""
if [ -n "${SSL_CERT_FILE}" ]
then
    echo "Using custom CA from ${SSL_CERT_FILE}"
    CURLOPTS="${CURLOPTS} --cacert ${SSL_CERT_FILE}"
fi

if [ -z "${CHECKOUT_BASE_URL}" ]; then
    echo "Must define CHECKOUT_BASE_URL environment"
    exit 1
fi
echo "Waiting for ${CHECKOUT_BASE_URL} to be available..."
for IX in $(seq ${TIMELIMIT}); do
    if curl -sSl $CURLOPTS "${CHECKOUT_BASE_URL}" >/dev/null; then
        break
    fi
    if [ ${IX} -eq ${TIMELIMIT} ]; then
        echo "No HTTP access after ${IX} seconds!"
        exit 1
    fi
    sleep 1
done
echo

echo "Running tests..."
TESTARGS="--verbose"
if [ -n "${XUNIT_OUTFILE}" ]; then
    TESTARGS="${TESTARGS} --junitxml=${XUNIT_OUTFILE}"
fi
python3 -m pytest ${TESTARGS} "${SELFDIR}" "$@"
