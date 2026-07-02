/**
 * Visual regression tests: Screenshot comparison across breakpoints.
 */

import { test, expect } from '@playwright/test';
import { setupAuth } from './auth-setup';
import { AUTHNZ_URL } from './config';

const BREAKPOINTS = [
  { name: 'desktop', width: 1920, height: 1080, label: '1920x1080' },
  { name: 'laptop', width: 1366, height: 768, label: '1366x768' },
  { name: 'tablet', width: 768, height: 1024, label: '768x1024' },
];

test.describe('Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
  });

  for (const bp of BREAKPOINTS) {
    const baselineName = `visual-${bp.name}`;

    test(`Dashboard home page - ${bp.label}`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto('/');
      await page.waitForLoadState('domcontentloaded');
      await page.waitForSelector('[ng-version]', { timeout: 5000 }).catch(() => {});
      await expect(page).toHaveScreenshot(`${baselineName}-dashboard.png`, { threshold: 0.1 });
    });

    test(`Agents page - ${bp.label}`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto('/dashboard/agents');
      await page.waitForLoadState('domcontentloaded');
      await page.evaluate(() => {
        document.querySelectorAll('td, th').forEach(el => {
          const text = el.textContent?.trim();
          if (text && /^\d{4}-\d{2}-\d{2}/.test(text)) {
            el.style.color = 'transparent';
            el.style.border = 'none';
            el.style.backgroundColor = 'transparent';
            el.style.minWidth = el.offsetWidth + 'px';
            el.style.minHeight = el.offsetHeight + 'px';
          }
        });
      });
      await expect(page).toHaveScreenshot(`${baselineName}-agents.png`, { threshold: 0.1 });
    });

    test(`Reports page - ${bp.label}`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto('/dashboard/reports');
      await page.waitForLoadState('domcontentloaded');
      await page.waitForSelector('[ng-version]', { timeout: 5000 }).catch(() => {});
      await expect(page).toHaveScreenshot(`${baselineName}-reports.png`, { threshold: 0.1 });
    });

    test(`Monitor page - ${bp.label}`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto('/dashboard/monitor');
      await page.waitForLoadState('domcontentloaded');
      await page.evaluate(() => {
        document.querySelectorAll('iframe').forEach(iframe => {
          const placeholder = document.createElement('div');
          placeholder.style.width = iframe.offsetWidth + 'px';
          placeholder.style.height = iframe.offsetHeight + 'px';
          placeholder.style.background = '#1a1a2e';
          placeholder.style.position = 'absolute';
          placeholder.style.top = iframe.offsetTop + 'px';
          placeholder.style.left = iframe.offsetLeft + 'px';
          placeholder.style.zIndex = '9999';
          placeholder.style.border = 'none';
          iframe.style.visibility = 'hidden';
          iframe.parentNode?.appendChild(placeholder);
        });
      });
      await expect(page).toHaveScreenshot(`${baselineName}-monitor.png`, { threshold: 0.1 });
    });
  }
});
