/**
 * Global Playwright setup - runs once before all tests.
 *
 * Waits for all backend services to be healthy before tests run:
 * - UI (port 9030)
 * - authnz (port 8084)
 * - OpenSearch (port 9200)
 * - OpenSearch Dashboards (port 5601)
 *
 * Seeding is handled separately via seed scripts in tests/seed/
 */

import { waitForUrlHealthy } from '../utils/api-helpers';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';
const AUTHNZ_URL = process.env.AUTHNZ_URL || 'http://localhost:8084';
const OPENSEARCH_URL = process.env.OPENSEARCH_URL || 'http://localhost:9200';
const OPENSEARCH_DASH_URL = process.env.OPENSEARCH_DASH_URL || 'http://localhost:5601';

export default async function globalSetup() {
  console.log('\n=== ANMS Integration Tests ===');
  console.log('Waiting for services to be healthy...\n');

  // Wait for UI
  console.log('  -> UI (port 9030)...');
  const uiReady = await waitForUrlHealthy(BASE_URL, 30);
  console.log('  ' + (uiReady ? 'OK' : 'timeout (may not be started)'));

  // Wait for authnz
  console.log('  -> authnz (port 8084)...');
  const authnzReady = await waitForUrlHealthy(AUTHNZ_URL, 20);
  console.log('  ' + (authnzReady ? 'OK' : 'timeout (may not be started)'));

  // Wait for OpenSearch
  console.log('  -> OpenSearch (port 9200)...');
  const opensearchReady = await waitForUrlHealthy(OPENSEARCH_URL, 30);
  console.log('  ' + (opensearchReady ? 'OK' : 'timeout (may not be started)'));

  // Wait for OpenSearch Dashboards
  console.log('  -> OpenSearch Dashboards (port 5601)...');
  const dashReady = await waitForUrlHealthy(OPENSEARCH_DASH_URL, 20);
  console.log('  ' + (dashReady ? 'OK' : 'timeout (may not be started)'));

  console.log('\n=== Global setup complete ===\n');
}
