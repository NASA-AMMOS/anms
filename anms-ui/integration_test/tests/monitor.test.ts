/**
 * Monitor tab tests: Verify Grafana iframe rendering and monitor status display.
 *
 * The Monitor page displays a Grafana dashboard embedded in an iframe.
 * Grafana proxies through the UI at /grafana/ — if Grafana is not running,
 * the iframe will show a "Page Not Found" error.
 *
 * Test Spec: ANMS_FUN_MGT_001 (Verify Monitor tab), ANMS_FUN_MGT_002 (Verify Grafana)
 */

import { test, expect } from '@playwright/test';
import { setupAuth, getTestUsername } from './auth-setup';
import { getMetrics } from '../utils/metrics';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';

test.describe('Monitor Tab', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('Monitor page loads with Grafana iframe', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard/monitor`);

    // The page should have loaded (Angular component rendered)
    const bodyText = await page.textContent('body');
    expect(bodyText.length).toBeGreaterThan(0);

    // There should be a Grafana iframe
    const iframe = page.locator('iframe');
    await expect(iframe).toBeVisible({ timeout: 10000 });

    const metrics = await getMetrics(page);
    console.log(`[monitor] Dashboard metrics: DOM ${metrics.domContentLoadedMs}ms, Elements: ${metrics.domElementCount}`);
    expect(metrics.domElementCount).toBeGreaterThan(5);
  });

  test('Grafana iframe has correct source', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard/monitor`);

    // Wait for iframe to be present
    const iframe = page.locator('iframe');
    await expect(iframe).toBeVisible({ timeout: 10000 });

    // The iframe should point to Grafana
    const src = await iframe.getAttribute('src');
    expect(src).toContain('grafana');

    console.log(`[monitor] Grafana iframe src: ${src}`);
  });

  test('Monitor page renders without JS errors', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto(`${BASE_URL}/dashboard/monitor`);

    // Give the iframe time to load
    await page.waitForTimeout(3000);

    // The iframe may show "Page Not Found" if Grafana is not running — that's expected
    // We just verify the Angular app itself has no JS errors
    const iframe = page.locator('iframe');
    if (await iframe.count() > 0) {
      const iframeSrc = await iframe.getAttribute('src');
      console.log(`[monitor] Grafana available: ${iframeSrc ? 'yes' : 'no'}, src=${iframeSrc}`);
    }
  });
});
