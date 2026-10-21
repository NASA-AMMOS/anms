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
set -euo pipefail

SECURITY_CONFIG_DIR="${SECURITY_CONFIG_DIR:-/usr/share/opensearch/config/opensearch-security}"
SECURITY_ADMIN_TOOL="${SECURITY_ADMIN_TOOL:-/usr/share/opensearch/plugins/opensearch-security/tools/securityadmin.sh}"

ROOT_CA="${ROOT_CA:-/usr/share/opensearch/config/root-ca.pem}"
ADMIN_CERT="${ADMIN_CERT:-/usr/share/opensearch/config/kirk.pem}"
ADMIN_KEY="${ADMIN_KEY:-/usr/share/opensearch/config/kirk-key.pem}"

SECURITY_ADMIN_RETRIES="${SECURITY_ADMIN_RETRIES:-60}"
SECURITY_ADMIN_SLEEP_SECONDS="${SECURITY_ADMIN_SLEEP_SECONDS:-5}"

ORIGINAL_ENTRYPOINT="${ORIGINAL_ENTRYPOINT:-/usr/share/opensearch/opensearch-docker-entrypoint.sh}"

echo "Starting OpenSearch..."

"$ORIGINAL_ENTRYPOINT" "$@" &
OPENSEARCH_PID="$!"

cleanup() {
  if kill -0 "$OPENSEARCH_PID" >/dev/null 2>&1; then
    kill "$OPENSEARCH_PID"
    wait "$OPENSEARCH_PID" || true
  fi
}

trap cleanup INT TERM

echo "Waiting for OpenSearch security plugin to become available..."

attempt=1
until "$SECURITY_ADMIN_TOOL" \
    -cd "$SECURITY_CONFIG_DIR" \
    -icl -nhnv \
    -cacert "$ROOT_CA" \
    -cert "$ADMIN_CERT" \
    -key "$ADMIN_KEY"; do

  if ! kill -0 "$OPENSEARCH_PID" >/dev/null 2>&1; then
    echo "OpenSearch exited before securityadmin.sh completed."
    wait "$OPENSEARCH_PID"
    exit 1
  fi

  if [ "$attempt" -ge "$SECURITY_ADMIN_RETRIES" ]; then
    echo "securityadmin.sh failed after ${SECURITY_ADMIN_RETRIES} attempts."
    cleanup
    exit 1
  fi

  echo "securityadmin.sh not ready yet. Attempt ${attempt}/${SECURITY_ADMIN_RETRIES}. Retrying in ${SECURITY_ADMIN_SLEEP_SECONDS}s..."
  attempt=$((attempt + 1))
  sleep "$SECURITY_ADMIN_SLEEP_SECONDS"
done

echo "OpenSearch security configuration applied."

wait "$OPENSEARCH_PID"