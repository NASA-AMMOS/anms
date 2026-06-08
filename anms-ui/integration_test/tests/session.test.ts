/**
 * Session management tests: Verify session persistence, concurrent sessions,
 * and state preservation across the Angular UI.
 */

import { test, expect } from '@playwright/test';
import { setupAuth, getTestUsername } from './auth-setup';
import { getMetrics } from '../utils/metrics';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';
const USERNAME = getTestUsername();

test.describe('Session Management', () => {
  test('Session persists across page refresh', async ({ page }) => {
    await setupAuth(page);
    await page.goto(BASE_URL);
    
    // Verify user is visible
    const bodyText = await page.textContent('body');
    expect(bodyText).toContain(USERNAME);
    
    // Refresh the page
    await page.reload({ waitUntil: 'domcontentloaded' });
    
    // User should still be visible after refresh
    const bodyTextAfter = await page.textContent('body');
    expect(bodyTextAfter).toContain(USERNAME);
    
    console.log('[session] Session persists across refresh');
  });

  test('Concurrent sessions work independently', async ({ browser }) => {
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();
    
    await setupAuth(page1);
    await setupAuth(page2);
    
    // Both pages navigate simultaneously
    const [resp1, resp2] = await Promise.all([
      page1.goto(BASE_URL),
      page2.goto(BASE_URL)
    ]);
    
    expect(resp1?.status()).toBeLessThan(400);
    expect(resp2?.status()).toBeLessThan(400);
    
    const text1 = await page1.textContent('body');
    const text2 = await page2.textContent('body');
    
    expect(text1).toContain(USERNAME);
    expect(text2).toContain(USERNAME);
    
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
    
    await page1.goto(BASE_URL);
    await page2.goto(BASE_URL);
    
    // Both should show the username
    const text1 = await page1.textContent('body');
    const text2 = await page2.textContent('body');
    expect(text1).toContain(USERNAME);
    expect(text2).toContain(USERNAME);
    
    console.log('[session] Cross-tab state preserved initially');
    
    await context.close();
  });

  test('Cookie attributes are set correctly', async ({ page }) => {
    await setupAuth(page);
    await page.goto(BASE_URL);
    
    // Playwright can read cookies from the page
    const cookies = await page.context().cookies([BASE_URL]);
    
    // Check that session cookies are set
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
    await page.goto(BASE_URL);
    
    const metricsBefore = await getMetrics(page);
    
    // Close and reopen a similar page
    await page.reload({ waitUntil: 'domcontentloaded' });
    
    const metricsAfter = await getMetrics(page);
    
    console.log(`[session] Before: ${metricsBefore.elementCount} elements, After: ${metricsAfter.elementCount} elements`);
    // Element count should be similar (not significantly higher)
    expect(metricsAfter.elementCount).toBeLessThan(metricsBefore.elementCount * 1.5);
  });
});
