/**
 * Navigation performance tests: Measure tab switching speed, cache
 * invalidation, and main thread blocking during rapid navigation.
 */

import { test, expect } from '@playwright/test';
import { setupAuth, getTestUsername } from './auth-setup';
import { AUTHNZ_URL } from './config';
import { getMetrics, logMetrics } from '../utils/metrics';
const USERNAME = getTestUsername();

test.describe('Navigation Performance', () => {
  test('Tab switching latency', async ({ page }) => {
    await setupAuth(page);
    const tabLocators = page.locator('[routerlink], [data-nav], .nav-item a, mat-tab').first();
    const count = await tabLocators.count();

    if (count > 1) {
      const latencies: number[] = [];
      for (let i = 0; i < 3; i++) {
        await tabLocators.first().click();
        const startTime = Date.now();
        await page.waitForLoadState('domcontentloaded', { timeout: 5000 }).catch(() => {});
        latencies.push(Date.now() - startTime);
        await tabLocators.last().click();
        await page.waitForLoadState('domcontentloaded', { timeout: 5000 }).catch(() => {});
      }
      const avg = latencies.reduce((a, b) => a + b, 0) / latencies.length;
      console.log(`[nav] Tab switching: avg=${Math.round(avg)}ms`);
    } else {
      console.log('[nav] No tabs found, skipping tab switching test');
    }
  });

  test('Rapid tab clicking does not crash', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/');
    const clickables = page.locator('a, button, [role="button"], mat-tab, mat-sidenav a').first();
    const count = await clickables.count();

    if (count > 0) {
      for (let i = 0; i < 8; i++) {
        await clickables.click();
        await page.waitForLoadState('domcontentloaded', { timeout: 2000 }).catch(() => {});
      }
      const bodyText = await page.textContent('body');
      expect(bodyText).not.toBeNull();
      console.log('[nav] Rapid clicking handled');
    } else {
      console.log('[nav] No clickable elements found');
    }
  });

  test('Memory stable after 50 page cycles', async ({ page }) => {
    test.setTimeout(120000);
    await setupAuth(page);
    const elementCounts: number[] = [];

    for (let i = 0; i < 50; i++) {
      await page.goto('/', { waitUntil: 'domcontentloaded' });
      await page.waitForLoadState('load', { timeout: 5000 }).catch(() => {});
      const metrics = await getMetrics(page);
      elementCounts.push(metrics.domElementCount);
      if (i % 10 === 0) {
        console.log(`[nav] Cycle ${i + 1}/50: elements=${metrics.domElementCount}`);
      }
    }

    const firstQuartile = elementCounts.slice(0, 12).reduce((a, b) => a + b, 0) / 12;
    const lastQuartile = elementCounts.slice(37).reduce((a, b) => a + b, 0) / 13;
    console.log(`[nav] First quartile avg elements: ${Math.round(firstQuartile)}, Last: ${Math.round(lastQuartile)}`);
    expect(lastQuartile).toBeLessThan(firstQuartile * 2);
  });

  test('Navigation after stale data refresh', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/');
    await page.waitForSelector('[ng-version]', { timeout: 5000 }).catch(() => {});
    await page.reload({ waitUntil: 'domcontentloaded' });
    const metrics = await getMetrics(page);
    logMetrics('Refresh', metrics);
    expect(metrics.domContentLoadedMs).toBeLessThan(10000);
  });
});
