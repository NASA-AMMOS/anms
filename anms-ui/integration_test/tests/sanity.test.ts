/**
 * Sanity check test - verifies Playwright is working correctly.
 * Does not require any services to be running.
 */
import { test, expect } from '@playwright/test';

test.describe('Sanity Check', () => {
  test('Playwright is installed and working', async ({ page }) => {
    await page.goto('data:text/html,<h1>Playwright works!</h1>');
    await expect(page.locator('h1')).toHaveText('Playwright works!');
  });

  test('Can capture page metrics', async ({ page }) => {
    await page.setContent('<html><body><div>Hello World</div></body></html>');
    const elementCount = await page.locator('*').count();
    expect(elementCount).toBeGreaterThan(0);
  });
});
