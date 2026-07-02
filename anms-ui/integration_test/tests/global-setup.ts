/**
 * Global Playwright setup - runs once before all tests.
 *
 * Waits for all backend services to be healthy before tests run:
 * - UI (port 9030)
 * - authnz (port 8084)
 * - anms-core via authnz (/nm/api/hello)
 * - amp-manager via authnz (/nm/api/version)
 * - OpenSearch (port 9200)
 * - OpenSearch Dashboards (port 5601)
 * - Grafana (port 3000)
 *
 * Then runs seed scripts to populate test data:
 * - seed_agents.py (registered agents in PostgreSQL)
 * - seed_dashboard.py (OpenSearch reports + Grafana config)
 */

import { execSync } from 'node:child_process';
import { waitForUrlHealthy } from '../utils/api-helpers';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';
const AUTHNZ_URL = process.env.AUTHNZ_URL || 'http://localhost:8084';
const OPENSEARCH_URL = process.env.OPENSEARCH_URL || 'http://localhost:9200';
const OPENSEARCH_DASH_URL = process.env.OPENSEARCH_DASH_URL || 'http://localhost:5601';
const GRAFANA_URL = process.env.GRAFANA_URL || 'http://localhost:3000';

/**
 * Run a seed script from the tests/seed/ directory.
 * Returns true if the script ran successfully.
 */
function runSeedScript(script: string, args: string[] = []): boolean {
  try {
    const scriptPath = `tests/seed/${script}`;
    execSync(`python3 ${scriptPath} ${args.join(' ')}`, {
      stdio: 'inherit',
      cwd: __dirname + '/..', // integration_test/
      timeout: 60000,
    });
    return true;
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.warn(`  ⚠ Seed script ${script} failed: ${msg}`);
    return false;
  }
}

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

  // Wait for anms-core (via authnz proxy)
  console.log('  -> anms-core (via /nm/api/hello)...');
  const coreReady = await waitForUrlHealthy(AUTHNZ_URL + '/nm/api/hello', 30);
  console.log('  ' + (coreReady ? 'OK' : 'timeout (may not be started)'));

  // Wait for amp-manager (via authnz proxy)
  console.log('  -> amp-manager (via /nm/api/version)...');
  const ampReady = await waitForUrlHealthy(AUTHNZ_URL + '/nm/api/version', 30);
  console.log('  ' + (ampReady ? 'OK' : 'timeout (may not be started)'));

  // Wait for OpenSearch
  console.log('  -> OpenSearch (port 9200)...');
  const opensearchReady = await waitForUrlHealthy(OPENSEARCH_URL, 30);
  console.log('  ' + (opensearchReady ? 'OK' : 'timeout (may not be started)'));

  // Wait for OpenSearch Dashboards
  console.log('  -> OpenSearch Dashboards (port 5601)...');
  const dashReady = await waitForUrlHealthy(OPENSEARCH_DASH_URL, 20);
  console.log('  ' + (dashReady ? 'OK' : 'timeout (may not be started)'));

  // Wait for Grafana
  console.log('  -> Grafana (port 3000)...');
  const grafanaReady = await waitForUrlHealthy(GRAFANA_URL, 30);
  console.log('  ' + (grafanaReady ? 'OK' : 'timeout (may not be started)'));

  // ─── Seed test data ─────────────────────────────────────────────────────
  console.log('\nSeeding test data...\n');

  const agentsSeeded = runSeedScript('seed_agents.py', ['--count', '100', '--reset']);
  const dashboardSeeded = runSeedScript('seed_dashboard.py', ['--count', '500', '--reset']);

  if (agentsSeeded && dashboardSeeded) {
    console.log('\n  ✓ All seed data loaded successfully');
  } else {
    console.log('\n  ⚠ Some seed scripts failed — tests may run with incomplete data');
  }

  console.log('\n=== Global setup complete ===\n');
}
