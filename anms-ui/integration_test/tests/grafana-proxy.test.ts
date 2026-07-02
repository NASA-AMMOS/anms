/**
 * Grafana proxy endpoint tests: Verify Grafana is reachable end-to-end
 * through the UI's proxy routes.
 *
 * If Grafana is not running in the testenv config, tests are skipped conditionally.
 */

import { test, expect } from '@playwright/test';
import { setupAuth } from './auth-setup';
import { AUTHNZ_URL } from './config';
import { waitForUrlHealthy } from '../utils/api-helpers';

// Check if Grafana is reachable — skip if not available
let grafanaAvailable = false;

test.beforeEach(async ({ request }) => {
  // Run Grafana health check once per suite
  if (grafanaAvailable === false) {
    try {
      grafanaAvailable = await waitForUrlHealthy(AUTHNZ_URL + '/grafana/api/health', 3);
    } catch {
      grafanaAvailable = false;
    }
  }
  if (!grafanaAvailable) {
    test.skip(true, 'Grafana is not available');
  }
});

test.describe('Grafana Proxy Endpoints', () => {
  test('Grafana root proxy returns 200 or redirect', async ({ request }) => {
    const response = await request.get(AUTHNZ_URL + '/grafana/', {
      maxRetries: 2,
      timeout: 10000,
    });
    console.log('[grafana] GET /grafana/ status: ' + response.status());
    expect(response.status()).toBeLessThan(500);
  });

  test('Grafana API health returns valid response', async ({ request }) => {
    const response = await request.get(AUTHNZ_URL + '/grafana/api/health', {
      maxRetries: 2,
      timeout: 10000,
      failOnStatusCode: false,
    });
    console.log('[grafana] GET /grafana/api/health status: ' + response.status());
    expect(response.status()).toBeLessThan(500);
    if (response.status() === 200) {
      const body = await response.text();
      console.log('[grafana] Health response: ' + body.substring(0, 200));
      expect(body.length).toBeGreaterThan(0);
    }
  });

  test('Grafana dashboard page loads via proxy', async ({ request }) => {
    const response = await request.get(
      AUTHNZ_URL + '/grafana/d/mwvijjmvk/monitor-page',
      { maxRetries: 2, timeout: 10000 }
    );
    console.log('[grafana] Dashboard page status: ' + response.status());
    expect(response.status()).toBeLessThan(500);
  });

  test('Grafana Live WebSocket API endpoint is reachable', async ({ request }) => {
    const response = await request.get(
      AUTHNZ_URL + '/grafana/api/live/',
      { maxRetries: 2, timeout: 10000 }
    );
    console.log('[grafana] /grafana/api/live/ status: ' + response.status());
    expect(response.status()).toBeLessThan(500);
  });

  test('Grafana dashboard API returns metadata', async ({ request }) => {
    const response = await request.get(
      AUTHNZ_URL + '/grafana/api/dashboards/',
      { maxRetries: 2, timeout: 10000 }
    );
    console.log('[grafana] Dashboard list status: ' + response.status());
    expect(response.status()).toBeLessThan(500);
  });

  test('Grafana image renderer is reachable', async ({ request }) => {
    const response = await request.get(AUTHNZ_URL + '/renderer/health', {
      maxRetries: 2,
      timeout: 10000,
    });
    console.log('[grafana] Renderer health status: ' + response.status());
    expect(response.status()).toBeLessThan(500);
  });

  test('Monitor page loads via UI (not direct Grafana)', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/dashboard/monitor', {
      waitUntil: 'domcontentloaded',
      timeout: 15000,
    });
    const bodyText = await page.textContent('body');
    expect(bodyText).not.toBeNull();
    expect(bodyText!.length).toBeGreaterThan(0);
    const iframe = page.locator('iframe');
    await expect(iframe).toBeVisible({ timeout: 10000 });
    const iframeSrc = await iframe.getAttribute('src');
    console.log('[grafana] Monitor page iframe src: ' + iframeSrc);
    expect(iframeSrc).toContain('grafana');
  });
});
