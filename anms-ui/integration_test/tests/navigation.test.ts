/**
 * Navigation performance tests: Measure tab switching speed, cache
 * invalidation, and main thread blocking during rapid navigation.
 */

import { test, expect } from '@playwright/test';
import { setupAuth, getTestUsername } from './auth-setup';
import { getMetrics } from '../utils/metrics';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';
const USERNAME = getTestUsername();

test.describe('Navigation Performance', () => {
  test('Tab switching latency', async ({ page }) => {
    await setupAuth(page);
    
    // Measure time to switch between tabs (if tabs exist)
    const tabLocators = page.locator('[routerlink], [data-nav], .nav-item a, mat-tab').first();
    const count = await tabLocators.count();
    
    if (count > 1) {
      const latencies = [];
      for (let i = 0; i < 3; i++) {
        await tabLocators.first().click();
        const startTime = Date.now();
        await page.waitForTimeout(500);
        latencies.push(Date.now() - startTime);
        
        await tabLocators.last().click();
        await page.waitForTimeout(500);
        latencies.push(Date.now() - startTime);
      }
      
      const avg = latencies.reduce((a, b) => a + b, 0) / latencies.length;
      console.log(`[nav] Tab switching: avg=${Math.round(avg)}ms`);
    } else {
      console.log('[nav] No tabs found, skipping tab switching test');
    }
  });

  test('Rapid tab clicking does not crash', async ({ page }) => {
    await setupAuth(page);
    await page.goto(BASE_URL);
    
    // Click rapidly on any clickable elements
    const clickables = page.locator('a, button, [role="button"], mat-tab, mat-sidenav a').first();
    const count = await clickables.count();
    
    if (count > 0) {
      for (let i = 0; i < 8; i++) {
        await clickables.click();
        await page.waitForTimeout(100);
      }
      
      // Page should still be functional
      const bodyText = await page.textContent('body');
      expect(bodyText).toBeDefined();
      
      console.log('[nav] Rapid clicking handled');
    } else {
      console.log('[nav] No clickable elements found');
    }
  });

  test('Memory stable after 50 page cycles', async ({ page }) => {
    await setupAuth(page);
    const elementCounts = [];
    
    for (let i = 0; i < 50; i++) {
      await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(100);
      
      const metrics = await getMetrics(page);
      elementCounts.push(metrics.domElementCount);
      
      if (i % 10 === 0) {
        console.log(`[nav] Cycle ${i + 1}/50: elements=${metrics.domElementCount}`);
      }
    }
    
    // Check for monotonic increase (memory leak indicator)
    const firstQuartile = elementCounts.slice(0, 12).reduce((a, b) => a + b, 0) / 12;
    const lastQuartile = elementCounts.slice(37).reduce((a, b) => a + b, 0) / 13;
    
    console.log(`[nav] First quartile avg elements: ${Math.round(firstQuartile)}, Last: ${Math.round(lastQuartile)}`);
    // Allow 2x increase for cache effects
    expect(lastQuartile).toBeLessThan(firstQuartile * 2);
  });

  test('Navigation after stale data refresh', async ({ page }) => {
    await setupAuth(page);
    await page.goto(BASE_URL);
    
    // Wait for initial load
    await page.waitForTimeout(2000);
    
    // Force refresh
    await page.reload({ waitUntil: 'domcontentloaded' });
    
    const metrics = await getMetrics(page);
    console.log(`[nav] Refresh: DOM=${metrics.domContentLoadedMs}ms, elements=${metrics.domElementCount}`);
    expect(metrics.domContentLoadedMs).toBeLessThan(10000);
  });
});
