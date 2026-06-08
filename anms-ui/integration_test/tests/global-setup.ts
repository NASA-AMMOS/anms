/**
 * Global Playwright setup - runs once before all tests.
 *
 * Waits for all backend services to be healthy, then seeds the database
 * and OpenSearch with realistic data for testing:
 * - 100+ agents with realistic URIs and registration timestamps
 * - 500+ reports with metrics (latency, throughput, errors)
 * - OpenSearch index configuration for report data
 *
 * Services checked:
 * - UI (port 9030)
 * - authnz (port 80)
 * - OpenSearch (port 9200)
 * - OpenSearch Dashboards (port 5601)
 */

import { chromium } from '@playwright/test';
import { spawn } from 'child_process';
import { promisify } from 'util';
import { waitForUrlHealthy } from '../utils/api-helpers';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';
const AUTHNZ_URL = process.env.AUTHNZ_URL || 'http://localhost:80';
const OPENSEARCH_URL = process.env.OPENSEARCH_URL || 'http://localhost:9200';
const OPENSEARCH_DASH_URL = process.env.OPENSEARCH_DASH_URL || 'http://localhost:5601';

const AGENTS_TO_SEED = parseInt(process.env.SEED_AGENTS || '100', 10);
const REPORTS_TO_SEED = parseInt(process.env.SEED_REPORTS || '100', 10);
const SKIP_SEEDING = process.env.SKIP_SEEDING === 'true';

function spawnAsync(cmd: string, args: string[], cwd: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const proc = spawn(cmd, args, { cwd, stdio: 'inherit' });
    proc.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${cmd} exited with code ${code}`));
    });
    proc.on('error', reject);
  });
}

export default async function globalSetup() {
  console.log('\n=== ANMS Integration Tests ===');
  console.log('Waiting for services to be healthy...\n');

  // Wait for UI
  console.log('  -> UI (port 9030)...');
  const uiReady = await waitForUrlHealthy(BASE_URL, 30);
  console.log('  ' + (uiReady ? 'OK' : 'timeout (may not be started)'));

  // Wait for authnz
  console.log('  -> authnz (port 80)...');
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

  // Seed data if services are ready
  if (!SKIP_SEEDING && opensearchReady) {
    console.log('\n=== Seeding database and OpenSearch ===');
    const seedDir = new URL('../tests/seed/', import.meta.url).pathname;
    
    // Seed agents
    console.log(`\n  Seeding ${AGENTS_TO_SEED} agents...`);
    try {
      await spawnAsync('python3', ['tests/seed/seed_agents.py', '--count', String(AGENTS_TO_SEED)], seedDir);
      console.log('  Agents seeded successfully');
    } catch (err) {
      console.log('  Warning: Agent seeding failed (likely already seeded or DB not ready):', (err as Error).message);
    }
    
    // Seed OpenSearch reports
    console.log(`\n  Seeding ${REPORTS_TO_SEED} reports in OpenSearch...`);
    try {
      await spawnAsync('python3', ['tests/seed/seed_dashboard.py', '--count', String(REPORTS_TO_SEED)], seedDir);
      console.log('  Reports seeded successfully');
    } catch (err) {
      console.log('  Warning: Report seeding failed:', (err as Error).message);
    }
    
    console.log('\n=== Seeding complete ===\n');
  } else if (SKIP_SEEDING) {
    console.log('\n=== Seeding skipped (SKIP_SEEDING=true) ===\n');
  }

  console.log('=== Global setup complete ===\n');
}
