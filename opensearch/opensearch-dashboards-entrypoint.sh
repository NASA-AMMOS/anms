#!/usr/bin/env bash
set -euo pipefail

DASHBOARDS_URL="http://0.0.0.0:5601"
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

until curl -sS \
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

    marker="${file}.imported"

    if [ -f "$marker" ]; then
      echo "Skipping already imported file: $file"
      continue
    fi

    echo "Importing saved objects from $file into tenant ${SECURITY_TENANT}..."

    curl -sS \
      -u "${DASHBOARDS_USER}:${DASHBOARDS_PASSWORD}" \
      -X POST "${DASHBOARDS_URL}/dashboards/api/saved_objects/_import?overwrite=true" \
      -H "osd-xsrf: true" \
      -H "securitytenant: global" \
      -F "file=@${file}"

    echo
    echo "Imported $file"

    # This marker only works if the import directory is writable.
    # If mounted read-only, import will still work but repeat on restart.
    touch "$marker" 2>/dev/null || true
  done
else
  echo "Import directory does not exist: $IMPORT_DIR"
fi

echo "OpenSearch Dashboards is running."

wait "$OSD_PID"