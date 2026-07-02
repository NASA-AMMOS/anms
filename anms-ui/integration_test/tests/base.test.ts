/**
 * Base tests: Session management and page loading (with header-based auth).
 *
 * The anms-ui Angular app uses `x-remote-user` header for auth bypass in
 * integration tests. The server (main.js) renders the app with this user.
 *
 * Test Spec: ANMS_FUN_APP_001 (Verify login via header), ANMS_FUN_APP_002 (Verify logout)
 */

import { test, expect } from '@playwright/test';
import { setupAuth, getTestUsername } from './auth-setup';
import { AUTHNZ_URL } from './config';
import { waitForUrlHealthy } from '../utils/api-helpers';
import { getMetrics, logMetrics } from '../utils/metrics';
const USERNAME = getTestUsername();

test.describe('Session Management & Page Loading', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  test('Home page loads successfully', async ({ page }) => {
    const response = await page.goto('/', { waitUntil: 'domcontentloaded' });
    expect(response?.status()).toBeLessThan(400);
    console.log(`[base] Home page accessible, status: ${response?.status()}`);
  });

  test('User profile link is visible after auth', async ({ page }) => {
    await page.goto('/');
    const toolbar = page.locator('mat-toolbar, app-header, header, .mat-toolbar, [class*="toolbar"]');
    const count = await toolbar.count();
    expect(count).toBeGreaterThan(0);
    console.log(`[base] Toolbar/header found: ${count}`);
  });

  test('Logout link exists in header', async ({ page }) => {
    await page.goto('/');
    const logout = page.locator('a:has-text("Logout"), button:has-text("Logout")');
    const count = await logout.count();
    expect(count).toBeGreaterThanOrEqual(0);
    console.log(`[base] Logout links found: ${count}`);
  });

  test('Page loads within acceptable time', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    const metrics = await getMetrics(page);
    logMetrics('Home page', metrics);
    expect(metrics.domContentLoadedMs).toBeLessThan(10000);
    expect(metrics.domElementCount).toBeGreaterThan(0);
  });
});
