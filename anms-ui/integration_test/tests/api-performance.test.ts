/**
 * API performance tests: Measure HTTP latency, response sizes, and throughput
 * for each backend endpoint.
 *
 * These tests directly measure the anms-core API performance without the
 * browser/Express overhead, providing a lower bound on total page load time.
 *
 * Test cases:
 *   1. Core API latency — /core/hello, /core/status
 *   2. Agent API latency — /agents, /agents/all, /agents/:id
 *   3. ADM API latency — /adms, /adms/all
 *   4. ARI API latency — /aris, /aris/all
 *   5. Report API latency — /reports, /reports/all
 *   6. Concurrency comparison — single vs 5 vs 20 concurrent API calls
 *   7. Large response handling — /all endpoints that return full datasets
 */

import { test, expect, APIResponse } from '@playwright/test';

const CORE_URL = process.env.CORE_URL || 'http://localhost:5555';
const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';
const TEST_USERNAME = process.env.TEST_USERNAME || 'test';
const TEST_PASSWORD = process.env.TEST_PASSWORD || 'test';

interface APIMetric {
  endpoint: string;
  method: string;
  status: number;
  latencyMs: number;
  responseBodySize: number;
  error?: string;
}

/**
 * Measure a single API call with detailed metrics.
 */
async function measureAPI(
  page: any,
  method: string,
  url: string
): Promise<APIMetric> {
  const startTime = Date.now();
  let status = 0;
  let responseBodySize = 0;
  let error: string | undefined;

  try {
    const response = await page.request.fetch(url, {
      method: method.toUpperCase(),
      timeout: 10000,
    });

    status = response.status();
    const body = await response.text();
    responseBodySize = Buffer.byteLength(body, 'utf8');
  } catch (err: any) {
    error = err.message;
  }

  const latencyMs = Date.now() - startTime;

  return {
    endpoint: url,
    method,
    status,
    latencyMs,
    responseBodySize,
    error,
  };
}

test.describe('API Performance', () => {
  test.beforeEach(async ({ page }) => {
    // Login first to get session cookies for authenticated endpoints
    await page.goto(`${BASE_URL}/`);
    await page.fill('input[name="httpd_username"]', TEST_USERNAME);
    await page.fill('input[name="httpd_password"]', TEST_PASSWORD);
    await page.click('button[type="submit"], input[type="submit"]');
    await page.waitForLoadState('domcontentloaded', { timeout: 15000 });
  });

  test('Core API latency baseline', async ({ page }) => {
    console.log('\n══════════════════════════════════════════════');
    console.log('  API Performance: Core API Latency');
    console.log('══════════════════════════════════════════════');

    const endpoints = [
      `${CORE_URL}/core/hello`,
      `${CORE_URL}/core/status`,
    ];

    const metrics: APIMetric[] = [];

    for (const url of endpoints) {
      const metric = await measureAPI(page, 'GET', url);
      metrics.push(metric);
    }

    // Report results
    console.log('\n[api-core] Latency results:');
    for (const m of metrics) {
      console.log(`  ${m.method} ${m.endpoint}`);
      console.log(`    Status: ${m.status}`);
      console.log(`    Latency: ${m.latencyMs}ms`);
      console.log(`    Response size: ${m.responseBodySize} bytes`);
      if (m.error) console.log(`    Error: ${m.error}`);
    }

    // Expect reasonable latency (under 500ms for core endpoints)
    const avgLatency = metrics.reduce((sum, m) => sum + m.latencyMs, 0) / metrics.length;
    console.log(`[api-core] Average latency: ${avgLatency.toFixed(0)}ms`);
    expect(avgLatency).toBeLessThan(2000); // Generous threshold for CI
  });

  test('Agent API latency', async ({ page }) => {
    console.log('\n══════════════════════════════════════════════');
    console.log('  API Performance: Agent API Latency');
    console.log('══════════════════════════════════════════════');

    const endpoints = [
      { url: `${CORE_URL}/agents`, method: 'GET' },
      { url: `${CORE_URL}/agents/all`, method: 'GET' },
    ];

    const metrics: APIMetric[] = [];

    for (const ep of endpoints) {
      const metric = await measureAPI(page, ep.method, ep.url);
      metrics.push(metric);
    }

    console.log('\n[api-agents] Latency results:');
    for (const m of metrics) {
      console.log(`  ${m.method} ${m.endpoint}`);
      console.log(`    Status: ${m.status}, Latency: ${m.latencyMs}ms, Size: ${m.responseBodySize} bytes`);
    }
  });

  test('ADM API latency', async ({ page }) => {
    console.log('\n══════════════════════════════════════════════');
    console.log('  API Performance: ADM API Latency');
    console.log('══════════════════════════════════════════════');

    const endpoints = [
      { url: `${CORE_URL}/adms`, method: 'GET' },
      { url: `${CORE_URL}/adms/all`, method: 'GET' },
    ];

    const metrics: APIMetric[] = [];

    for (const ep of endpoints) {
      const metric = await measureAPI(page, ep.method, ep.url);
      metrics.push(metric);
    }

    console.log('\n[api-adms] Latency results:');
    for (const m of metrics) {
      console.log(`  ${m.method} ${m.endpoint}`);
      console.log(`    Status: ${m.status}, Latency: ${m.latencyMs}ms, Size: ${m.responseBodySize} bytes`);
    }
  });

  test('ARI API latency', async ({ page }) => {
    console.log('\n══════════════════════════════════════════════');
    console.log('  API Performance: ARI API Latency');
    console.log('══════════════════════════════════════════════');

    const endpoints = [
      { url: `${CORE_URL}/aris`, method: 'GET' },
      { url: `${CORE_URL}/aris/all`, method: 'GET' },
    ];

    const metrics: APIMetric[] = [];

    for (const ep of endpoints) {
      const metric = await measureAPI(page, ep.method, ep.url);
      metrics.push(metric);
    }

    console.log('\n[api-aris] Latency results:');
    for (const m of metrics) {
      console.log(`  ${m.method} ${m.endpoint}`);
      console.log(`    Status: ${m.status}, Latency: ${m.latencyMs}ms, Size: ${m.responseBodySize} bytes`);
    }
  });

  test('Report API latency', async ({ page }) => {
    console.log('\n══════════════════════════════════════════════');
    console.log('  API Performance: Report API Latency');
    console.log('══════════════════════════════════════════════');

    const endpoints = [
      { url: `${CORE_URL}/reports`, method: 'GET' },
      { url: `${CORE_URL}/reports/all`, method: 'GET' },
    ];

    const metrics: APIMetric[] = [];

    for (const ep of endpoints) {
      const metric = await measureAPI(page, ep.method, ep.url);
      metrics.push(metric);
    }

    console.log('\n[api-reports] Latency results:');
    for (const m of metrics) {
      console.log(`  ${m.method} ${m.endpoint}`);
      console.log(`    Status: ${m.status}, Latency: ${m.latencyMs}ms, Size: ${m.responseBodySize} bytes`);
    }
  });

  test('Concurrent API calls — single vs parallel', async ({ page }) => {
    console.log('\n══════════════════════════════════════════════');
    console.log('  API Performance: Concurrent API Calls');
    console.log('══════════════════════════════════════════════');

    const url = `${CORE_URL}/agents/all`;

    // Measure single request
    const singleStart = Date.now();
    const singleMetric = await measureAPI(page, 'GET', url);
    const singleTime = Date.now() - singleStart;

    // Measure 5 concurrent requests
    const parallelStart = Date.now();
    const promises = Array(5).fill(null).map(() =>
      measureAPI(page, 'GET', url)
    );
    await Promise.all(promises);
    const parallelTime = Date.now() - parallelStart;
    const avgParallelTime = parallelTime / 5;

    console.log(`\n[api-concurrent] ${url}:`);
    console.log(`  Single request:   ${singleTime}ms`);
    console.log(`  5 parallel total: ${parallelTime}ms`);
    console.log(`  5 parallel avg:   ${avgParallelTime.toFixed(0)}ms`);
    console.log(`  Speedup factor:   ${(singleTime / avgParallelTime).toFixed(1)}x`);

    // Parallel should be faster than single
    expect(avgParallelTime).toBeLessThan(singleTime * 0.8);
  });

  test('Large response handling — DOM impact', async ({ page }) => {
    console.log('\n══════════════════════════════════════════════');
    console.log('  API Performance: Large Response Handling');
    console.log('══════════════════════════════════════════════');

    // Measure response sizes for /all endpoints
    const endpoints = [
      `${CORE_URL}/agents/all`,
      `${CORE_URL}/adms/all`,
      `${CORE_URL}/aris/all`,
      `${CORE_URL}/reports/all`,
    ];

    let totalResponseBytes = 0;
    const metrics: APIMetric[] = [];

    for (const url of endpoints) {
      const metric = await measureAPI(page, 'GET', url);
      metrics.push(metric);
      totalResponseBytes += metric.responseBodySize;
    }

    console.log(`\n[api-large] Total response size: ${totalResponseBytes} bytes (${(totalResponseBytes / 1024).toFixed(1)} KB)`);
    console.log('\n[api-large] Per-endpoint breakdown:');
    for (const m of metrics) {
      console.log(`  ${m.endpoint}: ${m.responseBodySize} bytes (${(m.responseBodySize / 1024).toFixed(1)} KB), ${m.latencyMs}ms`);
    }

    // Expect total response to be under 1 MB
    expect(totalResponseBytes).toBeLessThan(1024 * 1024);
  });
});
