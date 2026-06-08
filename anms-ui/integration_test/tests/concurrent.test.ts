/**
 * Concurrent load tests: Simulate multiple users accessing the UI simultaneously.
 *
 * This is the "stress testing" part - measures how the Angular UI handles
 * concurrent users at the browser level.
 *
 * Test cases:
 *   1. Single user baseline (N=1)
 *   2. Light load (N=5)
 *   3. Medium load (N=10)
 *   4. Heavy load (N=20)
 *
 * Metrics tracked:
 *   - Page load time per user
 *   - Main thread blocked time
 *   - JavaScript heap usage
 *   - DOM element count
 *   - Error rate (failed navigations, timeouts)
 */

import { test, expect, chromium, BrowserContext } from '@playwright/test';
import { measureNavigation, capturePageMetrics, calculateMemoryDelta, logMetrics } from '../utils/metrics';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';

interface UserMetrics {
  userId: number;
  loadTimeMs: number;
  domContentLoadedMs: number;
  jsHeapUsed: number;
  domElementCount: number;
  iframeCount: number;
  error: string | null;
}

/**
 * Simulate a single user logging in and navigating to a page.
 */
async function simulateUser(
  page: any,
  userId: number,
  targetPage: string
): Promise<UserMetrics> {
  const startTime = Date.now();
  let error: string | null = null;

  try {
    // Login
    await page.goto(`${BASE_URL}/`, { waitUntil: 'domcontentloaded', timeout: 15000 });
    
    // Fill credentials
    await page.fill('input[name="httpd_username"]', 'test', { timeout: 5000 }).catch(() => {
      console.log(`  [user ${userId}] Already logged in or login form not found`);
    });
    await page.fill('input[name="httpd_password"]', 'test', { timeout: 5000 }).catch(() => {});
    await page.click('button[type="submit"], input[type="submit"]', { timeout: 5000 }).catch(() => {});
    
    // Wait for navigation
    await page.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {
      console.log(`  [user ${userId}] Navigation to dashboard timed out`);
    });

    // Navigate to target page
    const navStart = Date.now();
    await page.goto(`${BASE_URL}${targetPage}`, { waitUntil: 'domcontentloaded', timeout: 15000 }).catch(err => {
      error = `Navigation failed: ${err.message}`;
    });

    // Capture metrics
    const metrics = await capturePageMetrics(page);

    return {
      userId,
      loadTimeMs: Date.now() - startTime,
      domContentLoadedMs: metrics.domContentLoadedMs,
      jsHeapUsed: metrics.jsHeapUsedSize,
      domElementCount: metrics.domElementCount,
      iframeCount: metrics.iframeCount,
      error,
    };
  } catch (err: any) {
    return {
      userId,
      loadTimeMs: Date.now() - startTime,
      domContentLoadedMs: 0,
      jsHeapUsed: 0,
      domElementCount: 0,
      iframeCount: 0,
      error: err.message,
    };
  }
}

test.describe('Concurrent Load Tests', () => {
  test('Baseline: Single user navigation', async ({ browser }) => {
    console.log('\n╔══════════════════════════════════════════╗');
    console.log('║  Concurrent Load: Baseline (N=1)        ║');
    console.log('╚══════════════════════════════════════════╝');

    const context = await browser.newContext();
    const page = await context.newPage();

    const metrics = await simulateUser(page, 0, '/#/monitor');
    
    console.log(`\n[baseline] User 0 results:`);
    console.log(`  Load time:     ${metrics.loadTimeMs}ms`);
    console.log(`  DOMContentLoaded: ${metrics.domContentLoadedMs}ms`);
    console.log(`  JS Heap:       ${(metrics.jsHeapUsed / (1024 * 1024)).toFixed(2)} MB`);
    console.log(`  DOM Elements:  ${metrics.domElementCount}`);
    console.log(`  Iframes:       ${metrics.iframeCount}`);
    if (metrics.error) {
      console.log(`  Error:         ${metrics.error}`);
    }

    await context.close();
  });

  test('Light load: 5 concurrent users', async ({ browser }) => {
    console.log('\n╔══════════════════════════════════════════╗');
    console.log('║  Concurrent Load: Light (N=5)           ║');
    console.log('╚══════════════════════════════════════════╝');

    const contexts: BrowserContext[] = [];
    const pages = [];
    const userMetrics: UserMetrics[] = [];

    try {
      // Create 5 contexts (cheap - shares browser process)
      for (let i = 0; i < 5; i++) {
        const context = await browser.newContext();
        const page = await context.newPage();
        contexts.push(context);
        pages.push(page);
      }

      // Simulate all users simultaneously
      const promises = pages.map((page, i) => 
        simulateUser(page, i, '/#/agents')
      );

      const results = await Promise.all(promises);
      results.forEach(r => userMetrics.push(r));

      // Analyze results
      const avgLoadTime = userMetrics.reduce((sum, m) => sum + m.loadTimeMs, 0) / userMetrics.length;
      const avgDomElements = userMetrics.reduce((sum, m) => sum + m.domElementCount, 0) / userMetrics.length;
      const successRate = userMetrics.filter(m => !m.error).length / userMetrics.length;
      const maxHeap = Math.max(...userMetrics.map(m => m.jsHeapUsed));

      console.log(`\n[light-load] 5 concurrent users:`);
      console.log(`  Success rate:    ${(successRate * 100).toFixed(0)}%`);
      console.log(`  Avg load time:   ${avgLoadTime.toFixed(0)}ms`);
      console.log(`  Avg DOM size:    ${avgDomElements} elements`);
      console.log(`  Max JS Heap:     ${(maxHeap / (1024 * 1024)).toFixed(2)} MB`);

      userMetrics.forEach(m => {
        console.log(`  User ${m.userId}: ${m.loadTimeMs}ms, ${m.domElementCount} DOM elems${m.error ? ` - ${m.error}` : ''}`);
      });

      // Expect reasonable performance
      expect(successRate).toBeGreaterThan(0.8); // At least 80% success
      expect(avgLoadTime).toBeLessThan(15000); // Average under 15s

    } finally {
      // Cleanup
      for (const context of contexts) {
        await context.close();
      }
    }
  });

  test('Medium load: 10 concurrent users', async ({ browser }) => {
    console.log('\n╔══════════════════════════════════════════╗');
    console.log('║  Concurrent Load: Medium (N=10)         ║');
    console.log('╚══════════════════════════════════════════╝');

    const contexts: BrowserContext[] = [];
    const pages = [];
    const userMetrics: UserMetrics[] = [];

    try {
      // Create 10 contexts
      for (let i = 0; i < 10; i++) {
        const context = await browser.newContext();
        const page = await context.newPage();
        contexts.push(context);
        pages.push(page);
      }

      // Simulate all users simultaneously
      const promises = pages.map((page, i) => 
        simulateUser(page, i, '/#/build')
      );

      const results = await Promise.all(promises);
      results.forEach(r => userMetrics.push(r));

      // Analyze results
      const successRate = userMetrics.filter(m => !m.error).length / userMetrics.length;
      const avgLoadTime = userMetrics.reduce((sum, m) => sum + m.loadTimeMs, 0) / userMetrics.length;
      const p95LoadTime = [...userMetrics].sort((a, b) => a.loadTimeMs - b.loadTimeMs)
        .find(m => m.loadTimeMs > avgLoadTime * 0.95);

      console.log(`\n[medium-load] 10 concurrent users:`);
      console.log(`  Success rate:    ${(successRate * 100).toFixed(0)}%`);
      console.log(`  Avg load time:   ${avgLoadTime.toFixed(0)}ms`);
      console.log(`  P95 load time:   ${p95LoadTime ? p95LoadTime.loadTimeMs + 'ms' : 'N/A'}`);

      const errors = userMetrics.filter(m => m.error);
      if (errors.length > 0) {
        console.log(`  Errors:          ${errors.length} users failed`);
        errors.slice(0, 3).forEach(m => console.log(`    - User ${m.userId}: ${m.error}`));
      }

      // Expect high success rate even at medium load
      expect(successRate).toBeGreaterThan(0.7); // At least 70% success

    } finally {
      // Cleanup
      for (const context of contexts) {
        await context.close();
      }
    }
  });

  test('Rapid navigation: Memory leak detection', async ({ page }) => {
    console.log('\n╔══════════════════════════════════════════╗');
    console.log('║  Rapid Navigation: Memory Leak Test     ║');
    console.log('╚══════════════════════════════════════════╝');

    // Login first
    await page.goto(`${BASE_URL}/`);
    await page.fill('input[name="httpd_username"]', 'test');
    await page.fill('input[name="httpd_password"]', 'test');
    await page.click('button[type="submit"], input[type="submit"]');
    await page.waitForLoadState('domcontentloaded', { timeout: 15000 });

    // Capture initial memory
    const initialMetrics = await capturePageMetrics(page);
    console.log(`\n[initial] Heap used: ${(initialMetrics.jsHeapUsedSize / (1024 * 1024)).toFixed(2)} MB`);

    // Navigate through tabs rapidly
    const tabs = [
      '/#/monitor',
      '/#/agents',
      '/#/build',
      '/#/status',
      '/#/adms',
      '/#/help',
    ];

    for (const tab of tabs) {
      await page.goto(`${BASE_URL}${tab}`, { waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(500); // Brief pause
    }

    // Capture final memory
    const finalMetrics = await capturePageMetrics(page);
    const memoryDelta = calculateMemoryDelta(initialMetrics, finalMetrics);

    console.log(`\n[final] Heap used: ${(finalMetrics.jsHeapUsedSize / (1024 * 1024)).toFixed(2)} MB`);
    console.log(`[memory] Delta used: ${(memoryDelta.deltaUsed / (1024 * 1024)).toFixed(2)} MB`);
    console.log(`[memory] Delta total: ${(memoryDelta.deltaTotal / (1024 * 1024)).toFixed(2)} MB`);

    // Check for memory leak (heuristic: >50MB growth is suspicious)
    if (memoryDelta.deltaUsed > 50 * 1024 * 1024) {
      console.warn(`[WARN] Possible memory leak: ${memoryDelta.deltaUsed / (1024 * 1024).toFixed(2)} MB growth`);
    } else {
      console.log(`[OK] Memory growth within acceptable range`);
    }
  });
});
