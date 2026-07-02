# ANMS Integration Test Infrastructure Audit Report

**Date:** 2026-07-02
**Scope:** `anms-ui/integration_test/` — 17 test files, 3 utility files, 1 config, 1 shell script

---

## 1. AUTH PATTERNS — Critical: Header-based auth vs real login

### Finding 1.1: `setupAuth()` performs real form-based login, but most tests ignore it

**Severity:** HIGH — Misleading test coverage

`tests/auth-setup.ts` (lines 25–44) correctly implements a form-based login through authnz (`/authn/login.html` with `httpd_username`/`httpd_password` fields). However, every test that calls `setupAuth(page)` immediately discards its results — `setupAuth` returns a page, but the tests then navigate to `BASE_URL` which is usually `http://localhost:9030` (anms-ui directly, NOT through authnz on 8084).

**Impact:** The login flow through authnz is executed, but the page navigated to is the raw UI on port 9030. This means:
- The authnz session cookie is lost (different origin)
- The test effectively tests the UI behind `x-remote-user` header auth (the dev bypass), not through authnz
- The `setupAuth` function gives a false sense of "real authnz testing"

**Files affected:** `base.test.ts:19`, `agents.test.ts:14`, `build.test.ts:14`, `monitor.test.ts:19`, `error-recovery.test.ts:13`, `concurrent.test.ts:19`, `api-performance.test.ts:14`, `navigation.test.ts:15`, `session.test.ts:17`, `grafana-live-reconnect.test.ts:23`, `visual-regression.test.ts:38`, `spec-driven.test.ts:37`

### Finding 1.2: Tests hit different base URLs with different auth expectations

**Severity:** MEDIUM — Coverage gaps

| Base URL | Port | Auth Model | Tests Using It |
|----------|------|------------|----------------|
| `http://localhost:9030` | anms-ui | `x-remote-user` header bypass | base, agents, build, monitor, error-recovery, concurrent, api-performance, navigation, session, grafana-live-reconnect |
| `http://localhost:8084` | authnz proxy | Session cookie (from form login) | grafana-proxy, visual-regression, spec-driven |
| `http://localhost:8084` (via `AUTHNZ_URL`) | authnz proxy | HTTP API (request object) | authnz |

Tests that use port 8084 but still call `setupAuth()` are actually doing two things that conflict: (a) logging in via form to set a cookie, then (b) navigating to the same page that was already loaded by the login redirect. The `setupAuth` on port 8084 pages is partially meaningful, but the test assertions then run against the UI behind the proxy.

### Finding 1.3: Global setup doesn't authenticate

**Severity:** LOW — Structural gap

`tests/global-setup.ts` (lines 20–45) waits for services to be healthy but performs zero authentication. There's no pre-authenticated browser context shared across tests. Each test that needs auth calls `setupAuth` in `beforeEach`, creating redundant login flows.

---

## 2. URL INCONSISTENCY — 2 different BASE_URLs, no unified convention

### Finding 2.1: Inconsistent BASE_URL defaults across test files

**Severity:** MEDIUM — Fragile routing

```
anms-ui (9030):  base.test.ts:14, agents.test.ts:10, build.test.ts:10,
                 monitor.test.ts:15, error-recovery.test.ts:9, concurrent.test.ts:14,
                 api-performance.test.ts:9, navigation.test.ts:10, session.test.ts:13,
                 grafana-live-reconnect.test.ts:18, visual-regression.test.ts:27,
                 spec-driven.test.ts:17

authnz (8084):   grafana-proxy.test.ts:20, visual-regression.test.ts:27, spec-driven.test.ts:17

authnz via AUTHNZ_URL env var: authnz.test.ts:16
```

The playwright.config.ts (line 30) defaults to `http://localhost:8084`, but every individual test file overrides this with its own hardcoded fallback of either `9030` or `8084`. This means:
- `BASE_URL` env var is effectively ignored by most tests
- Each test file has its own copy of the URL constant
- If a port changes, 17 files need updating

### Finding 2.2: Test coverage gap — no test exercises the full authnz → UI path

**Severity:** HIGH — Structural gap

No test navigates through authnz (8084) → redirects to UI (9030) as a user would in production. The `authnz.test.ts` only checks HTTP status codes via `request.get()`, not full browser navigation. The `grafana-proxy.test.ts:98` is the closest, but it runs `setupAuth` then navigates directly to `/dashboard/monitor` — bypassing the authnz redirect flow.

---

## 3. ASSERTION QUALITY — Permissive assertions mask real failures

### Finding 3.1: "It loads" assertions dominate

**Severity:** HIGH — Low signal-to-noise

The majority of tests check only `toBeDefined()`, `toBeTruthy()`, or `toBeLessThan(500/10000/15000)`. These assertions pass if the page exists at all, regardless of correctness.

| File | Line | Assertion | Issue |
|------|------|-----------|-------|
| `base.test.ts` | 38 | `bodyCount > 0` | `body` always exists |
| `error-recovery.test.ts` | 20, 38, 56, 101 | `toBeDefined()` | Almost no-op |
| `error-recovery.test.ts` | 122 | `body > 0` | Body always has elements |
| `build.test.ts` | 40 | `bodyCount > 0` | Always true |
| `navigation.test.ts` | 57 | `toBeDefined()` | No meaningful check |
| `spec-driven.test.ts` | 118 | `rowCount >= 0` | Always true |
| `api-performance.test.ts` | 31, 42, 52, 62 | No assertions | Tests only log |

### Finding 3.2: Tests with no assertions at all

**Severity:** HIGH — Silent pass

The following tests have zero assertions (they only log):

- `api-performance.test.ts:35` — `GET /api/agents` — no assertion
- `api-performance.test.ts:46` — `GET /api/build/ari/all` — no assertion
- `api-performance.test.ts:55` — `GET /api/report/entry/name/test` — no assertion
- `agents.test.ts:32` — "Agents table present" — no assertion
- `agents.test.ts:43` — "Search input exists" — no assertion
- `build.test.ts:45` — "Transcoder log access" — no assertion
- `grafana-live-reconnect.test.ts:26` — "Live endpoint accessible" — no assertion

These tests will pass even if the entire feature is broken.

### Finding 3.3: Only a minority of tests have meaningful assertions

**Severity:** MEDIUM — Inconsistent quality

Tests with decent assertions:
- `monitor.test.ts:27` — checks `bodyText.length > 0` AND `iframe.toBeVisible()`
- `session.test.ts:21` — checks `app-root` element count
- `spec-driven.test.ts:50-58` — checks specific panel names exist
- `spec-driven.test.ts:96` — checks table headers contain "Endpoint"
- `spec-driven.test.ts:308-310` — checks ADM columns
- `visual-regression.test.ts` — screenshot comparison (meaningful but fragile)

---

## 4. waitForTimeout ANTI-PATTERNS — 39 occurrences, many replaceable

### Finding 4.1: 39 `waitForTimeout()` calls total

**Severity:** HIGH — Brittle, flaky

| File | Count | Typical usage |
|------|-------|---------------|
| `spec-driven.test.ts` | 15 | Waiting for UI to render after navigation/form interaction |
| `error-recovery.test.ts` | 5 | Waiting for routed API errors to propagate |
| `navigation.test.ts` | 5 | Waiting after tab clicks and page cycles |
| `grafana-live-reconnect.test.ts` | 3 | Waiting for iframe to load |
| `visual-regression.test.ts` | 4 | Waiting for Angular rendering / masking |
| `agents.test.ts` | 2 | Waiting after navigation |
| `build.test.ts` | 2 | Waiting after navigation |
| `concurrent.test.ts` | 1 | Brief pause between reloads |
| `monitor.test.ts` | 1 | Waiting for iframe |

### Finding 4.2: Replaceable patterns

**Severity:** HIGH — Direct improvement opportunities

These `waitForTimeout` calls should use explicit waiting:

| File:Line | Current | Should be |
|-----------|---------|-----------|
| `agents.test.ts:26` | `waitForTimeout(1000)` after `goto('/dashboard/agents')` | `expect(page.locator('app-agents')).toBeVisible()` |
| `build.test.ts:24` | `waitForTimeout(1000)` after `goto('/dashboard/builder')` | `expect(page.locator('app-builder')).toBeVisible()` |
| `monitor.test.ts:64` | `waitForTimeout(3000)` to let iframe load | `expect(page.locator('iframe')).toBeVisible()` (already used elsewhere) |
| `error-recovery.test.ts:34,52,98,118` | `waitForTimeout(2000)` after API interception | `page.waitForResponse(...)` for the expected error response |
| `spec-driven.test.ts:30` | `waitForTimeout(2000)` in `goToTab` | `page.waitForFunction` (already has one) — redundant |
| `spec-driven.test.ts:112` | `waitForTimeout(1000)` after search | `page.waitForResponse` for search API |
| `spec-driven.test.ts:130` | `waitForTimeout(500)` after row click | `expect(page.locator('.agent-details')).toBeVisible()` |
| `spec-driven.test.ts:424` | `waitForTimeout(3000)` after status refresh | `page.waitForResponse` for status API |
| `spec-driven.test.ts:571` | `waitForTimeout(2000)` after 404 nav | `expect(page.locator('body')).toBeVisible()` |
| `visual-regression.test.ts:50` | `waitForTimeout(1000)` for Angular | `expect(page.locator('app-root')).toBeVisible()` |

---

## 5. BRITTLE SELECTORS — CSS selectors that will break on minor DOM changes

### Finding 5.1: Union selectors that match too broadly

**Severity:** MEDIUM

| File:Line | Selector | Issue |
|-----------|----------|-------|
| `base.test.ts:32` | `mat-toolbar, app-header, header, .mat-toolbar, [class*="toolbar"]` | `header` matches every `<header>` element; `[class*="toolbar"]` matches any class containing "toolbar" |
| `agents.test.ts:37` | `[data-qa*="agent"], :text("Agents"), app-agents` | `:text("Agents")` matches any element with "Agents" text anywhere; `.first()` hides strict mode violations |
| `agents.test.ts:52` | `input[placeholder*="Search"], input[matInput]` | Generic input selectors match any search field on the page |
| `build.test.ts:34` | `app-builder, :text("ARI"), :text("Build")` | `:text("Build")` is extremely broad — could match any "Build" text on the page |
| `build.test.ts:55` | `:text("Transcoder"), :text("CBOR"), mat-paginator` | Text-based selectors are brittle to i18n changes |
| `navigation.test.ts:18` | `[routerlink], [data-nav], .nav-item a, mat-tab` | `[routerlink]` matches every Angular route link; too broad |
| `navigation.test.ts:46` | `a, button, [role="button"], mat-tab, mat-sidenav a` | Matches literally every clickable element on the page |
| `spec-driven.test.ts:44` | `.card-header` | Generic class — will match any card anywhere |
| `spec-driven.test.ts:108` | `button.btn-outline-secondary` | Generic button class, could match in any section |
| `spec-driven.test.ts:447` | `.user-ribbon, [data-qa="user"], .top-ribbon .username, nav .user-name` | Union of 4 broad selectors |

### Finding 5.2: Overuse of `.first()` to work around strict mode

**Severity:** MEDIUM — Masks selector ambiguity

19 uses of `.first()` across the test suite (documented in search results above). This pattern suppresses Playwright's strict mode violations but doesn't fix the root cause — the selector matches multiple elements. The right fix is to use more specific selectors (e.g., `page.locator('app-agents table')` instead of `page.locator('table').first()`).

---

## 6. DUPLICATE TEST LOGIC — Repeated patterns not centralized

### Finding 6.1: Auth setup duplicated in every test file

**Severity:** LOW — Cosmetic but structural

Every test file individually:
```typescript
import { setupAuth } from './auth-setup';
const BASE_URL = process.env.BASE_URL || 'http://localhost:XXXXX';
```

This pattern is repeated in 12 files. The `BASE_URL` default is especially duplicated with 3 different values.

### Finding 6.2: Memory leak detection duplicated verbatim

**Severity:** MEDIUM — Maintenance burden

The same quartile-analysis pattern appears in:
- `concurrent.test.ts:93-117` — "Memory leak detection — 50 page reloads"
- `navigation.test.ts:65-89` — "Memory stable after 50 page cycles"

Both use identical logic:
```typescript
const firstQuartile = readings.slice(0, 12).reduce(...) / 12;
const lastQuartile = readings.slice(37).reduce(...) / 13;
expect(lastQuartile).toBeLessThan(firstQuartile * 2);
```

This should be in `utils/metrics.ts` as `detectMemoryLeak(readings: number[])`.

### Finding 6.3: Dashboard navigation pattern duplicated

**Severity:** MEDIUM

The `goToTab` helper in `spec-driven.test.ts:21-31` does navigation + wait that's also manually replicated in:
- `agents.test.ts:17-25`
- `build.test.ts:17-25`
- `spec-driven.test.ts` (inline in multiple tests)

### Finding 6.4: Console error collection duplicated

**Severity:** LOW

The pattern `page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()) })` appears in:
- `monitor.test.ts:53-59`
- `grafana-live-reconnect.test.ts:51-57`

Should be a `waitForConsoleErrors(page, filter?)` utility.

---

## 7. CONFIG INCONSISTENCIES — playwright.config.ts gaps

### Finding 7.1: Timeout mismatch

**Severity:** MEDIUM

`playwright.config.ts:39` sets `timeout: 30000` (30s) globally, but individual tests override:
- `concurrent.test.ts:94` — `test.setTimeout(120000)` — 120s for memory leak test
- `navigation.test.ts:66` — `test.setTimeout(120000)` — 120s for memory leak test

These 2x60s tests are 4x the global timeout. If more long-running tests are added, the gap will widen.

### Finding 7.2: Retries only on CI

**Severity:** MEDIUM

`playwright.config.ts:45` — `retries: process.env.CI ? 2 : 0`. Tests run locally with zero retries, meaning local flakiness goes undetected. Tests that use `waitForTimeout` (inherently flaky) are especially at risk of failing locally due to timing differences.

### Finding 7.3: No test timeout per-file configuration

**Severity:** LOW

Some tests have meaningful assertions and quick timeouts (10s), while others that are essentially `waitForTimeout`-based can take much longer. There's no correlation between test complexity and timeout. A 50-reload memory test (120s) and a "does the page load" test (30s) share the same default.

### Finding 7.4: Single browser project

**Severity:** LOW

`playwright.config.ts:71-79` — only Chromium is configured. This is acknowledged as intentional, but there's no note about whether the app has been tested with any other browser, and the Angular Material components may render differently.

---

## 8. ERROR HANDLING — Mixed strategies, inconsistent resilience

### Finding 8.1: Tests silently pass when prerequisites are missing

**Severity:** MEDIUM

When Grafana isn't running, `monitor.test.ts:66-67` says "iframe may show Page Not Found — that's expected" and the test passes. When OpenSearch isn't running, `opensearch.test.ts:63` checks `response.status() < 500` which would fail if the service is down (no fallback). The inconsistency means:
- Some tests convert missing services into false positives
- Others convert missing services into false negatives

### Finding 8.2: Global setup fails silently

**Severity:** MEDIUM

`tests/global-setup.ts:27-42` — if a service times out, it logs "timeout (may not be started)" and continues. The tests then proceed, producing either false positives (passing vacuously) or false negatives (crashing). There's no mechanism to:
- Skip tests whose prerequisites aren't met
- Fail fast if critical services are missing
- Retry service health checks with exponential backoff

### Finding 8.3: Error-recovery tests have no cleanup

**Severity:** LOW

`error-recovery.test.ts` uses `page.route()` to intercept and manipulate API responses, but these routes may persist across test boundaries if not properly cleaned up. Playwright should auto-clean, but if a test crashes mid-route, subsequent tests inherit the route.

### Finding 8.4: `grafana-live-reconnect.test.ts:26` — "reconnection" test doesn't test reconnection

**Severity:** HIGH — Misleading test name

The test file claims to test "Grafana Live WebSocket reconnection" and "Simulates network conditions (offline, slow, intermittent)" in the header comment (lines 4-5). But the actual tests just check:
1. That the live endpoint is accessible
2. That the monitor page loads
3. That there are no console errors

No actual network simulation, reconnection testing, or WebSocket disruption occurs. The test name and description are aspirational but unimplemented.

---

## Summary of Findings by Severity

| Severity | Count | Key Areas |
|----------|-------|-----------|
| **HIGH** | 7 | Auth model mismatch, URL fragmentation, missing assertions, waitForTimeout anti-patterns, misleading test names |
| **MEDIUM** | 9 | Brittle selectors, duplicate logic, timeout gaps, inconsistent error handling |
| **LOW** | 4 | Cosmetic duplication, config notes, route cleanup |

## Recommended Priority Actions

1. **Unified BASE_URL** — Remove per-file BASE_URL constants; have all tests read from `playwright.config.ts` or a shared `test-urls.ts` module
2. **Fix auth model** — Either test authnz flow end-to-end (login → redirect → UI) or explicitly acknowledge these are `x-remote-user` bypass tests
3. **Add assertions** — Convert `toBeDefined()` and `toBeTruthy()` to meaningful checks; remove or add assertions to the 6 tests with zero assertions
4. **Replace waitForTimeout** — Prioritize the 15 most problematic calls in `spec-driven.test.ts` and `error-recovery.test.ts`
5. **Deduplicate memory leak detection** — Move the quartile analysis to `utils/metrics.ts`
6. **Fix grafana-live-reconnect** — Either implement actual reconnection testing or rename to reflect its actual scope
