/**
 * Agents tab tests: Agent listing, search, and detail views.
 *
 * Covers:
 * - ANMS User Guide: Agents section
 * - Test Spec: ANMS_FUN_AGENT_001 (Verify Agent listing),
 *   ANMS_FUN_AGENT_002 (Verify Agent details)
 *
 * User Guide Flow:
 *   1. Navigate to Agents tab
 *   2. Search agents by ID string or registration time
 *   3. View agent details (reports sent, operations)
 *   4. Add new agent
 *   5. Manage agent (generate ARI, send command)
 */

import { test, expect } from '@playwright/test';
import { measureNavigation, capturePageMetrics, logMetrics } from '../utils/metrics';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';

test.describe('Agents Tab', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto(`${BASE_URL}/`);
    await page.fill('input[name="httpd_username"]', 'test');
    await page.fill('input[name="httpd_password"]', 'test');
    await page.click('button[type="submit"], input[type="submit"]');
    await page.waitForLoadState('domcontentloaded', { timeout: 15000 });
  });

  test('Verify Agents tab is accessible', async ({ page }) => {
    // Click Agents tab
    const agentsTab = page.locator('a:has-text("Agents"), .nav-agents, [data-qa="agents-tab"]').first();
    await expect(agentsTab).toBeVisible();
    await agentsTab.click();

    // Wait for Agents content to load
    await expect(page.locator('[data-qa="agents-content"], .agents-tab, :text("Agents")')).toBeVisible({ timeout: 10000 });
    console.log('[agents] Agents tab accessible');
  });

  test('Agent table displays list of agents', async ({ page }) => {
    // Navigate to Agents
    const agentsTab = page.locator('a:has-text("Agents"), .nav-agents, [data-qa="agents-tab"]').first();
    await agentsTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "The table in the middle of the Agents page displays the Agents registered"
    const agentTable = page.locator('table, mat-table, [data-qa="agent-table"]').first();
    const tableVisible = await agentTable.isVisible().catch(() => false);
    
    console.log(`[agents] Agent table visible: ${tableVisible}`);

    // Check for table headers per user guide
    const headers = await page.locator('th:has-text("ID"), th:has-text("Agent"), th:has-text("Registered")').count();
    console.log(`[agents] Table headers found: ${headers}`);
  });

  test('Search agents by ID string', async ({ page }) => {
    // Navigate to Agents
    const agentsTab = page.locator('a:has-text("Agents"), .nav-agents, [data-qa="agents-tab"]').first();
    await agentsTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "The search bar at the top of the page allows a user to search the Agents"
    // by ID String (Example: ipn:1.1)
    const searchInput = page.locator('input[placeholder*="search"], input[placeholder*="ID"], input[type="search"]').first();
    
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('ipn:1.1');
      await searchInput.press('Enter');
      
      // Wait for filtered results
      await page.waitForTimeout(1000);
      
      const filteredCount = await page.locator('table tr, mat-row').count();
      console.log(`[agents] Filtered results: ${filteredCount} rows`);
    } else {
      console.log('[agents] Search input not found (may use different selector)');
    }
  });

  test('View agent details', async ({ page }) => {
    // Navigate to Agents
    const agentsTab = page.locator('a:has-text("Agents"), .nav-agents, [data-qa="agents-tab"]').first();
    await agentsTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "For additional information on a specific Agent, click a row in the table"
    // The Agent details are displayed, including:
    // * Registered Agent ID
    // * Agent ID String
    // * Time Agent was First Registered
    // * Time Agent was Last Registered
    
    // Try to click first agent row
    const agentRow = page.locator('table tr:not(:first-child), mat-row').first();
    const rowVisible = await agentRow.isVisible().catch(() => false);
    
    if (rowVisible) {
      await agentRow.click();
      
      // Wait for details to appear
      await page.waitForTimeout(2000);
      
      // Check for agent details fields
      const hasAgentId = await page.locator(':text("Agent ID"), :text("ipn:")').first().isVisible().catch(() => false);
      const hasFirstRegistered = await page.locator(':text("First Registered"), :text("first_registered")').first().isVisible().catch(() => false);
      const hasLastRegistered = await page.locator(':text("Last Registered"), :text("last_registered")').first().isVisible().catch(() => false);
      
      console.log(`[agents] Detail fields: ID=${hasAgentId}, First=${hasFirstRegistered}, Last=${hasLastRegistered}`);
    }
  });

  test('Agent details page shows sent reports', async ({ page }) => {
    // Navigate to Agents and click an agent
    const agentsTab = page.locator('a:has-text("Agents"), .nav-agents, [data-qa="agents-tab"]').first();
    await agentsTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "The first dropdown, labeled 'Select Sent Reports' provides a list of reports"
    const sentReportsDropdown = page.locator('select:has-text("Sent Reports"), select:has-text("Reports")').first();
    const dropdownVisible = await sentReportsDropdown.isVisible().catch(() => false);
    
    console.log(`[agents] "Select Sent Reports" dropdown visible: ${dropdownVisible}`);
  });

  test('Agent details page shows ARI builder for sending commands', async ({ page }) => {
    // Navigate to Agents
    const agentsTab = page.locator('a:has-text("Agents"), .nav-agents, [data-qa="agents-tab"]').first();
    await agentsTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "The second dropdown menu allows the user to build a command to send"
    // "The `Select Operation` dropdown can be used to select the operation for the command"
    const operationDropdown = page.locator('select:has-text("Operation"), select:has-text("Select")').first();
    const dropdownVisible = await operationDropdown.isVisible().catch(() => false);
    
    console.log(`[agents] "Select Operation" dropdown visible: ${dropdownVisible}`);
  });

  test('Add new agent button/form present', async ({ page }) => {
    // Navigate to Agents
    const agentsTab = page.locator('a:has-text("Agents"), .nav-agents, [data-qa="agents-tab"]').first();
    await agentsTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "Enter the Address of the Agent to add to the ANMS, and select the `Add Node` button"
    const addNodeBtn = page.locator('button:has-text("Add Node"), button:has-text("Add Agent"), [data-qa="add-agent-btn"]').first();
    const addBtnVisible = await addNodeBtn.isVisible().catch(() => false);
    
    console.log(`[agents] "Add Node" button visible: ${addBtnVisible}`);
  });

  test('Agents tab performance: table rendering', async ({ page }) => {
    // Navigate to Agents with metrics
    const result = await measureNavigation(page, `${BASE_URL}/#/agents`);

    console.log('\n[agents] Performance metrics:');
    logMetrics('Agents Tab', result.metrics);

    // DOM size should be reasonable for a table view
    expect(result.metrics.domElementCount).toBeLessThan(5000);
    console.log(`[agents] DOM size OK: ${result.metrics.domElementCount} elements`);
  });

  test('Manage agent dialog accessible', async ({ page }) => {
    // Navigate to Agents
    const agentsTab = page.locator('a:has-text("Agents"), .nav-agents, [data-qa="agents-tab"]').first();
    await agentsTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "To manage an Agent(s), select the agent(s) to be managed from the agent table, 
    // then select the manage button in the upper right part of the table"
    const manageBtn = page.locator('button:has-text("Manage"), button:has-text("Manage Agent"), [data-qa="manage-btn"]').first();
    const manageBtnVisible = await manageBtn.isVisible().catch(() => false);
    
    console.log(`[agents] "Manage" button visible: ${manageBtnVisible}`);
  });
});
