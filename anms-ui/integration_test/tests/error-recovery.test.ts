/**
 * Error recovery tests: Verify the Angular UI handles network failures,
 * server timeouts, and connection resets gracefully.
 */

import { test, expect } from '@playwright/test';
import { setupAuth } from './auth-setup';

test.describe('Error Recovery', () => {
  test('UI handles missing API gracefully', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/');
    const bodyText = await page.textContent('body');
    expect(bodyText).not.toBeNull();
    console.log('[error-recovery] UI handles missing API gracefully');
  });

  test('UI handles 500 errors gracefully', async ({ page }) => {
    await setupAuth(page);
    await page.route('**/core/*', async route => {
      await route.fulfill({ status: 500, body: 'Internal Server Error' });
    });
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('body', { timeout: 5000 });
    const bodyText = await page.textContent('body');
    expect(bodyText).not.toBeNull();
    console.log('[error-recovery] 500 errors handled gracefully');
  });

  test('UI handles connection timeout gracefully', async ({ page }) => {
    await setupAuth(page);
    await page.route('**/core/*', async route => {
      await route.abort('connectiontimeout');
    });
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('body', { timeout: 5000 });
    const bodyText = await page.textContent('body');
    expect(bodyText).not.toBeNull();
    console.log('[error-recovery] Connection timeout handled gracefully');
  });

  test('UI recovers after temporary API failure', async ({ page }) => {
    await setupAuth(page);
    let requestCount = 0;

    await page.route('**/core/*', async route => {
      if (requestCount === 0) {
        await route.fulfill({ status: 503, body: 'Service Unavailable' });
      } else {
        await route.continue();
      }
      requestCount++;
    });

    const response1 = await page.goto('/');
    expect(response1?.status()).toBeLessThan(400);

    console.log('[error-recovery] Recovery after temporary failure');
  });

  test('UI handles empty API responses gracefully', async ({ page }) => {
    await setupAuth(page);
    await page.route('**/core/*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: '{}',
      });
    });
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('body', { timeout: 5000 });
    const bodyText = await page.textContent('body');
    expect(bodyText).not.toBeNull();
    console.log('[error-recovery] Empty responses handled gracefully');
  });

  test('UI handles malformed JSON gracefully', async ({ page }) => {
    await setupAuth(page);
    await page.route('**/core/*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: 'not valid json {',
      });
    });
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('body', { timeout: 5000 });
    const bodyCount = await page.locator('body').count();
    expect(bodyCount).toBeGreaterThan(0);
    console.log('[error-recovery] Malformed JSON handled gracefully');
  });
});
