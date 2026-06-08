/**
 * Visual regression tests: Screenshot comparison across breakpoints.
 *
 * Takes screenshots at 3 breakpoints and compares against baselines:
 * - Desktop (1920x1080)
 * - Laptop (1366x768)
 * - Tablet (768x1024)
 *
 * First run creates baselines — subsequent runs compare.
 * Baselines stored in tests/__screenshots__/<testname>.png
 *
 * Usage:
 *   npx playwright test visual-regression.test.ts --update-snapshots   # create baselines
 *   npx playwright test visual-regression.test.ts                       # compare
 */

import { test, expect } from '@playwright/test';
import { setupAuth } from './auth-setup';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';

// Breakpoints to test
const BREAKPOINTS = [
  { name: 'desktop', width: 1920, height: 1080, label: '1920x1080' },
  { name: 'laptop', width: 1366, height: 768, label: '1366x768' },
  { name: 'tablet', width: 768, height: 1024, label: '768x1024' },
];

test.describe('Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  // Screenshot each page at each breakpoint
  for (const bp of BREAKPOINTS) {
    const snapshotName = `${bp.name}`;
    const baselineName = `visual-${snapshotName}`;

    test(`Dashboard home page - ${bp.label}`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto(BASE_URL);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(1000); // Wait for Angular rendering

      await expect(page).toHaveScreenshot(`${baselineName}-dashboard.png`, {
        threshold: 0.1, // Allow 10% pixel difference for dynamic content
      });
    });

    test(`Agents page - ${bp.label}`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto(BASE_URL + '/dashboard/agents');
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(1000);

      await expect(page).toHaveScreenshot(`${baselineName}-agents.png`, {
        threshold: 0.1,
      });
    });

    test(`Reports page - ${bp.label}`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto(BASE_URL + '/dashboard/reports');
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(1000);

      await expect(page).toHaveScreenshot(`${baselineName}-reports.png`, {
        threshold: 0.1,
      });
    });

    test(`Monitor page - ${bp.label}`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto(BASE_URL + '/dashboard/monitor');
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(1000);

      await expect(page).toHaveScreenshot(`${baselineName}-monitor.png`, {
        threshold: 0.1,
      });
    });
  }
});
