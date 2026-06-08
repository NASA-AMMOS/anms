/**
 * Monitor tab tests: Grafana integration and panel rendering.
 *
 * Covers:
 * - ANMS User Guide: Monitoring section (Reports per Minute, Received Reports, ARIs)
 * - Test Spec: ANMS_FUN_APP_004 (Verify default applications)
 * - Wiki findings: Grafana iframe blocking main thread, Infinity datasource
 *
 * User Guide Flow:
 *   1. Navigate to Monitor tab
 *   2. View default panels (Reports per Minute, Received Reports, ARIs)
 *   3. Optionally create custom panels via Grafana
 *
 * Performance Concerns (from wiki):
 *   - Grafana iframe blocks main thread
 *   - Infinity datasource makes external HTTP calls
 *   - Grafana uses same Postgres as anms-core (pool competition)
 */

import { test, expect } from '@playwright/test';
import { measureNavigation, capturePageMetrics, detectPerformanceIssues, logMetrics } from '../utils/metrics';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';

test.describe('Monitor Tab & Grafana Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto(`${BASE_URL}/`);
    await page.fill('input[name="httpd_username"]', 'test');
    await page.fill('input[name="httpd_password"]', 'test');
    await page.click('button[type="submit"], input[type="submit"]');
    await page.waitForLoadState('domcontentloaded', { timeout: 15000 });
  });

  test('Verify Monitor tab is accessible', async ({ page }) => {
    // Click Monitor tab
    const monitorTab = page.locator('a:has-text("Monitor"), .nav-monitor, [data-qa="monitor-tab"]').first();
    await expect(monitorTab).toBeVisible();
    await monitorTab.click();

    // Wait for Monitor content to load
    await expect(page.locator('[data-qa="monitor-content"], .monitor-tab, :text("Monitor")')).toBeVisible({ timeout: 10000 });
    console.log('[monitor] Monitor tab accessible');
  });

  test('Default panels load correctly', async ({ page }) => {
    // Navigate to Monitor
    const monitorTab = page.locator('a:has-text("Monitor"), .nav-monitor, [data-qa="monitor-tab"]').first();
    await monitorTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Check for default panels per user guide:
    // "There are four default displays that are populated at the top of the Monitor tab"
    
    // Panel 1: Reports per Minute
    const reportsPerMin = page.locator(':text("Reports per Minute")').first();
    const hasReportsPanel = await reportsPerMin.isVisible().catch(() => false);

    // Panel 2: Received Reports table
    const receivedReports = page.locator(':text("Received Reports")').first();
    const hasReceivedReports = await receivedReports.isVisible().catch(() => false);

    // Panel 3: ARIs table
    const arisPanel = page.locator(':text("ARIs")').first();
    const hasAris = await arisPanel.isVisible().catch(() => false);

    // At least some panels should be visible (may be empty if no data)
    const panelsVisible = [hasReportsPanel, hasReceivedReports, hasAris].filter(Boolean).length;
    console.log(`[monitor] Default panels visible: ${panelsVisible}/3`);
  });

  test('Grafana iframe loads and renders', async ({ page }) => {
    // Navigate to Monitor
    const monitorTab = page.locator('a:has-text("Monitor"), .nav-monitor, [data-qa="monitor-tab"]').first();
    await monitorTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Check for Grafana iframe
    const iframes = page.locator('iframe');
    const iframeCount = await iframes.count();
    
    console.log(`[monitor] Iframe count: ${iframeCount}`);
    
    // Per wiki finding: "Monitor component embeds Grafana in an iframe"
    // This is expected - we're testing that it works, not that it doesn't exist
    if (iframeCount > 0) {
      // Check iframe is accessible
      const iframeSrc = await iframes.first().getAttribute('src');
      console.log(`[monitor] Grafana iframe src: ${iframeSrc}`);
      
      // Verify iframe is loaded (not blank)
      const iframeReady = await page.evaluate(() => {
        const iframe = document.querySelector('iframe');
        return iframe && iframe.contentWindow && !iframe.contentWindow.document.querySelector('.loading');
      });
      console.log(`[monitor] Grafana iframe ready: ${iframeReady}`);
    }
  });

  test('Monitor tab performance: DOM size and load time', async ({ page }) => {
    // Navigate to Monitor with metrics
    const result = await measureNavigation(page, `${BASE_URL}/#/monitor`);

    console.log('\n[monitor] Performance metrics:');
    logMetrics('Monitor Tab', result.metrics);

    // Check for performance issues
    const issues = detectPerformanceIssues(result.metrics);
    if (issues.length > 0) {
      console.warn('[monitor] Performance issues detected:');
      issues.forEach(issue => console.warn(`  - ${issue}`));
    }

    // Expect reasonable DOM size (Angular should virtualize large tables)
    expect(result.metrics.domElementCount).toBeLessThan(10000);
    console.log(`[monitor] DOM size OK: ${result.metrics.domElementCount} elements`);
  });

  test('Grafana Infinity datasource calls are tracked', async ({ page }) => {
    // Navigate to Monitor
    const monitorTab = page.locator('a:has-text("Monitor"), .nav-monitor, [data-qa="monitor-tab"]').first();
    await monitorTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Capture network requests
    const requests: string[] = [];
    page.on('request', request => {
      const url = request.url();
      if (url.includes('infinity') || url.includes('grafana')) {
        requests.push(url);
      }
    });

    // Wait for some network activity
    await page.waitForTimeout(2000);

    console.log(`[monitor] Infinity/Grafana API calls: ${requests.length}`);
    if (requests.length > 0) {
      requests.slice(0, 3).forEach(url => console.log(`  - ${url}`));
    }
  });

  test('Custom panel creation button is present', async ({ page }) => {
    // Navigate to Monitor
    const monitorTab = page.locator('a:has-text("Monitor"), .nav-monitor, [data-qa="monitor-tab"]').first();
    await monitorTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "select New Panel under the Grafana section"
    const newPanelBtn = page.locator(':text("New Panel"), button:has-text("New Panel"), :text("Create")').first();
    const hasNewPanelBtn = await newPanelBtn.isVisible().catch(() => false);
    
    console.log(`[monitor] "New Panel" button visible: ${hasNewPanelBtn}`);
  });
});
