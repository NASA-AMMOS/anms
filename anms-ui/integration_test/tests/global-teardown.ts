/**
 * Global Playwright teardown - runs once after all tests.
 *
 * Automatically tears down the test environment regardless of which compose
 * file and which container runtime (docker or podman) was used.
 *
 * Detects the compose file from the INTEGRATION_TEST_COMPOSE env var
 * (or the playwright config's testDir-based default) and the runtime from
 * DOCKER_CMD env var or by checking which binary is available.
 * Applies the podman override file automatically when using podman.
 */

import { execSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

function detectRuntime(): string {
  // 1. Check for explicit override
  if (process.env.DOCKER_CMD) {
    console.log(`  Using DOCKER_CMD=${process.env.DOCKER_CMD}`);
    return process.env.DOCKER_CMD;
  }

  // 2. Check for docker compose plugin availability
  const testDir = __dirname; // integration_test/tests/

  // Try docker first (most common)
  try {
    execSync('docker compose version', { stdio: 'ignore' });
    console.log('  Detected: docker');
    return 'docker';
  } catch {
    // docker not available
  }

  // Try podman compose
  try {
    execSync('podman compose version', { stdio: 'ignore' });
    console.log('  Detected: podman');
    return 'podman';
  } catch {
    // podman not available either
    console.log('  WARNING: neither docker nor podman found');
    return 'docker'; // fallback
  }
}

function getComposeFile(): string {
  // Check env var first
  const envCompose = process.env.INTEGRATION_TEST_COMPOSE;
  if (envCompose && envCompose.endsWith('.yml')) {
    console.log(`  Using compose file from env: ${envCompose}`);
    return envCompose;
  }

  // Check playwright config for the default
  const configPath = join(testDir, '..', 'playwright.config.ts');
  if (existsSync(configPath)) {
    // Default in playwright.config.ts is docker-compose-full.yml
    console.log('  Using default compose file: docker-compose-full.yml');
    return 'docker-compose-full.yml';
  }

  return 'docker-compose-full.yml';
}

function getPodmanOverride(composeFile: string): string | null {
  // Derive podman override filename: docker-compose-full.yml → docker-compose-full-podman-override.yml
  const base = composeFile.replace('.yml', '');
  const override = `${base}-podman-override.yml`;
  const overridePath = join(testDir, '..', override);

  if (existsSync(overridePath)) {
    return override;
  }
  return null;
}

export default function globalTeardown() {
  console.log('\n╔══════════════════════════════════════════════════╗');
  console.log('║  ANMS Angular UI Integration Tests               ║');
  console.log('║  Global Teardown                                 ║');
  console.log('╚══════════════════════════════════════════════════╝');

  const runtime = detectRuntime();
  const composeFile = getComposeFile();
  const testDir = __dirname;

  console.log(`  Compose file: ${composeFile}`);
  console.log(`  Runtime: ${runtime}`);

  const base = composeFile.replace('.yml', '');
  const cmdParts = [
    runtime,
    'compose',
    '-f',
    composeFile,
    'down',
    '--remove-orphans'
  ];

  // Auto-apply podman override when using podman
  const podmanOverride = runtime === 'podman' ? getPodmanOverride(composeFile) : null;
  if (podmanOverride) {
    cmdParts.push('-f');
    cmdParts.push(podmanOverride);
    console.log(`  Applying podman override: ${podmanOverride}`);
  }

  const cmd = cmdParts.join(' ');
  console.log(`  Running: ${cmd}`);

  try {
    execSync(cmd, { stdio: 'inherit', cwd: join(testDir, '..') });
    console.log('\n  ✓ Teardown complete\n');
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    // Non-zero exit is expected if no containers were running
    // Only log warning, don't fail the entire teardown
    console.log(`  ⚠ Teardown warning: ${msg}`);
    console.log('\n  (This is normal if no containers were running)\n');
  }
}
