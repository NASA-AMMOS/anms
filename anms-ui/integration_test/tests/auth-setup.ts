/**
 * Auth setup: Configures Playwright pages with the x-remote-user header
 * for integration test auth bypass. All auth-dependent tests should
 * call setupAuth() on their page before navigating.
 *
 * The anms-ui server (main.js) checks this header and sets req.user
 * if no session auth is present.
 */

import { chromium } from '@playwright/test';
import type { BrowserContext, Page } from '@playwright/test';

const TEST_USERNAME = process.env.TEST_USERNAME || 'test';

/**
 * Configure a page with auth header and return it.
 */
export async function setupAuth(page: Page): Promise<Page> {
  await page.setExtraHTTPHeaders({
    'x-remote-user': TEST_USERNAME,
  });
  return page;
}

/**
 * Configure a browser context with auth header (affects all pages in the context).
 */
export async function setupAuthContext(context: BrowserContext): Promise<BrowserContext> {
  await context.addInitScript(() => {
    // Set global variable for tests to reference
    (window as any).__TEST_USERNAME = TEST_USERNAME;
  });
  return context;
}

/**
 * Get the current test username (for assertions).
 */
export function getTestUsername(): string {
  return TEST_USERNAME;
}
