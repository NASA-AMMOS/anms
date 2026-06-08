/**
 * Test utilities for measuring Angular UI performance and metrics.
 *
 * Provides helper functions to:
 * - Measure page load times
 * - Count DOM elements
 * - Monitor JavaScript heap usage
 * - Track navigation performance
 */

import { Page, BrowserContext } from '@playwright/test';

export interface PageMetrics {
  /** Time from navigation start to DOMContentLoaded (ms) */
  domContentLoadedMs: number;
  /** Time from navigation start to load event (ms) */
  loadEventMs: number;
  /** Total number of DOM elements */
  domElementCount: number;
  /** JavaScript heap used size (bytes) */
  jsHeapUsedSize: number;
  /** JavaScript heap total size (bytes) */
  jsHeapTotalSize: number;
  /** Number of iframes */
  iframeCount: number;
  /** Number of Angular components (detected by element attributes) */
  angularComponentCount: number;
  /** Main thread blocked time (ms) */
  mainThreadBlockedMs: number;
}

/**
 * Capture comprehensive page metrics.
 */
export async function capturePageMetrics(page: Page): Promise<PageMetrics> {
  return await page.evaluate(async () => {
    // Timing from performance API
    const navigationStart = performance.timing.navigationStart;
    const domContentLoaded = performance.timing.domContentLoadedEventEnd - navigationStart;
    const loadEvent = performance.timing.loadEventEnd - navigationStart;

    // DOM element count
    const domElementCount = document.querySelectorAll('*').length;

    // JavaScript heap usage
    let jsHeapUsedSize = 0;
    let jsHeapTotalSize = 0;
    if (window.performance && (window.performance as any).memory) {
      const memory = (window.performance as any).memory;
      jsHeapUsedSize = memory.usedJSHeapSize;
      jsHeapTotalSize = memory.totalJSHeapSize;
    }

    // Iframe count
    const iframeCount = document.querySelectorAll('iframe').length;

    // Angular components (detected by Angular attribute or ng-version)
    const angularComponentCount = document.querySelectorAll('[ng-version]').length;

    // Main thread blocked time (simplified - check for long tasks)
    let mainThreadBlockedMs = 0;
    if ('PerformanceObserver' in window) {
      // Note: We can't actually observe from here due to async nature,
      // so we use a heuristic: count elements that indicate complex rendering
      const complexElements = document.querySelectorAll(
        'table, mat-table, ag-grid, virtual-repeat, infinite-scroll'
      );
      mainThreadBlockedMs = complexElements.length * 16; // Approximate: 16ms per frame
    }

    return {
      domContentLoadedMs: domContentLoaded,
      loadEventMs: loadEvent,
      domElementCount,
      jsHeapUsedSize,
      jsHeapTotalSize,
      iframeCount,
      angularComponentCount,
      mainThreadBlockedMs,
    };
  });
}

/**
 * Measure the time taken for a page navigation.
 */
export async function measureNavigation(
  page: Page,
  url: string
): Promise<{ url: string; durationMs: number; metrics: PageMetrics }> {
  const startTime = Date.now();
  await page.goto(url, { waitUntil: 'load', timeout: 30000 });
  const durationMs = Date.now() - startTime;
  const metrics = await capturePageMetrics(page);

  return {
    url,
    durationMs,
    metrics,
  };
}

/**
 * Calculate memory delta between two points.
 */
export function calculateMemoryDelta(
  before: PageMetrics,
  after: PageMetrics
): { deltaUsed: number; deltaTotal: number } {
  return {
    deltaUsed: after.jsHeapUsedSize - before.jsHeapUsedSize,
    deltaTotal: after.jsHeapTotalSize - before.jsHeapTotalSize,
  };
}

/**
 * Log metrics to console in a readable format.
 */
export function logMetrics(name: string, metrics: PageMetrics): void {
  const mb = (bytes: number) => `${(bytes / (1024 * 1024)).toFixed(2)} MB`;

  console.log(`\n[metrics] ${name}`);
  console.log(`  DOMContentLoaded: ${metrics.domContentLoadedMs.toFixed(0)}ms`);
  console.log(`  Load Event:       ${metrics.loadEventMs.toFixed(0)}ms`);
  console.log(`  DOM Elements:     ${metrics.domElementCount}`);
  console.log(`  JS Heap Used:     ${mb(metrics.jsHeapUsedSize)}`);
  console.log(`  JS Heap Total:    ${mb(metrics.jsHeapTotalSize)}`);
  console.log(`  Iframes:          ${metrics.iframeCount}`);
  console.log(`  Angular Comps:    ${metrics.angularComponentCount}`);
  console.log(`  Main Thread:      ${metrics.mainThreadBlockedMs}ms (est.)`);
}

/**
 * Check if page has potential performance issues.
 */
export function detectPerformanceIssues(metrics: PageMetrics): string[] {
  const issues: string[] = [];

  // Check DOM size
  if (metrics.domElementCount > 5000) {
    issues.push(`Large DOM: ${metrics.domElementCount} elements (threshold: 5000)`);
  }

  // Check load time
  if (metrics.loadEventMs > 5000) {
    issues.push(`Slow load: ${metrics.loadEventMs.toFixed(0)}ms (threshold: 5s)`);
  }

  // Check iframe count (Grafana iframe issue)
  if (metrics.iframeCount > 0) {
    issues.push(`Iframes present: ${metrics.iframeCount} (may block main thread)`);
  }

  // Check memory growth (heuristic)
  if (metrics.jsHeapTotalSize > 0 && metrics.jsHeapUsedSize > 0) {
    const utilization = metrics.jsHeapUsedSize / metrics.jsHeapTotalSize;
    if (utilization > 0.9) {
      issues.push(`High memory utilization: ${(utilization * 100).toFixed(0)}%`);
    }
  }

  return issues;
}
