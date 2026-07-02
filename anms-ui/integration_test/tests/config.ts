/**
 * Shared test configuration — single source of truth for URLs and credentials.
 *
 * All integration test files should import from here instead of hardcoding
 * their own BASE_URL, AUTHNZ_URL, etc.
 */

// Authnz is the production-facing reverse proxy (handles auth + routing)
export const AUTHNZ_URL = process.env.AUTHNZ_URL || 'http://localhost:8084';

// OpenSearch runs on port 9200 (HTTPS)
export const OPENSEARCH_URL = process.env.OPENSEARCH_URL || 'https://localhost:9200';
export const OPENSEARCH_USER = process.env.OPENSEARCH_USER || 'admin';
export const OPENSEARCH_PASS = process.env.OPENSEARCH_PASS || 'Str0ng!Pass#2026';

// OpenSearch Dashboards runs on port 5601
export const OPENSEARCH_DASH_URL = process.env.OPENSEARCH_DASH_URL || 'http://localhost:5601';

// Grafana runs on port 3000
export const GRAFANA_URL = process.env.GRAFANA_URL || 'http://localhost:3000';

// Test credentials
export const TEST_USERNAME = process.env.TEST_USERNAME || 'test';
export const TEST_PASSWORD = process.env.TEST_PASSWORD || 'test';
