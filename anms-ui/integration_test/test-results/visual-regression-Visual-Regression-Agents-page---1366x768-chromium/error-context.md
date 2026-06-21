# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: visual-regression.test.ts >> Visual Regression >> Agents page - 1366x768
- Location: tests/visual-regression.test.ts:57:9

# Error details

```
Error: expect(page).toHaveScreenshot(expected) failed

  11679 pixels (ratio 0.02 of all image pixels) are different.

  Snapshot: visual-laptop-agents.png

Call log:
  - Expect "toHaveScreenshot(visual-laptop-agents.png)" with timeout 5000ms
    - verifying given screenshot expectation
  - taking page screenshot
    - disabled all CSS animations
  - waiting for fonts to load...
  - fonts loaded
  - 11679 pixels (ratio 0.02 of all image pixels) are different.
  - waiting 100ms before taking screenshot
  - taking page screenshot
    - disabled all CSS animations
  - waiting for fonts to load...
  - fonts loaded
  - captured a stable screenshot
  - 11679 pixels (ratio 0.02 of all image pixels) are different.

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e4]:
    - generic [ref=e8]:
      - generic [ref=e9] [cursor=pointer]: AMMOS ANMS
      - generic [ref=e10]: Version - v2.0.0-11-g80a27c5
      - button [ref=e11] [cursor=pointer]:
        - img [ref=e12]: admin_panel_settings
      - button [ref=e15] [cursor=pointer]:
        - img [ref=e16]: logout
    - generic [ref=e19]:
      - navigation [ref=e23]:
        - link [ref=e24] [cursor=pointer]:
          - /url: /dashboard/home
          - img [ref=e25]: dashboard
        - group [ref=e27]
        - link "Good" [ref=e29] [cursor=pointer]:
          - /url: /dashboard/status
          - img [ref=e30]: checklist
          - generic [ref=e33]: Good
        - link [ref=e34] [cursor=pointer]:
          - /url: /dashboard/adms
          - img [ref=e35]: schema
        - link [ref=e36] [cursor=pointer]:
          - /url: /dashboard/help
          - img [ref=e37]: help
        - separator [ref=e39]
        - link [ref=e40] [cursor=pointer]:
          - /url: "#"
          - img [ref=e41]: navigate_next
      - separator [ref=e43]
      - generic [ref=e44]:
        - list [ref=e48]:
          - listitem
          - listitem [ref=e49]: / dashboard
          - listitem [ref=e50]: / agents
        - generic [ref=e53]:
          - generic [ref=e55]:
            - generic [ref=e56]:
              - textbox "Search by ID String, First Registered, or Last Registered" [ref=e57]
              - button "Search" [ref=e60] [cursor=pointer]
            - generic [ref=e61]:
              - paragraph [ref=e63]: Select Agent to view
              - generic [ref=e64]:
                - button "Manage" [disabled]
            - table [ref=e65]:
              - rowgroup [ref=e66]:
                - row "Select All Agent Endpoint URI First Registered Last Registered" [ref=e67]:
                  - columnheader "Select All" [ref=e68]:
                    - generic [ref=e71] [cursor=pointer]:
                      - checkbox [ref=e73]
                      - generic:
                        - img
                    - text: Select All
                  - columnheader "Agent Endpoint URI" [ref=e74]
                  - columnheader "First Registered" [ref=e75]
                  - columnheader "Last Registered" [ref=e76]
              - rowgroup [ref=e77]:
                - button "ipn:2.6 2026-06-09T21:21:22.307541+00:00 2026-06-11T16:52:06.931390+00:00" [ref=e78] [cursor=pointer]:
                  - cell [ref=e79]:
                    - generic [ref=e82]:
                      - checkbox [ref=e84]
                      - generic:
                        - img
                  - cell "ipn:2.6" [ref=e85]
                  - cell "2026-06-09T21:21:22.307541+00:00" [ref=e86]
                  - cell "2026-06-11T16:52:06.931390+00:00" [ref=e87]
                - button "ipn:3.6 2026-06-09T21:21:22.326750+00:00 2026-06-11T16:52:06.981262+00:00" [ref=e88] [cursor=pointer]:
                  - cell [ref=e89]:
                    - generic [ref=e92]:
                      - checkbox [ref=e94]
                      - generic:
                        - img
                  - cell "ipn:3.6" [ref=e95]
                  - cell "2026-06-09T21:21:22.326750+00:00" [ref=e96]
                  - cell "2026-06-11T16:52:06.981262+00:00" [ref=e97]
            - generic [ref=e98]:
              - generic [ref=e100]:
                - generic [ref=e101]: Agent Address
                - textbox "Add by address" [ref=e102]
                - button "Add" [ref=e103] [cursor=pointer]
              - group [ref=e105]:
                - generic [ref=e107]:
                  - generic [ref=e108]:
                    - generic [ref=e109]: "Items per page:"
                    - combobox "Items per page:" [ref=e114] [cursor=pointer]:
                      - generic [ref=e115]:
                        - generic [ref=e117]: "10"
                        - img [ref=e120]
                  - generic [ref=e123]:
                    - status [ref=e124]: 1 – 2 of 2
                    - button "First page" [disabled] [ref=e125]:
                      - img [ref=e126]
                    - button "Previous page" [disabled] [ref=e130]:
                      - img [ref=e131]
                    - button "Next page" [disabled] [ref=e135]:
                      - img [ref=e136]
                    - button "Last page" [disabled] [ref=e140]:
                      - img [ref=e141]
          - paragraph [ref=e146]: "Amp Version:"
  - alert "failed to reach manager" [ref=e149]
```

# Test source

```ts
  1   | /**
  2   |  * Visual regression tests: Screenshot comparison across breakpoints.
  3   |  *
  4   |  * Takes screenshots at 3 breakpoints and compares against baselines:
  5   |  * - Desktop (1920x1080)
  6   |  * - Laptop (1366x768)
  7   |  * - Tablet (768x1024)
  8   |  *
  9   |  * First run creates baselines — subsequent runs compare.
  10  |  * Baselines stored in tests/__screenshots__/<testname>.png
  11  |  *
  12  |  * Dynamic content handling:
  13  |  * - Agents page: timestamps in "First/Last Registered" columns are masked
  14  |  * - Monitor page: Grafana iframe is replaced with a static placeholder
  15  |  *   (live Grafana data changes between screenshot attempts, making stable
  16  |  *   comparison impossible)
  17  |  * - Dashboard & Reports pages: no dynamic content, standard comparison
  18  |  *
  19  |  * Usage:
  20  |  *   npx playwright test visual-regression.test.ts --update-snapshots   # create baselines
  21  |  *   npx playwright test visual-regression.test.ts                       # compare
  22  |  */
  23  | 
  24  | import { test, expect } from '@playwright/test';
  25  | import { setupAuth } from './auth-setup';
  26  | 
  27  | const BASE_URL = process.env.BASE_URL || 'http://localhost:8084';
  28  | 
  29  | // Breakpoints to test
  30  | const BREAKPOINTS = [
  31  |   { name: 'desktop', width: 1920, height: 1080, label: '1920x1080' },
  32  |   { name: 'laptop', width: 1366, height: 768, label: '1366x768' },
  33  |   { name: 'tablet', width: 768, height: 1024, label: '768x1024' },
  34  | ];
  35  | 
  36  | test.describe('Visual Regression', () => {
  37  |   test.beforeEach(async ({ page }) => {
  38  |     await setupAuth(page);
  39  |   });
  40  | 
  41  |   // Screenshot each page at each breakpoint
  42  |   for (const bp of BREAKPOINTS) {
  43  |     const snapshotName = `${bp.name}`;
  44  |     const baselineName = `visual-${snapshotName}`;
  45  | 
  46  |     test(`Dashboard home page - ${bp.label}`, async ({ page }) => {
  47  |       await page.setViewportSize({ width: bp.width, height: bp.height });
  48  |       await page.goto(BASE_URL);
  49  |       await page.waitForLoadState('domcontentloaded');
  50  |       await page.waitForTimeout(1000); // Wait for Angular rendering
  51  | 
  52  |       await expect(page).toHaveScreenshot(`${baselineName}-dashboard.png`, {
  53  |         threshold: 0.1,
  54  |       });
  55  |     });
  56  | 
  57  |     test(`Agents page - ${bp.label}`, async ({ page }) => {
  58  |       await page.setViewportSize({ width: bp.width, height: bp.height });
  59  |       await page.goto(BASE_URL + '/dashboard/agents');
  60  |       await page.waitForLoadState('domcontentloaded');
  61  | 
  62  |       // Mask dynamic timestamp columns so they don't cause flaky diffs
  63  |       await page.evaluate(() => {
  64  |         // Mask cells with timestamp-like content (ISO dates, etc.)
  65  |         document.querySelectorAll('td, th').forEach(el => {
  66  |           const text = el.textContent?.trim();
  67  |           if (text && /^\d{4}-\d{2}-\d{2}/.test(text)) {
  68  |             el.style.color = 'transparent';
  69  |             el.style.border = 'none';
  70  |             el.style.backgroundColor = 'transparent';
  71  |             el.style.minWidth = el.offsetWidth + 'px';
  72  |             el.style.minHeight = el.offsetHeight + 'px';
  73  |           }
  74  |         });
  75  |       });
  76  | 
  77  |       await page.waitForTimeout(500); // Allow masking to apply
  78  | 
> 79  |       await expect(page).toHaveScreenshot(`${baselineName}-agents.png`, {
      |                          ^ Error: expect(page).toHaveScreenshot(expected) failed
  80  |         threshold: 0.1,
  81  |       });
  82  |     });
  83  | 
  84  |     test(`Reports page - ${bp.label}`, async ({ page }) => {
  85  |       await page.setViewportSize({ width: bp.width, height: bp.height });
  86  |       await page.goto(BASE_URL + '/dashboard/reports');
  87  |       await page.waitForLoadState('domcontentloaded');
  88  |       await page.waitForTimeout(1000);
  89  | 
  90  |       await expect(page).toHaveScreenshot(`${baselineName}-reports.png`, {
  91  |         threshold: 0.1,
  92  |       });
  93  |     });
  94  | 
  95  |     test(`Monitor page - ${bp.label}`, async ({ page }) => {
  96  |       await page.setViewportSize({ width: bp.width, height: bp.height });
  97  |       await page.goto(BASE_URL + '/dashboard/monitor');
  98  |       await page.waitForLoadState('domcontentloaded');
  99  | 
  100 |       // Replace the Grafana iframe with a static placeholder div.
  101 |       // Grafana's live data updates between Playwright's stability check
  102 |       // screenshots, making comparison impossible. Replacing with a
  103 |       // static element ensures consistent screenshots.
  104 |       await page.evaluate(() => {
  105 |         const iframes = document.querySelectorAll('iframe');
  106 |         iframes.forEach(iframe => {
  107 |           // Create a placeholder that mimics a dark Grafana dashboard
  108 |           const placeholder = document.createElement('div');
  109 |           placeholder.style.width = iframe.offsetWidth + 'px';
  110 |           placeholder.style.height = iframe.offsetHeight + 'px';
  111 |           placeholder.style.background = '#1a1a2e';
  112 |           placeholder.style.position = 'absolute';
  113 |           placeholder.style.top = iframe.offsetTop + 'px';
  114 |           placeholder.style.left = iframe.offsetLeft + 'px';
  115 |           placeholder.style.zIndex = '9999';
  116 |           placeholder.style.border = 'none';
  117 |           iframe.style.visibility = 'hidden';
  118 |           iframe.parentNode?.appendChild(placeholder);
  119 |         });
  120 |       });
  121 | 
  122 |       await page.waitForTimeout(1000); // Wait for Angular rendering
  123 | 
  124 |       await expect(page).toHaveScreenshot(`${baselineName}-monitor.png`, {
  125 |         threshold: 0.1,
  126 |       });
  127 |     });
  128 |   }
  129 | });
  130 | 
```