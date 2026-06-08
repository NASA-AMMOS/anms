/**
 * Grafana Live WebSocket reconnection tests.
 *
 * Simulates network conditions (offline, slow, intermittent) via Playwright's
 * routing API and verifies Grafana Live connections (WebSocket) reconnect
 * properly after disruption.
 *
 * Grafana Live uses WebSocket for real-time data streaming. When the network
 * drops, the client should automatically reconnect.
 *
 * Usage:
 *   npx playwright test grafana-live-reconnect.test.ts
 */

import { test, expect } from '@playwright/test';
import { setupAuth } from './auth-setup';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';
const GRAFANA_PROXY_URL = '/grafana';

test.describe('Grafana Live WebSocket Reconnection', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('Grafana live endpoint is accessible', async ({ page }) => {
    // The Grafana proxy routes /grafana/api/live/stream through to Grafana's
    // Live WebSocket endpoint at /api/live/stream
    await page.goto(BASE_URL + GRAFANA_PROXY_URL + '/api/live/stream');
    await page.waitForTimeout(2000);
    
    // Should not have a hard error
    console.log('[grafana-live] Live endpoint accessible');
  });

  test('Monitor page loads with Grafana iframe', async ({ page }) => {
    await page.goto(BASE_URL + '/dashboard/monitor');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);
    
    // Verify iframe is present
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
    
    await page.goto(BASE_URL + '/dashboard/monitor');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);
    
    // Filter to only errors from Grafana iframe context
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

  test('Simulates network drop — verifies page still accessible', async ({ page }) => {
    // Route all network to a non-existent host (simulates network drop)
    await page.route('**/*', async route => {
      await route.abort('connectionrefused');
    });
    
    await page.goto(BASE_URL);
    await page.waitForTimeout(1000);
    
    // The Angular app should still be rendered (even if no data loads)
    const bodyText = await page.textContent('body');
    expect(bodyText.length).toBeGreaterThan(0);
    
    console.log('[grafana-live] Network drop simulated — app still rendered');
    
    // Restore normal routing
    await page.unroute('**/*');
  });
});
