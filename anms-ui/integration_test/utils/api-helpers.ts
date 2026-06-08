/**
 * API helpers for Playwright integration tests.
 *
 * Provides utilities for:
 * - Waiting for backend services to be healthy
 * - Making API calls to anms-core
 * - Seeding test data via API
 */

import { Page } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';

/**
 * Wait for a URL to respond with a 200 status.
 */
export async function waitForUrlHealthy(url: string, maxRetries = 30): Promise<boolean> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, { method: 'GET' });
      if (response.ok) {
        return true;
      }
    } catch (err) {
      // Ignore connection errors, retry
    }
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  return false;
}

/**
 * Wait for the UI to be accessible.
 */
export async function waitForUI(page: Page, maxRetries = 30): Promise<boolean> {
  const healthUrl = `${BASE_URL}/`;
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await page.goto(healthUrl, { waitUntil: 'domcontentloaded', timeout: 5000 });
      if (response && response.status() < 500) {
        return true;
      }
    } catch (err) {
      // Ignore navigation errors, retry
    }
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  return false;
}

/**
 * Wait for the UI to be accessible via Page object.
 * Returns true when page is loaded and responsive.
 */
export async function waitForUIReady(page: Page): Promise<boolean> {
  try {
    // Wait for Angular to bootstrap (ng-version attribute appears)
    await page.waitForSelector('[ng-version]', { timeout: 15000 });
    return true;
  } catch (err) {
    // Fallback: check for page content
    await page.waitForLoadState('load', { timeout: 15000 });
    return true;
  }
}

/**
 * Make an authenticated API call using the UI's session.
 * The UI serves as a proxy to the backend.
 */
export async function makeApiCall(
  page: Page,
  path: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  body?: any
): Promise<{ status: number; data: any }> {
  const url = `${BASE_URL}${path}`;
  
  const options: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (body && (method === 'POST' || method === 'PUT')) {
    options.body = JSON.stringify(body);
  }

  const response = await page.evaluate(
    async ({ url, options }) => {
      try {
        const res = await fetch(url, options);
        const data = await res.json().catch(() => null);
        return { status: res.status, data };
      } catch (err: any) {
        return { status: 0, data: { error: err.message } };
      }
    },
    { url, options }
  );

  return response;
}

/**
 * Check if a route is accessible.
 */
export async function checkRouteAccessible(page: Page, route: string): Promise<{
  accessible: boolean;
  status: number;
  title?: string;
}> {
  try {
    const response = await page.goto(`${BASE_URL}${route}`, {
      waitUntil: 'domcontentloaded',
      timeout: 10000,
    });

    const status = response ? response.status() : 0;
    const title = await page.title();

    return {
      accessible: status < 500,
      status,
      title,
    };
  } catch (err) {
    return {
      accessible: false,
      status: 0,
    };
  }
}
