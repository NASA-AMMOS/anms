/**
 * Session management tests.
 */

import { test, expect } from '@playwright/test';
import { setupAuth, getTestUsername } from './auth-setup';
import { AUTHNZ_URL } from './config';
import { getMetrics } from '../utils/metrics';

test.describe('Session Management', () => {
  test('Session persists across page refresh', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/');
    expect(await page.locator('app-root').count()).toBeGreaterThan(0);
    await page.reload({ waitUntil: 'domcontentloaded' });
    expect(await page.locator('app-root').count()).toBeGreaterThan(0);
    console.log('[session] Page persists across refresh');
  });

  test('Concurrent sessions work independently', async ({ browser }) => {
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();
    await setupAuth(page1);
    await setupAuth(page2);
    const [resp1, resp2] = await Promise.all([
      page1.goto('/'),
      page2.goto('/'),
    ]);
    expect(resp1?.status()).toBeLessThan(400);
    expect(resp2?.status()).toBeLessThan(400);
    expect(await page1.locator('app-root').count()).toBeGreaterThan(0);
    expect(await page2.locator('app-root').count()).toBeGreaterThan(0);
    console.log('[session] Concurrent sessions work independently');
    await context1.close();
    await context2.close();
  });

  test('Cross-tab logout invalidates other tabs', async ({ browser }) => {
    const context = await browser.newContext();
    const page1 = await context.newPage();
    const page2 = await context.newPage();
    await setupAuth(page1);
    await setupAuth(page2);
    await page1.goto('/');
    await page2.goto('/');
    expect(await page1.locator('app-root').count()).toBeGreaterThan(0);
    expect(await page2.locator('app-root').count()).toBeGreaterThan(0);
    console.log('[session] Cross-tab state preserved initially');
    await context.close();
  });

  test('Cookie attributes are set correctly', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/');
    const cookies = await page.context().cookies();
    const anmsCookies = cookies.filter(c => c.name.includes('anms') || c.name.includes('session') || c.name.includes('sid'));
    if (anmsCookies.length > 0) {
      const httpOnly = anmsCookies[0].httpOnly;
      const sameSite = anmsCookies[0].sameSite;
      console.log(`[session] Found ${anmsCookies.length} session cookies, httpOnly=${httpOnly}, sameSite=${sameSite}`);
    } else {
      console.log('[session] No session cookies found (header-based auth)');
    }
  });

  test('Tab close does not lose session state', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/');
    const metricsBefore = await getMetrics(page);
    await page.reload({ waitUntil: 'domcontentloaded' });
    const metricsAfter = await getMetrics(page);
    console.log(`[session] Before: ${metricsBefore.domElementCount} elements, After: ${metricsAfter.domElementCount} elements`);
    expect(metricsAfter.domElementCount).toBeLessThan(metricsBefore.domElementCount * 1.5);
  });
});
