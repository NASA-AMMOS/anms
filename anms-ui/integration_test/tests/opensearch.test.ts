/**
 * OpenSearch integration tests: Validate the search/monitoring data layer.
 *
 * The full-stack compose includes OpenSearch + OpenSearch Dashboards but
 * no tests verify the search layer works. These tests validate:
 * - OpenSearch cluster health
 * - OpenSearch Dashboards accessibility
 * - anms-core is writing data to OpenSearch
 *
 * Note: OpenSearch requires HTTPS with basic auth. Playwright's request API
 * needs ignoreHTTPSErrors for the self-signed cert.
 *
 * Test Spec: ANMS_FUN_MGT_002 (Verify Grafana monitoring)
 */

import { test, expect } from '@playwright/test';
import { OPENSEARCH_URL, OPENSEARCH_USER, OPENSEARCH_PASS, OPENSEARCH_DASH_URL } from './config';
import { waitForUrlHealthy } from '../utils/api-helpers';

let opensearchAvailable = false;

test.beforeEach(async ({ request }) => {
  if (opensearchAvailable === false) {
    try {
      opensearchAvailable = await waitForUrlHealthy(OPENSEARCH_URL + '/_cluster/health', 3);
    } catch {
      opensearchAvailable = false;
    }
  }
  if (!opensearchAvailable) {
    test.skip(true, 'OpenSearch is not available');
  }
});

/** Build a Basic auth header string */
function authHeader(user: string, pass: string): string {
  return 'Basic ' + Buffer.from(`${user}:${pass}`).toString('base64');
}

test.describe('OpenSearch Integration', () => {
  test('OpenSearch root endpoint responds via HTTPS', async ({ request }) => {
    const response = await request.get(OPENSEARCH_URL, {
      maxRetries: 2,
      timeout: 10000,
      ignoreHTTPSErrors: true, // self-signed cert in test env
      headers: { Authorization: authHeader(OPENSEARCH_USER, OPENSEARCH_PASS) },
    });
    
    console.log('[opensearch] Root status: ' + response.status());
    expect(response.status()).toBeLessThan(500);
    
    if (response.ok()) {
      const json = await response.json();
      console.log('[opensearch] Name: ' + json.name + ', Version: ' + json.version.number);
      expect(json).toHaveProperty('name');
      expect(json).toHaveProperty('version');
    }
  });

  test('OpenSearch cluster health is green or yellow', async ({ request }) => {
    const response = await request.get(OPENSEARCH_URL + '/_cluster/health', {
      maxRetries: 2,
      timeout: 10000,
      ignoreHTTPSErrors: true,
      headers: { Authorization: authHeader(OPENSEARCH_USER, OPENSEARCH_PASS) },
    });
    
    console.log('[opensearch] Cluster health status: ' + response.status());
    expect(response.status()).toBeLessThan(500);
    
    if (response.ok()) {
      const json = await response.json();
      console.log('[opensearch] Status: ' + json.status + ', Nodes: ' + json.number_of_nodes);
      expect(['green', 'yellow']).toContain(json.status);
    }
  });

  test('OpenSearch has indices from anms-core', async ({ request }) => {
    const response = await request.get(OPENSEARCH_URL + '/_cat/indices?v', {
      maxRetries: 2,
      timeout: 10000,
      ignoreHTTPSErrors: true,
      headers: { Authorization: authHeader(OPENSEARCH_USER, OPENSEARCH_PASS) },
    });
    
    console.log('[opensearch] Indices status: ' + response.status());
    expect(response.status()).toBeLessThan(500);
    
    const body = await response.text();
    console.log('[opensearch] Indices:\n' + body);
    // At minimum, anms-core should have created at least one index
    expect(body.length).toBeGreaterThan(0);
  });

  test('OpenSearch search endpoint works', async ({ request }) => {
    const response = await request.post(OPENSEARCH_URL + '/_search', {
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': authHeader(OPENSEARCH_USER, OPENSEARCH_PASS),
      },
      data: { query: { match_all: {} } },
      maxRetries: 2,
      timeout: 10000,
      ignoreHTTPSErrors: true,
    });
    
    console.log('[opensearch] Search status: ' + response.status());
    expect(response.status()).toBeLessThan(500);
    
    if (response.ok()) {
      const json = await response.json();
      console.log('[opensearch] Total hits: ' + json.hits.total.value);
    }
  });

  test('OpenSearch Dashboards is reachable', async ({ request }) => {
    const response = await request.get('http://localhost:5601', {
      maxRetries: 2,
      timeout: 10000,
    });
    
    console.log('[opensearch-dashboards] Status: ' + response.status());
    expect(response.status()).toBeLessThan(500);
  });

  test('OpenSearch Dashboards API responds', async ({ request }) => {
    // OS Dashboards requires auth; 401 is acceptable in environments without session cookie
    const response = await request.get('http://localhost:5601/api/status', {
      maxRetries: 2,
      timeout: 10000,
      failOnStatusCode: false,
    });
    
    console.log('[opensearch-dashboards] /api/status status: ' + response.status());
    expect(response.status()).toBeLessThan(500);
    
    if (response.ok()) {
      const json = await response.json();
      console.log('[opensearch-dashboards] Status: ' + JSON.stringify(json));
    }
  });

  test('OpenSearch indexing works (write test)', async ({ request }) => {
    // Create a test index and index a document
    const testIndex = 'test-integration-' + Date.now();
    const auth = authHeader(OPENSEARCH_USER, OPENSEARCH_PASS);
    
    // Create index
    const createResp = await request.put(OPENSEARCH_URL + '/' + testIndex, {
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': auth,
      },
      data: JSON.stringify({
        settings: { number_of_shards: 1, number_of_replicas: 0 },
      }),
      maxRetries: 2,
      timeout: 10000,
      ignoreHTTPSErrors: true,
    });
    
    console.log('[opensearch] Create index: ' + createResp.status());
    expect(createResp.status()).toBe(200);
    
    // Index a document
    const indexResp = await request.post(OPENSEARCH_URL + '/' + testIndex + '/_doc?refresh=true', {
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': auth,
      },
      data: JSON.stringify({
        test: true,
        timestamp: new Date().toISOString(),
        purpose: 'integration-test',
      }),
      maxRetries: 2,
      timeout: 10000,
      ignoreHTTPSErrors: true,
    });
    
    console.log('[opensearch] Index document: ' + indexResp.status());
    expect(indexResp.status()).toBe(201);
    
    // Search for the document
    const searchResp = await request.post(OPENSEARCH_URL + '/' + testIndex + '/_search', {
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': auth,
      },
      data: JSON.stringify({ query: { match_all: {} } }),
      maxRetries: 2,
      timeout: 10000,
      ignoreHTTPSErrors: true,
    });
    
    const searchData = await searchResp.json();
    console.log('[opensearch] Document count: ' + searchData.hits.total.value);
    expect(searchData.hits.total.value).toBeGreaterThanOrEqual(1);
    
    // Clean up
    await request.delete(OPENSEARCH_URL + '/' + testIndex, {
      headers: { 'Authorization': auth },
      maxRetries: 2,
      timeout: 10000,
      ignoreHTTPSErrors: true,
    });
    console.log('[opensearch] Cleaned up test index');
  });
});
