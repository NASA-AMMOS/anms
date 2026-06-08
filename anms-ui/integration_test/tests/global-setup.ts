/**
 * Global Playwright setup - runs once before all tests.
 *
 * This fixture can be used to:
 * - Seed the database with test data
 * - Create test users
 * - Set up initial state
 *
 * Currently empty - the test environment should be fully initialized
 * via docker-compose before tests run. See README.md for usage.
 */

import { chromium } from '@playwright/test';

export default async function globalSetup() {
  console.log('\n╔══════════════════════════════════════════╗');
  console.log('║  ANMS Angular UI Integration Tests       ║');
  console.log('║  Global Setup                            ║');
  console.log('╚══════════════════════════════════════════╝');
  console.log('\nTest environment should be running:');
  console.log('  docker compose -f docker-compose-full.yml up -d');
  console.log('\nWaiting for UI to be healthy...\n');
}
