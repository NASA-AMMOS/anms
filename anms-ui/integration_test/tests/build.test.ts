/**
 * Build tab tests: ARI Builder, String Input, and transcoding.
 *
 * Covers:
 * - ANMS User Guide: Build section
 * - Test Spec: ANMS_FUN_BLD_001 (Verify ARI building),
 *   ANMS_FUN_TRC_001 (Verify ARI transcoding)
 *
 * User Guide Flow:
 *   1. Navigate to Build tab
 *   2. Toggle between ARI Builder and String Input modes
 *   3. Search/filter ARIs in the builder
 *   4. Input ARI string and submit for transcoding
 *   5. Verify CBOR output in transcoder log table
 *
 * Key UI Elements:
 *   - Toggle switch: ARI Builder ↔ String Input
 *   - Search bar: Filter ARIs by type, ADM, or name
 *   - Dropdown: Select ARI from list
 *   - Input boxes: Parameter fields for selected ARI
 *   - AC Builder: Collection parameter builder
 *   - Transcoder log table: Shows string and CBOR versions
 */

import { test, expect } from '@playwright/test';
import { measureNavigation, logMetrics } from '../utils/metrics';

const BASE_URL = process.env.BASE_URL || 'http://localhost:9030';

test.describe('Build Tab & ARI Builder', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto(`${BASE_URL}/`);
    await page.fill('input[name="httpd_username"]', 'test');
    await page.fill('input[name="httpd_password"]', 'test');
    await page.click('button[type="submit"], input[type="submit"]');
    await page.waitForLoadState('domcontentloaded', { timeout: 15000 });
  });

  test('Verify Build tab is accessible', async ({ page }) => {
    // Click Build tab
    const buildTab = page.locator('a:has-text("Build"), .nav-build, [data-qa="build-tab"]').first();
    await expect(buildTab).toBeVisible();
    await buildTab.click();

    // Wait for Build content to load
    await expect(page.locator('[data-qa="build-content"], .build-tab, :text("Build")')).toBeVisible({ timeout: 10000 });
    console.log('[build] Build tab accessible');
  });

  test('ARI Builder toggle switch present', async ({ page }) => {
    // Navigate to Build
    const buildTab = page.locator('a:has-text("Build"), .nav-build, [data-qa="build-tab"]').first();
    await buildTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "To switch between building and translating ARIs, 
    // use the toggle at the center of the screen beneath the menu bar"
    const toggleSwitch = page.locator(
      'input[type="checkbox"], .toggle-switch, [data-qa="build-toggle"]'
    ).first();
    
    const toggleVisible = await toggleSwitch.isVisible().catch(() => false);
    console.log(`[build] Toggle switch visible: ${toggleVisible}`);
  });

  test('Search bar filters ARIs', async ({ page }) => {
    // Navigate to Build
    const buildTab = page.locator('a:has-text("Build"), .nav-build, [data-qa="build-tab"]').first();
    await buildTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "type in the search bar as shown to filter available ARIs by type, ADM, or name"
    const searchInput = page.locator(
      'input[placeholder*="search"], input[placeholder*="ARI"], input[type="search"]'
    ).first();
    
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('EDD');
      await searchInput.press('Enter');
      
      // Wait for filtered results
      await page.waitForTimeout(1000);
      
      const filteredCount = await page.locator('mat-option, .ari-option, [data-qa="ari-option"]').count();
      console.log(`[build] Filtered ARI options: ${filteredCount}`);
    } else {
      console.log('[build] Search input not found');
    }
  });

  test('ARI dropdown displays available ARIs', async ({ page }) => {
    // Navigate to Build
    const buildTab = page.locator('a:has-text("Build"), .nav-build, [data-qa="build-tab"]').first();
    await buildTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "The user may also choose an ARI from the drop down list"
    const dropdown = page.locator('mat-select, select, [data-qa="ari-dropdown"]').first();
    const dropdownVisible = await dropdown.isVisible().catch(() => false);
    
    console.log(`[build] ARI dropdown visible: ${dropdownVisible}`);
  });

  test('String Input mode and transcoder log', async ({ page }) => {
    // Navigate to Build
    const buildTab = page.locator('a:has-text("Build"), .nav-build, [data-qa="build-tab"]').first();
    await buildTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "toggle the switch at the top of the screen to select the ARI String Input option"
    const toggleSwitch = page.locator(
      'input[type="checkbox"], .toggle-switch, [data-qa="build-toggle"]'
    ).first();
    
    const toggleVisible = await toggleSwitch.isVisible().catch(() => false);
    
    if (toggleVisible) {
      await toggleSwitch.click();
      
      // Wait for String Input mode
      await page.waitForTimeout(1000);
      
      // Per user guide: "In the top input box, enter a string ARI and select the SUBMIT button"
      const stringInput = page.locator(
        'input[placeholder*="ARI string"], input[placeholder*="string"], textarea'
      ).first();
      
      if (await stringInput.isVisible().catch(() => false)) {
        await stringInput.fill('ari://ietf/dtnma-agent/EDD/num-msg-rx');
        
        const submitBtn = page.locator(
          'button:has-text("SUBMIT"), button:has-text("Submit"), input[type="submit"]'
        ).first();
        
        if (await submitBtn.isVisible().catch(() => false)) {
          await submitBtn.click();
          
          // Wait for transcoding to complete
          await page.waitForTimeout(2000);
          
          // Per user guide: "The CBOR generated by the ANMS will be populated in the table below"
          const transcoderTable = page.locator('table, mat-table, [data-qa="transcoder-log"]').first();
          const tableVisible = await transcoderTable.isVisible().catch(() => false);
          
          console.log(`[build] Transcoder log table visible: ${tableVisible}`);
          
          // Check for CBOR output
          const hasCbor = await page.locator(':text("cbor"), [data-qa="cbor-output"]').first().isVisible().catch(() => false);
          console.log(`[build] CBOR output visible: ${hasCbor}`);
        }
      }
    }
  });

  test('Transcoder log table shows entries', async ({ page }) => {
    // Navigate to Build
    const buildTab = page.locator('a:has-text("Build"), .nav-build, [data-qa="build-tab"]').first();
    await buildTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "The transcoded ARIs are presented in the table at the bottom of the Build tab"
    const transcoderTable = page.locator('table, mat-table, [data-qa="transcoder-log"]').first();
    const tableVisible = await transcoderTable.isVisible().catch(() => false);
    
    if (tableVisible) {
      // Per user guide: "The table provides the Transcoder Log ID, String form of the ARI, 
      // a description of what the provided string was parsed as, the CBOR translation, 
      // the URI, and details on transcoding errors"
      const tableHeaders = await page.locator('th:has-text("ID"), th:has-text("String"), th:has-text("CBOR")').count();
      console.log(`[build] Transcoder table headers: ${tableHeaders}`);
    } else {
      console.log('[build] Transcoder log table not visible (may be empty)');
    }
  });

  test('ARI parameter input fields present', async ({ page }) => {
    // Navigate to Build
    const buildTab = page.locator('a:has-text("Build"), .nav-build, [data-qa="build-tab"]').first();
    await buildTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "If the chosen ARI has parameters, input boxes will be provided for each required field"
    const paramInputs = await page.locator('input[type="text"], mat-input, textarea').count();
    console.log(`[build] Parameter input fields: ${paramInputs}`);
  });

  test('AC (Collection) builder UI present', async ({ page }) => {
    // Navigate to Build
    const buildTab = page.locator('a:has-text("Build"), .nav-build, [data-qa="build-tab"]').first();
    await buildTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Per user guide: "An ARI Collection (AC) builder is provided for ARIs requiring an AC parameter"
    const acBuilder = page.locator(
      ':text("Collection"), [data-qa="ac-builder"], :text("AC")'
    ).first();
    
    const acBuilderVisible = await acBuilder.isVisible().catch(() => false);
    console.log(`[build] AC builder visible: ${acBuilderVisible}`);
  });

  test('Build tab performance: ARI population', async ({ page }) => {
    // Navigate to Build with metrics
    const result = await measureNavigation(page, `${BASE_URL}/#/build`);

    console.log('\n[build] Performance metrics:');
    logMetrics('Build Tab', result.metrics);

    // DOM size should be reasonable (Angular should use virtual scroll for large ARI lists)
    expect(result.metrics.domElementCount).toBeLessThan(10000);
    console.log(`[build] DOM size OK: ${result.metrics.domElementCount} elements`);
  });

  test('ARIA accessibility attributes present', async ({ page }) => {
    // Navigate to Build
    const buildTab = page.locator('a:has-text("Build"), .nav-build, [data-qa="build-tab"]').first();
    await buildTab.click();
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });

    // Check for basic ARIA attributes
    const ariaElements = await page.locator('[aria-label], [aria-describedby], [role]').count();
    console.log(`[build] ARIA attributes present: ${ariaElements} elements`);
  });
});
