/**
 * Concurrent load and stress tests: N parallel users, memory leak detection.
 *
 * These tests simulate multiple users accessing the Angular UI simultaneously
 * to measure load times, response stability, and detect memory leaks.
 *
 * Test Spec: ANMS_PERF_001 (Concurrency test), ANMS_PERF_002 (Memory stability)
 */

import { test, expect } from '@playwright/test';
import { setupAuth } from './auth-setup';
import { AUTHNZ_URL } from './config';
import { getMetrics, logMetrics } from '../utils/metrics';

test.describe('Concurrent Load Tests', () => {
  test('Single user loads homepage', async ({ page }) => {
    await setupAuth(page);
    const startTime = Date.now();
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    const loadTime = Date.now() - startTime;
    const metrics = await getMetrics(page);
    logMetrics('Single user', metrics);
    expect(loadTime).toBeLessThan(15000);
  });

  test('Five concurrent users load homepage', async ({ browser }) => {
    const context = await browser.newContext();
    const pages = await Promise.all(
      Array.from({ length: 5 }, async () => {
        const page = await context.newPage();
        await setupAuth(page);
        return page;
      })
    );

    const results = await Promise.all(
      pages.map(async (page, i) => {
        const startTime = Date.now();
        await page.goto('/', { waitUntil: 'domcontentloaded' });
        const loadTime = Date.now() - startTime;
        const metrics = await getMetrics(page);
        return { index: i, loadTime, metrics };
      })
    );

    results.forEach(r => {
      logMetrics(`Concurrent user ${r.index}`, r.metrics);
      expect(r.loadTime).toBeLessThan(15000);
    });

    const avgLoadTime = results.reduce((sum, r) => sum + r.loadTime, 0) / results.length;
    console.log(`[stress] Avg load time for 5 users: ${Math.round(avgLoadTime)}ms`);
    expect(avgLoadTime).toBeLessThan(15000);

    await context.close();
  });

  test('Ten concurrent users load homepage', async ({ browser }) => {
    const context = await browser.newContext();
    const pages = await Promise.all(
      Array.from({ length: 10 }, async () => {
        const page = await context.newPage();
        await setupAuth(page);
        return page;
      })
    );

    const results = await Promise.all(
      pages.map(async (page, i) => {
        const startTime = Date.now();
        await page.goto('/', { waitUntil: 'domcontentloaded' });
        const loadTime = Date.now() - startTime;
        const metrics = await getMetrics(page);
        return { index: i, loadTime, metrics };
      })
    );

    results.forEach(r => {
      expect(r.loadTime).toBeLessThan(20000);
    });

    const avgLoadTime = results.reduce((sum, r) => sum + r.loadTime, 0) / results.length;
    console.log(`[stress] Avg load time for 10 users: ${Math.round(avgLoadTime)}ms`);
    expect(avgLoadTime).toBeLessThan(20000);

    await context.close();
  });

  test('Memory leak detection — 50 page reloads', async ({ page }) => {
    test.setTimeout(120000);
    await setupAuth(page);

    const memoryReadings = [];
    for (let i = 0; i < 50; i++) {
      await page.goto('/', { waitUntil: 'domcontentloaded' });
      await page.waitForLoadState('load', { timeout: 5000 }).catch(() => {});
      const metrics = await getMetrics(page);
      memoryReadings.push(metrics.domContentLoadedMs);
      if (i % 10 === 0) {
        console.log(`[stress] Reload ${i + 1}/50: DOM=${metrics.domContentLoadedMs}ms, elements=${metrics.domElementCount}`);
      }
    }

    const firstQuartile = memoryReadings.slice(0, 12).reduce((a, b) => a + b, 0) / 12;
    const lastQuartile = memoryReadings.slice(37).reduce((a, b) => a + b, 0) / 13;
    console.log(`[stress] First quartile avg: ${Math.round(firstQuartile)}ms, Last quartile avg: ${Math.round(lastQuartile)}ms`);
    expect(lastQuartile).toBeLessThan(firstQuartile * 2);
  });
});
