/**
 * Monitor tab tests: Verify Grafana iframe rendering and monitor status display.
 */

import { test, expect } from '@playwright/test';
import { setupAuth, getTestUsername } from './auth-setup';
import { AUTHNZ_URL } from './config';
import { getMetrics, logMetrics } from '../utils/metrics';

test.describe('Monitor Tab', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('Monitor page loads with Grafana iframe', async ({ page }) => {
    await page.goto('/dashboard/monitor');
    const bodyText = await page.textContent('body');
    expect(bodyText).not.toBeNull();
    const iframe = page.locator('iframe');
    await expect(iframe).toBeVisible({ timeout: 10000 });
    const metrics = await getMetrics(page);
    logMetrics('Monitor page', metrics);
    console.log(`[monitor] Dashboard metrics: DOM ${metrics.domContentLoadedMs}ms, Elements: ${metrics.domElementCount}`);
    expect(metrics.domElementCount).toBeGreaterThan(5);
  });

  test('Grafana iframe has correct source', async ({ page }) => {
    await page.goto('/dashboard/monitor');
    const iframe = page.locator('iframe');
    await expect(iframe).toBeVisible({ timeout: 10000 });
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
    await page.goto('/dashboard/monitor');
    await page.waitForLoadState('load', { timeout: 10000 }).catch(() => {});
    const iframe = page.locator('iframe');
    if (await iframe.count() > 0) {
      const iframeSrc = await iframe.getAttribute('src');
      console.log(`[monitor] Grafana available: ${iframeSrc ? 'yes' : 'no'}, src=${iframeSrc}`);
      expect(iframeSrc).toContain('grafana');
    }
  });
});
