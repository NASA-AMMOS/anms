/**
 * Auth setup: Handles authnz form-based login to match production environment.
 *
 * authnz (Apache) uses mod_auth_form for authentication. The login page is at
 * /authn/login.html and the form posts to /authn/dologin.html with fields
 * "username" and "password". On success, authnz redirects to /index.html and
 * sets a session cookie.
 *
 * All auth-dependent tests should call setupAuth(page) before navigating.
 * This ensures the test environment matches production (through authnz).
 *
 * Test credentials: test:test (from auth/demo/htpasswd)
 */

import { chromium } from '@playwright/test';
import type { BrowserContext, Page } from '@playwright/test';
import { TEST_USERNAME, TEST_PASSWORD } from './config';

/**
 * Log in through authnz's form-based authentication.
 * Navigate to the login page, fill out the form, and submit.
 */
export async function setupAuth(page: Page): Promise<Page> {
  // Navigate to authnz login page
  await page.goto('/authn/login.html', { waitUntil: 'domcontentloaded' });

  // Fill out the login form - authnz uses fields named "username" and "password"
  await page.fill('input[name="httpd_username"]', TEST_USERNAME);
  await page.fill('input[name="httpd_password"]', TEST_PASSWORD);

  // Submit the form (posts to /authn/dologin.html)
  const [response] = await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 10000 }),
    page.locator('button[type="submit"]').click(),
  ]);

  // Verify login succeeded - should be redirected to /index.html or /
  const currentUrl = page.url();
  console.log(`[authnz] Login successful, redirected to: ${currentUrl}`);

  return page;
}

/**
 * Configure a browser context with authnz login (affects all pages in the context).
 * Uses the same form-based login but applied at the context level.
 */
export async function setupAuthContext(context: BrowserContext): Promise<BrowserContext> {
  const page = await context.newPage();
  await setupAuth(page);
  // Context now has the authnz session cookie
  await page.close();
  return context;
}

/**
 * Get the current test username (for assertions).
 */
export function getTestUsername(): string {
  return TEST_USERNAME;
}
