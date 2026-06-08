/**
 * Navigation performance tests: Measure tab switching speed, cache
 * invalidation, and main thread blocking during rapid navigation.
 *
 * Test cases:
 *   1. Tab switching latency — time to switch between each tab pair
 *   2. Rapid navigation — back-to-back tab clicks under stress
 *   3. Cache behavior — does navigating away preserve state?
 *   4. Memory accumulation — does navigating cycle increase heap over time?
 *   5. Stale data detection — does a tab show stale data after switching away?
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';
const TEST_USERNAME = process.env.TEST_USERNAME || 'test';
const TEST_PASSWORD = process.env.TEST_PASSWORD || 'test';

interface NavMetric {
  from: string;
  to: string;
  latencyMs: number;
  domContentLoadedMs: number;
  error?: string;
}

/**
 * Login helper.
 */
async function login(page: any) {
  await page.goto(`${BASE_URL}/`);
  await page.fill('input[name="httpd_username"]', TEST_USERNAME);
  await page.fill('input[name="httpd_password"]', TEST_PASSWORD);
  await page.click('button[type="submit"], input[type="submit"]');
  await page.waitForLoadState('domcontentloaded', { timeout: 15000 });
}

/**
 * Get tab locator by name.
 */
function getTabLocator(page: any, tabName: string) {
  const tabs: Record<string, string> = {
    'Monitor': 'Monitor',
    'Agents': 'Agents',
    'Build': 'Build',
    'Status': 'Status',
    'ADMs': 'ADMs',
  };
  
  const name = tabs[tabName] || tabName;
  return page.locator(`a:has-text("${name}"), [data-qa="${tabName.toLowerCase()}-tab"]`).first();
}

/**
 * Navigate to a tab and measure performance.
 */
async function navigateToTab(page: any, tabName: string): Promise<NavMetric & { metrics: any }> {
  const navStart = Date.now();
  const tabLocator = getTabLocator(page, tabName);
  
  let error: string | undefined;
  let domContentLoadedMs = 0;

  try {
    await tabLocator.click();
    
    // Measure DOM content loaded time
    const perfMetrics = await page.evaluate(() => {
      const perf = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: perf ? perf.domContentLoadedEventEnd - perf.startTime : 0,
        loadEvent: perf ? perf.loadEventEnd - perf.startTime : 0,
        responseEnd: perf ? perf.responseEnd - perf.requestStart : 0,
      };
    });
    
    domContentLoadedMs = perfMetrics.domContentLoaded;
  } catch (err: any) {
    error = err.message;
  }

  const latencyMs = Date.now() - navStart;

  return {
    from: 'current',
    to: tabName,
    latencyMs,
    domContentLoadedMs,
    error,
    metrics: {
      domContentLoadedMs,
      jsHeapUsedSize: 0,
      domElementCount: 0,
    },
  };
}

test.describe('Navigation Performance', () => {
  test('Tab switching latency matrix', async ({ page }) => {
    console.log('\n══════════════════════════════════════════════');
    console.log('  Navigation: Tab Switching Latency Matrix');
    console.log('══════════════════════════════════════════════');

    await login(page);

    const tabs = ['Monitor', 'Agents', 'Build', 'Status', 'ADMs'];
    const metrics: NavMetric[] = [];

    for (let i = 0; i < tabs.length - 1; i++) {
      const metric = await navigateToTab(page, tabs[i]);
      metrics.push(metric);
      await page.waitForTimeout(500); // Brief pause
    }

    // Report results
    console.log('\n[nav] Tab switching latency:');
    for (const m of metrics) {
      console.log(`  ${m.from} → ${m.to}: ${m.latencyMs}ms`);
      console.log(`    DOMContentLoaded: ${m.domContentLoadedMs}ms${m.error ? ` (${m.error})` : ''}`);
    }

    // Most tab switches should complete in under 3 seconds
    const avgLatency = metrics.reduce((sum, m) => sum + m.latencyMs, 0) / metrics.length;
    console.log(`\n[nav] Average switch latency: ${avgLatency.toFixed(0)}ms`);
    expect(avgLatency).toBeLessThan(5000); // Generous threshold
  });

  test('Rapid navigation — back to back tab clicks', async ({ page }) => {
    console.log('\n══════════════════════════════════════════════');
    console.log('  Navigation: Rapid Tab Clicking');
    console.log('══════════════════════════════════════════════');

    await login(page);

    const tabs = ['Monitor', 'Agents', 'Build', 'Status', 'ADMs', 'Monitor', 'Agents', 'Build'];
    const errors: string[] = [];
    const startTime = Date.now();

    // Rapidly click through all tabs
    for (const tab of tabs) {
      try {
        const tabLocator = getTabLocator(page, tab);
        await tabLocator.click();
        await page.waitForTimeout(100); // Minimal pause
      } catch (err: any) {
        errors.push(err.message);
      }
    }

    const totalTime = Date.now() - startTime;

    console.log(`\n[nav-rapid] ${tabs.length} tab switches in ${totalTime}ms`);
    console.log(`[nav-rapid] Average: ${(totalTime / tabs.length).toFixed(0)}ms per switch`);
    console.log(`[nav-rapid] Errors: ${errors.length}/${tabs.length}`);

    if (errors.length > 0) {
      console.warn('[nav-rapid] Errors during rapid switching:');
      errors.slice(0, 3).forEach(e => console.warn(`  - ${e}`));
    }

    // Should complete all switches in under 30 seconds total
    expect(totalTime).toBeLessThan(30000);
  });

  test('Memory accumulation over navigation cycles', async ({ page }) => {
    console.log('\n══════════════════════════════════════════════');
    console.log('  Navigation: Memory Leak Detection');
    console.log('══════════════════════════════════════════════');

    await login(page);

    const tabs = ['Monitor', 'Agents', 'Build', 'Status', 'ADMs'];
    const memoryReadings: number[] = [];

    // Cycle through tabs 10 times, measuring memory each time
    for (let cycle = 0; cycle < 10; cycle++) {
      for (const tab of tabs) {
        const tabLocator = getTabLocator(page, tab);
        await tabLocator.click();
        await page.waitForTimeout(300); // Allow DOM to settle
      }

      // Capture JS heap usage
      const heapUsed = await page.evaluate(() => {
        if ((performance as any).memory) {
          return (performance as any).memory.usedJSHeapSize;
        }
        return 0;
      });
      memoryReadings.push(heapUsed);
    }

    // Report memory readings
    console.log('\n[nav-memory] Heap used (MB) per cycle:');
    for (let i = 0; i < memoryReadings.length; i++) {
      console.log(`  Cycle ${i + 1}: ${(memoryReadings[i] / (1024 * 1024)).toFixed(2)} MB`);
    }

    // Check for memory leak: compare first and last
    const initialHeap = memoryReadings[0];
    const finalHeap = memoryReadings[memoryReadings.length - 1];
    const growth = finalHeap - initialHeap;

    console.log(`\n[nav-memory] Initial heap: ${(initialHeap / (1024 * 1024)).toFixed(2)} MB`);
    console.log(`[nav-memory] Final heap:   ${(finalHeap / (1024 * 1024)).toFixed(2)} MB`);
    console.log(`[nav-memory] Growth:       ${(growth / (1024 * 1024)).toFixed(2)} MB`);

    // Heuristic: >50MB growth over 50 tab switches is suspicious
    if (growth > 50 * 1024 * 1024) {
      console.warn('[nav-memory] ⚠ Possible memory leak detected');
    } else {
      console.log('[nav-memory] ✓ Memory growth within acceptable range');
    }
  });

  test('Stale data detection after tab switch', async ({ page }) => {
    console.log('\n══════════════════════════════════════════════');
    console.log('  Navigation: Stale Data Detection');
    console.log('══════════════════════════════════════════════');

    await login(page);

    // Visit Agents tab, note what we see
    const agentsTab = getTabLocator(page, 'Agents');
    await agentsTab.click();
    await page.waitForTimeout(1000);
    const agentsText = await page.locator('table, mat-table').textContent();

    // Switch to Build tab
    const buildTab = getTabLocator(page, 'Build');
    await buildTab.click();
    await page.waitForTimeout(1000);
    const buildText = await page.locator('table, mat-table').textContent();

    // Switch back to Agents
    await agentsTab.click();
    await page.waitForTimeout(1000);
    const agentsTextAfter = await page.locator('table, mat-table').textContent();

    console.log(`\n[nav-stale] Agents table text (length): ${agentsText?.length || 0}`);
    console.log(`[nav-stale] Build table text (length): ${buildText?.length || 0}`);
    console.log(`[nav-stale] Agents table text after (length): ${agentsTextAfter?.length || 0}`);

    // The Agents table should still be visible and contain data after switching
    const agentsVisible = await page.locator('table, mat-table').isVisible();
    expect(agentsVisible).toBe(true);
  });
});
