/**
 * Playwright configuration for ANMS Angular UI integration tests.
 *
 * Tests the full stack (postgres, anms-core, redis, UI) with headless Chromium.
 * Runs tests against the built Angular UI through authnz reverse proxy on port 8084 (matches production).
 *
 * Usage:
 *   # Run all tests
 *   npx playwright test
 *
 *   # Run specific test file
 *   npx playwright test tests/base.test.ts
 *
 *   # Run with UI (visible browser) for debugging
 *   npx playwright test --headed
 *
 *   # Run with parallelism and workers
 *   npx playwright test --workers 4
 *
 *   # Generate report
 *   npx playwright test --reporter=html
 */

import { defineConfig, devices } from '@playwright/test';
import { AUTHNZ_URL } from './tests/config';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['list'],
  ],
  use: {
    baseURL: AUTHNZ_URL,
    trace: 'on-first-retry',
    screenshot: 'on',
    video: 'on',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
    },
  ],
  globalSetup: './tests/global-setup.ts',
  globalTeardown: './tests/global-teardown.ts',
});
