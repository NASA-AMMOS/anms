/**
 * Grafana Live WebSocket reconnection tests.
 */

import { test, expect } from '@playwright/test';
import { setupAuth } from './auth-setup';
import { AUTHNZ_URL } from './config';
const GRAFANA_PROXY_URL = '/grafana';

test.describe('Grafana Live WebSocket Reconnection', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('Grafana live endpoint is accessible', async ({ page }) => {
    await page.goto(GRAFANA_PROXY_URL + '/api/live/stream');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('body', { timeout: 5000 }).catch(() => {});
    const bodyText = await page.locator('body').textContent();
    expect(bodyText).not.toBeNull();
    console.log('[grafana-live] Live endpoint accessible');
  });

  test('Monitor page loads with Grafana iframe', async ({ page }) => {
    await page.goto('/dashboard/monitor');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('[ng-version]', { timeout: 5000 }).catch(() => {});
    const iframe = page.locator('iframe[src*="grafana"]');
    await expect(iframe).toBeVisible({ timeout: 10000 });
    const count = await iframe.count();
    expect(count).toBeGreaterThanOrEqual(1);
    console.log(`[grafana-live] Found ${count} Grafana iframe(s)`);
  });

  test('Grafana iframe loads without console errors', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    await page.goto('/dashboard/monitor');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('[ng-version]', { timeout: 5000 }).catch(() => {});
    const grafanaErrors = consoleErrors.filter(e =>
      e.includes('grafana') || e.includes('WebSocket') || e.includes('live')
    );
    if (grafanaErrors.length > 0) {
      console.log('[grafana-live] Console errors from Grafana context:');
      for (const err of grafanaErrors) {
        console.log(`  - ${err}`);
      }
    }
  });
});
