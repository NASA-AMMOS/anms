/**
 * Base tests: Authentication, session management, and page loading.
 *
 * Covers:
 * - ANMS User Guide: User Accounts and Login/Logout
 * - Test Spec: ANMS_FUN_APP_001 (Verify login), ANMS_FUN_APP_002 (Verify logout)
 *
 * User Guide Flow:
 *   1. User accesses ANMS URL
 *   2. Browser redirects to login page
 *   3. User enters credentials (form-based auth)
 *   4. On success, top ribbon appears with username
 *   5. Logout link ends session
 */

import { test, expect } from '@playwright/test';

// Configuration from .env or defaults
const TEST_USERNAME = process.env.TEST_USERNAME || 'test';
const TEST_PASSWORD = process.env.TEST_PASSWORD || 'test';
const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';

test.describe('Authentication & Session Management', () => {
  test('Verify login page is accessible', async ({ page }) => {
    // Navigate to base URL - should redirect to login
    const response = await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });

    // Check we get a 200 or 302 (redirect to login)
    expect(response?.status()).toBeLessThan(400);
    console.log(`[base] Login page accessible, status: ${response?.status()}`);
  });

  test('Perform login with valid credentials', async ({ page }) => {
    // Navigate to login page
    await page.goto(`${BASE_URL}/`);

    // Fill in credentials
    await page.fill('input[name="httpd_username"]', TEST_USERNAME);
    await page.fill('input[name="httpd_password"]', TEST_PASSWORD);

    // Submit login form
    await page.click('button[type="submit"], input[type="submit"]');

    // Wait for navigation to dashboard/home
    await page.waitForLoadState('domcontentloaded', { timeout: 15000 });

    // Verify top ribbon appears with username
    // The ribbon should contain the username after successful login
    const ribbon = await page.locator('[data-qa="user-ribbon"], .top-ribbon, :text("test")').first();
    
    // Check for successful login indicators
    // Either username in ribbon OR dashboard content
    const hasUsername = await page.locator(':text("test")').first().isVisible();
    const hasDashboard = await page.locator('[data-qa="dashboard"], .dashboard').first().isVisible();
    
    expect(hasUsername || hasDashboard).toBe(true);
    console.log('[base] Login successful, dashboard accessible');
  });

  test('Top ribbon shows username after login', async ({ page }) => {
    // Login first
    await page.goto(`${BASE_URL}/`);
    await page.fill('input[name="httpd_username"]', TEST_USERNAME);
    await page.fill('input[name="httpd_password"]', TEST_PASSWORD);
    await page.click('button[type="submit"], input[type="submit"]');
    await page.waitForLoadState('domcontentloaded', { timeout: 15000 });

    // Check that username appears in top ribbon
    // Per user guide: "the current account name is displayed in the top ribbon"
    const username = await page.locator(':text("test")').first();
    await expect(username).toBeVisible({ timeout: 5000 });
    console.log('[base] Username visible in top ribbon');
  });

  test('Navigate to login/logout page via user profile', async ({ page }) => {
    // Login
    await page.goto(`${BASE_URL}/`);
    await page.fill('input[name="httpd_username"]', TEST_USERNAME);
    await page.fill('input[name="httpd_password"]', TEST_PASSWORD);
    await page.click('button[type="submit"], input[type="submit"]');
    await page.waitForLoadState('domcontentloaded', { timeout: 15000 });

    // Click user account link in ribbon
    const userLink = page.locator(':text("test"), .user-profile-link').first();
    await expect(userLink).toBeVisible();
    await userLink.click();

    // Verify profile page loads
    // User Guide: "Selecting the user account link will show the user's profile page"
    await expect(page.locator('input[name="username"]')).toBeVisible({ timeout: 10000 });
    console.log('[base] User profile page accessible');
  });

  test('Verify logout ends session', async ({ page, context }) => {
    // Login
    await page.goto(`${BASE_URL}/`);
    await page.fill('input[name="httpd_username"]', TEST_USERNAME);
    await page.fill('input[name="httpd_password"]', TEST_PASSWORD);
    await page.click('button[type="submit"], input[type="submit"]');
    await page.waitForLoadState('domcontentloaded', { timeout: 15000 });

    // Click logout
    const logoutLink = page.locator(':text("Logout"), a:has-text("Logout")').first();
    await expect(logoutLink).toBeVisible();
    await logoutLink.click();

    // Should redirect back to login page
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });
    
    // Check for login form elements
    const hasLoginForm = await page.locator('input[name="httpd_username"]').count();
    expect(hasLoginForm).toBeGreaterThan(0);
    console.log('[base] Logout successful, redirected to login page');
  });

  test('Verify error handling for invalid credentials', async ({ page }) => {
    // Navigate to login
    await page.goto(`${BASE_URL}/`);

    // Try invalid credentials
    await page.fill('input[name="httpd_username"]', 'invalid');
    await page.fill('input[name="httpd_password"]', 'invalid');
    await page.click('button[type="submit"], input[type="submit"]');

    // Should stay on login page or show error
    // User Guide doesn't specify exact error handling, but should not crash
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });
    
    // Should still be on login page (not redirected to dashboard)
    const hasLoginForm = await page.locator('input[name="httpd_username"]').count();
    expect(hasLoginForm).toBeGreaterThan(0);
    console.log('[base] Invalid credentials handled gracefully');
  });
});
