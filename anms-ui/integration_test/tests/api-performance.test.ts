/**
 * API performance tests: Measure HTTP latency, response sizes, and throughput
 * for each backend endpoint.
 */

import { test, expect } from '@playwright/test';
import { setupAuth } from './auth-setup';

import { AUTHNZ_URL } from './config';
const API_BASE = AUTHNZ_URL.replace(/\/$/, '') + '/api';

test.describe('API Performance', () => {
  test('GET /api/core/service_status is fast', async ({ page }) => {
    await setupAuth(page);
    const startTime = Date.now();
    const response = await page.goto(`${API_BASE}/core/service_status`);
    const loadTime = Date.now() - startTime;
    
    expect(response?.status()).toBeLessThan(400);
    expect(loadTime).toBeLessThan(5000);
    console.log(`[api-perf] service_status: ${loadTime}ms`);
  });

  test('GET /api/core/adms returns data', async ({ page }) => {
    await setupAuth(page);
    const startTime = Date.now();
    const response = await page.goto(`${API_BASE}/core/adms`);
    const loadTime = Date.now() - startTime;

    expect(response?.status()).toBeLessThan(500);
    console.log(`[api-perf] adms: ${loadTime}ms`);
  });

  test('GET /api/agents returns data', async ({ page }) => {
    await setupAuth(page);
    const startTime = Date.now();
    const response = await page.goto(`${API_BASE}/agents?page=0&size=10`);
    const loadTime = Date.now() - startTime;

    expect(response?.status()).toBeLessThan(500);
    console.log(`[api-perf] agents: ${loadTime}ms`);
  });

  test('GET /api/build/ari/all returns data', async ({ page }) => {
    await setupAuth(page);
    const startTime = Date.now();
    const response = await page.goto(`${API_BASE}/build/ari/all`);
    const loadTime = Date.now() - startTime;

    expect(response?.status()).toBeLessThan(500);
    console.log(`[api-perf] ari/all: ${loadTime}ms`);
  });

  test('GET /api/report/entry/name/test returns gracefully', async ({ page }) => {
    await setupAuth(page);
    const startTime = Date.now();
    const response = await page.goto(`${API_BASE}/report/entry/name/test`);
    const loadTime = Date.now() - startTime;

    expect(response?.status()).toBeLessThan(500);
    console.log(`[api-perf] report/name/test: ${loadTime}ms, status=${response?.status()}`);
  });

  test('Multiple sequential API calls show stable latency', async ({ page }) => {
    await setupAuth(page);
    const latencies = [];
    
    for (let i = 0; i < 5; i++) {
      const startTime = Date.now();
      await page.goto(`${API_BASE}/core/service_status`);
      const loadTime = Date.now() - startTime;
      latencies.push(loadTime);
    }
    
    const avg = latencies.reduce((a, b) => a + b, 0) / latencies.length;
    const max = Math.max(...latencies);
    const min = Math.min(...latencies);
    
    console.log(`[api-perf] Sequential calls: avg=${Math.round(avg)}ms, min=${min}ms, max=${max}ms`);
    // Max should not be more than 3x average
    expect(max).toBeLessThan(avg * 3);
  });

  test('Concurrent API calls remain responsive', async ({ browser }) => {
    const context = await browser.newContext();
    const pages = await Promise.all(
      Array.from({ length: 5 }, () => context.newPage())
    );
    
    const latencies = await Promise.all(
      pages.map(async (page) => {
        await setupAuth(page);
        const startTime = Date.now();
        await page.goto(`${API_BASE}/core/service_status`);
        return Date.now() - startTime;
      })
    );
    
    const avg = latencies.reduce((a, b) => a + b, 0) / latencies.length;
    console.log(`[api-perf] 5 concurrent API calls: avg=${Math.round(avg)}ms`);
    
    // All should complete within reasonable time
    latencies.forEach((l, i) => {
      expect(l).toBeLessThan(10000);
      console.log(`[api-perf] Call ${i}: ${l}ms`);
    });
    
    await context.close();
  });
});
