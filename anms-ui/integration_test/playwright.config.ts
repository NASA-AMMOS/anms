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

/**
 * Read environment variables for custom base URL.
 * Default: http://localhost:9030
 */
const BASE_URL = process.env.BASE_URL || 'http://localhost:8084';
const USERNAME = process.env.TEST_USERNAME || 'test';
const PASSWORD = process.env.TEST_PASSWORD || 'test';

export default defineConfig({
  // Test directory
  testDir: './tests',

  // Timeout for each test (in milliseconds)
  timeout: 30000,

  // Fail the build on CI if testrunner exited without reporting test results
  forbidOnly: !!process.env.CI,

  // Retry on CI only (not locally, for faster iteration)
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,

  // Reporter: HTML report always, console on failure
  reporter: [
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['list'],
  ],

  // Use test environment
  use: {
    baseURL: BASE_URL,
    // Collect trace when retrying for failed tests
    trace: 'on-first-retry',
    // Capture screenshots on failure
    screenshot: 'on',
    // Capture video on failure
    video: 'on',
  },

  // Configure projects for different browser engines
  // Chromium only — Firefox/WebKit require additional OS deps (GTK4 for WebKit, etc.)
  // that aren't available in EL9 / Rocky 9 repos. Chromium is sufficient for
  // integration testing the Angular UI.
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Context for concurrent testing (simulates multiple users)
        viewport: { width: 1920, height: 1080 },
      },
    },
  ],

  // Global setup/teardown
  globalSetup: './tests/global-setup.ts',
  globalTeardown: './tests/global-teardown.ts',
});
