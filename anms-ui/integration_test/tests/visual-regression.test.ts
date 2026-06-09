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
 * Dynamic content handling:
 * - Agents page: timestamps in "First/Last Registered" columns are masked
 * - Monitor page: Grafana iframe is replaced with a static placeholder
 *   (live Grafana data changes between screenshot attempts, making stable
 *   comparison impossible)
 * - Dashboard & Reports pages: no dynamic content, standard comparison
 *
 * Usage:
 *   npx playwright test visual-regression.test.ts --update-snapshots   # create baselines
 *   npx playwright test visual-regression.test.ts                       # compare
 */

import { test, expect } from '@playwright/test';
import { setupAuth } from './auth-setup';

const BASE_URL = process.env.BASE_URL || 'http://localhost:8084';

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
        threshold: 0.1,
      });
    });

    test(`Agents page - ${bp.label}`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto(BASE_URL + '/dashboard/agents');
      await page.waitForLoadState('domcontentloaded');

      // Mask dynamic timestamp columns so they don't cause flaky diffs
      await page.evaluate(() => {
        // Mask cells with timestamp-like content (ISO dates, etc.)
        document.querySelectorAll('td, th').forEach(el => {
          const text = el.textContent?.trim();
          if (text && /^\d{4}-\d{2}-\d{2}/.test(text)) {
            el.style.color = 'transparent';
            el.style.border = 'none';
            el.style.backgroundColor = 'transparent';
            el.style.minWidth = el.offsetWidth + 'px';
            el.style.minHeight = el.offsetHeight + 'px';
          }
        });
      });

      await page.waitForTimeout(500); // Allow masking to apply

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

      // Replace the Grafana iframe with a static placeholder div.
      // Grafana's live data updates between Playwright's stability check
      // screenshots, making comparison impossible. Replacing with a
      // static element ensures consistent screenshots.
      await page.evaluate(() => {
        const iframes = document.querySelectorAll('iframe');
        iframes.forEach(iframe => {
          // Create a placeholder that mimics a dark Grafana dashboard
          const placeholder = document.createElement('div');
          placeholder.style.width = iframe.offsetWidth + 'px';
          placeholder.style.height = iframe.offsetHeight + 'px';
          placeholder.style.background = '#1a1a2e';
          placeholder.style.position = 'absolute';
          placeholder.style.top = iframe.offsetTop + 'px';
          placeholder.style.left = iframe.offsetLeft + 'px';
          placeholder.style.zIndex = '9999';
          placeholder.style.border = 'none';
          iframe.style.visibility = 'hidden';
          iframe.parentNode?.appendChild(placeholder);
        });
      });

      await page.waitForTimeout(1000); // Wait for Angular rendering

      await expect(page).toHaveScreenshot(`${baselineName}-monitor.png`, {
        threshold: 0.1,
      });
    });
  }
});
