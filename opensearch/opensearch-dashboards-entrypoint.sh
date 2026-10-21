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

DASHBOARDS_URL="${DASHBOARDS_URL:-http://127.0.0.1:5601}"
DASHBOARDS_USER="admin"
DASHBOARDS_PASSWORD="${OPENSEARCH_INITIAL_ADMIN_PASSWORD:-admin}"
SECURITY_TENANT="${SECURITY_TENANT:-global}"
IMPORT_DIR="/tmp/dashboards"

echo "Starting OpenSearch Dashboards..."

# Start the original OpenSearch Dashboards Docker launcher in the background.
opensearch-dashboards \
  --server.host="${SERVER_HOST:-0.0.0.0}" \
  --server.basePath="/dashboards" \
  --server.rewriteBasePath="true" \
  --opensearch.hosts="${OPENSEARCH_HOSTS:-[\"https://opensearch:9200\"]}" \
  --opensearch.ssl.verificationMode="${OPENSEARCH_SSL_VERIFICATIONMODE:-none}" \
  --opensearch.requestHeadersWhitelist="${OPENSEARCH_REQUESTHEADERSALLOWLIST:-[\"authorization\",\"securitytenant\"]}" \
  --opensearch_security.auth.anonymous_auth_enabled="${OPENSEARCH_SECURITY_AUTH_ANONYMOUS_AUTH_ENABLED:-true}" \
  --opensearch_security.multitenancy.enabled="${OPENSEARCH_SECURITY_MULTITENANCY_ENABLED:-true}" \
  --opensearch_security.multitenancy.tenants.enable_global="${OPENSEARCH_SECURITY_MULTITENANCY_TENANTS_ENABLE_GLOBAL:-true}" \
  --opensearch_security.multitenancy.tenants.enable_private="${OPENSEARCH_SECURITY_MULTITENANCY_TENANTS_ENABLE_PRIVATE:-false}" \
  --opensearch_security.multitenancy.tenants.preferred="${OPENSEARCH_SECURITY_MULTITENANCY_TENANTS_PREFERRED:-[\"Global\"]}" \
  --opensearch_security.readonly_mode.roles="${OPENSEARCH_SECURITY_READONLY_MODE_ROLES:-[\"kibana_read_only\",\"anonymous_dashboard_viewer\"]}" &
OSD_PID="$!"

echo "Waiting for OpenSearch Dashboards to become available..."

until curl --fail -sS \
  -u "${DASHBOARDS_USER}:${DASHBOARDS_PASSWORD}" \
  "${DASHBOARDS_URL}/dashboards/api/status" >/dev/null 2>&1; do
  sleep 5

  if ! kill -0 "$OSD_PID" >/dev/null 2>&1; then
    echo "OpenSearch Dashboards exited before becoming ready."
    wait "$OSD_PID"
    exit 1
  fi
done

echo "OpenSearch Dashboards is ready."

if [ -d "$IMPORT_DIR" ]; then
  for file in "$IMPORT_DIR"/*.ndjson; do
    [ -e "$file" ] || {
      echo "No .ndjson files found in $IMPORT_DIR"
      break
    }

    echo "Importing saved objects from $file into tenant ${SECURITY_TENANT}..."

    # Import on every startup: markers on the host can outlive the OpenSearch
    # data volume and incorrectly skip provisioning on a fresh deployment.
    # The import API can return HTTP 200 with success=false and object errors.
    # Use the Node runtime bundled with OpenSearch Dashboards to check the body.
    curl --fail -sS \
      -u "${DASHBOARDS_USER}:${DASHBOARDS_PASSWORD}" \
      -X POST "${DASHBOARDS_URL}/dashboards/api/saved_objects/_import?overwrite=true" \
      -H "osd-xsrf: true" \
      -H "securitytenant: ${SECURITY_TENANT}" \
      -F "file=@${file}" |
      /usr/share/opensearch-dashboards/node/bin/node -e '
      const fs = require("fs");
      const result = JSON.parse(fs.readFileSync(0, "utf8"));
      if (result.success !== true) {
        console.error("Saved-object import failed:", JSON.stringify(result));
        process.exit(1);
      }
      console.log(`Imported ${result.successCount} saved objects`);
    '

    echo "Imported $file"
  done
else
  echo "Import directory does not exist: $IMPORT_DIR"
fi

echo "OpenSearch Dashboards is running."

wait "$OSD_PID"
