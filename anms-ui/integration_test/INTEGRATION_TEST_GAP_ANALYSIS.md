# ANMS Integration Test Infrastructure: Comprehensive Gap Analysis

**Date:** 2026-07-02
**Scope:** `anms-ui/integration_test/` — Playwright test suite, compose infrastructure, seeding pipeline, CI readiness
**Sources Reviewed:**
- Wiki: `investigations/32`, `36`, `30`, `31`, `decisions.md`, `spec-extraction/03`
- Infra: `playwright.config.ts`, `global-setup.ts`, `global-teardown.ts`, `start-integration-tests.sh`
- Compose: `docker-compose-full.yml`, `docker-compose-testenv.yml`, `docker-compose-full-podman-override.yml`
- Seeds: `seed_agents.py`, `seed_dashboard.py`
- Tests: `spec-driven.test.ts`, `agents.test.ts`, `base.test.ts`, `auth-setup.ts`, `opensearch.test.ts`
- CI: `.github/workflows/build-test.yaml`, `.github/workflows/anms-core.yaml`
- Audit: `AUDIT_REPORT.md`, `TESTING.md`

---

## 1. Global Setup/Teardown Lifecycle

### 1.1 Setup Waits for Wrong Services — CRITICAL FLAKINESS RISK
**Severity: HIGH**

`tests/global-setup.ts` waits for 4 services:
| Service | Port | Status |
|---------|------|--------|
| anms-ui | 9030 | ✅ Waited |
| authnz | 8084 | ✅ Waited |
| OpenSearch | 9200 | ✅ Waited |
| OpenSearch Dashboards | 5601 | ✅ Waited |
| **anms-core** | **5555** | ❌ NOT waited |
| **amp-manager** | **8089** | ❌ NOT waited |
| **postgres** | **5432** | ❌ NOT waited |
| **grafana** | **3000** | ❌ NOT waited |

**Impact:** Tests may start while `anms-core` or `amp-manager` are still initializing. The `anms-core` Flask app needs to connect to postgres and run migrations before the API is usable. The `amp-manager` needs the ion-manager Unix socket to appear. This creates flaky failures — tests pass on slow machines (services happened to be ready) and fail on fast ones (services not yet started).

**Fix:** Add health checks for anms-core (`/core/hello`), amp-manager (`/nm/api/agents`), postgres (`pg_isready`), and grafana (`/api/health`) to `global-setup.ts`.

### 1.2 Global Teardown Now Has Implementation — BUT Has Race Condition
**Severity: MEDIUM**

The previous audit (6/30) found `global-teardown.ts` was empty. It has since been implemented with runtime detection and auto-compose-down. However:

- **Race condition:** The teardown function uses `execSync` synchronously. If Playwright's exit is triggered by a test error (uncaught exception), the teardown may not complete if the process is killed forcefully.
- **No env var validation:** The teardown reads `INTEGRATION_TEST_COMPOSE` env var, but `start-integration-tests.sh` sets it on line 113. However, if tests are run directly with `npx playwright test` (without the shell script), this env var is not set, and the teardown defaults to `docker-compose-full.yml` — which may not match what's actually running.
- **Podman override detection is fragile:** Uses `getPodmanOverride()` to derive filename from base compose name, but the derived path uses `join(testDir, '..', override)` which assumes the override is always in the parent directory.

### 1.3 No Data Seeding in Global Setup
**Severity: HIGH**

The global-setup comment states: *"Seeding is handled separately via seed scripts in tests/seed/"* but there is **no call to any seed script** anywhere in the test lifecycle:
- `global-setup.ts` — no seeding
- `global-teardown.ts` — no seeding
- `start-integration-tests.sh` — no seeding
- `playwright.config.ts` — no seeding
- No test file calls seed scripts

**Impact:** Tests run against whatever data state the database has from previous runs, or empty. The `seed_agents.py` and `seed_dashboard.py` scripts exist but are completely orphaned — they must be run manually before tests, and there's no automation ensuring this.

---

## 2. Health Check Coverage — Shell Script vs. Global Setup Mismatch

### 2.1 `start-integration-tests.sh` Also Missing Critical Health Checks
**Severity: HIGH**

The shell script's `wait_for_url` calls also have gaps:

**Full mode waits for:** authnz (80), anms-ui (9030), opensearch (9200), grafana (3000)
**Missing:** anms-core (5555), amp-manager (8089), postgres (5432)

**Testenv mode waits for:** anms-ui (9031) only
**Missing:** anms-core (5555), amp-manager (8089), postgres (5432), redis (6379)

This is a **dual gap** — both the shell script AND `global-setup.ts` miss the same services. The most impactful missing check is `anms-core` (5555) because:
- Tests make API calls to `/api/core/*` endpoints
- If anms-core is not ready, API calls fail with connection refused
- The service takes ~30-60 seconds to fully initialize after postgres/redis are ready

### 2.2 All Health Checks Use HTTP Polling — No Service-Level Health Awareness
**Severity: MEDIUM**

`waitForUrlHealthy()` in `utils/api-helpers.ts` does simple HTTP GET polling. It does not:
- Check compose file healthcheck definitions
- Use `docker compose ps --filter health=healthy`
- Implement exponential backoff (uses fixed 1-second intervals)
- Distinguish between "service not started" vs "service crashed" vs "service slow to respond"

---

## 3. Compose File Coverage — Full Stack Is Comprehensive

### 3.1 Full Stack (docker-compose-full.yml) ✅ Adequate
Services included:
| Category | Services | Status |
|----------|----------|--------|
| DB | postgres, redis | ✅ |
| Backend | anms-core, amp-manager | ✅ |
| DTN | ion-manager, ion-agent2, ion-agent3 | ✅ |
| Frontend | anms-ui | ✅ |
| Search | opensearch, opensearch-dashboards | ✅ |
| Monitoring | grafana, grafana-image-renderer | ✅ |
| Auth | authnz (disabled by default) | ⚠️ Disabled |
| Admin | adminer | ✅ |
| Pipeline | mqtt-broker, transcoder, aricodec | ✅ |

### 3.2 Testenv (docker-compose-testenv.yml) ✅ Adequate
Lightweight subset: postgres, redis, anms-core, ion-manager, amp-manager, anms-ui
Missing only: authnz, grafana, opensearch, adminer — acceptable for fast CI.

### 3.3 authnz Service Disabled
**Severity: LOW**

authnz requires TLS certs from `ammos-tls` volume. Tests work around this with `x-remote-user` header bypass on port 9030. This is acceptable for integration tests but means there is **no test coverage of the full authnz → redirect → UI flow**.

---

## 4. Test Configuration Gaps

### 4.1 No Test Tagging/Grouping or Sharding
**Severity: MEDIUM**

`playwright.config.ts`:
- Single project (Chromium only)
- `workers: undefined` locally, `workers: 1` on CI
- No `grep` patterns or test tagging
- No shard configuration

**Impact:** Cannot run subsets of tests (e.g., "only agents tab tests", "only error-recovery"). Cannot parallelize tests on CI (critical for reducing CI time). All 40+ tests run sequentially on CI, taking ~2 minutes minimum with no room for growth.

**Fix:** Add test tagging with `@smoke`, `@regression`, `@api` metadata. Configure multiple worker processes on CI.

### 4.2 No Test File Organization by Spec Section
**Severity: LOW**

Tests are organized by feature area (agents, build, monitor, etc.) which is reasonable. However, there's no mapping file or naming convention that makes it obvious which spec section each test covers. The `spec-driven.test.ts` file attempts to address this by embedding spec IDs (e.g., `ANMS_EXP_DAP_001`) in test describe blocks, but individual test files (`agents.test.ts`, `build.test.ts`) do not carry spec IDs.

### 4.3 Timeout Configuration
**Severity: LOW**

Global timeout: 30s. Two tests override to 120s for memory leak detection. No per-file or per-suite timeout configuration. Tests with `waitForTimeout` anti-patterns (39 occurrences per AUDIT_REPORT) will have unpredictable runtimes.

---

## 5. CI Readiness — INCOMPLETE

### 5.1 No Dedicated Playwright Integration Test Workflow
**Severity: HIGH**

**Current CI workflows:**
- `build-test.yaml` — Runs `checkout-test/run.sh` (not Playwright tests)
- `anms-core.yaml` — Runs anms-core integration tests (Postman/newman)
- `aricodec.yaml`, `transcoder.yaml` — Component-specific

**Missing:** A workflow that runs `npx playwright test` in `anms-ui/integration_test/`.

### 5.2 Environment Requirements Not Documented for CI
**Severity: MEDIUM**

The README notes the tests require:
- **`privileged: true`** mode for amp-manager and ion-manager (NET_ADMIN, NET_RAW, SYS_NICE)
- **`sockdir` external volume** must pre-exist
- **Rocky Linux 9** environment
- **APL infrastructure** cannot run on restricted Docker environments

**CI implication:** GitHub Actions runners have Docker but **not privileged mode** for containers. This means Playwright integration tests **cannot run on standard GitHub Actions** without workarounds:
1. Use `self-hosted` runners with privileged mode
2. Use `docker-compose-testenv.yml` (no ion-manager/amp-manager — but then no real DTN tests)
3. Use a different test runner environment (GitLab self-hosted, custom VM)

### 5.3 CI Env Var Requirements
**Required env vars for CI:**
| Variable | Needed? | Default | CI Override Needed? |
|----------|---------|---------|---------------------|
| `BASE_URL` | Yes | `localhost:8084` | May need override |
| `TEST_USERNAME` | Optional | `test` | No |
| `TEST_PASSWORD` | Optional | `test` | No |
| `DB_USER` | Optional | `root` | No |
| `DB_PASSWORD` | Optional | `changeme` | No |
| `DB_NAME` | Optional | `amp_core` | No |
| `DOCKER_IMAGE_PREFIX` | Optional | `ghcr.io/nasa-ammos/anms/` | No |
| `OPENSEARCH_INITIAL_ADMIN_PASSWORD` | Yes | hardcoded fallback | Should be env var |
| `HOST_SOCKDIR` | Yes | `/var/tmp/nm` | May differ in CI |
| `INTEGRATION_TEST_COMPOSE` | Yes | `docker-compose-full.yml` | Should be set explicitly |

### 5.4 Podman Support Not Auto-Discovered in CI
**Severity: LOW**

`start-integration-tests.sh` auto-detects podman. `global-teardown.ts` auto-detects podman. But the CI workflows don't set `DOCKER_CMD`, so they default to docker. If a GitLab CI runner has only podman, there's no automatic fallback.

---

## 6. Data Seeding Pipeline — COMPLETELY ORPHANED

### 6.1 Seed Scripts Exist But Are Never Called
**Severity: HIGH**

| Script | Purpose | Called By |
|--------|---------|-----------|
| `seed_agents.py` | Creates 100+ agents in PostgreSQL | **NOWHERE** |
| `seed_dashboard.py` | Seeds OpenSearch indices + Grafana datasource | **NOWHERE** |
| `seed_full.py` | **Does not exist** | N/A |

There is no `seed_full.py` or equivalent orchestrator script. The two seed scripts operate independently:
- `seed_agents.py` connects directly to PostgreSQL using imported `anms-core` models
- `seed_dashboard.py` connects to OpenSearch via HTTP REST API

**What needs to happen to wire them in:**

1. **Create `seed_full.py`** (or add seeding to `global-setup.ts`):
   ```python
   # seed_full.py
   import subprocess
   subprocess.run(['python', 'tests/seed/seed_agents.py', '--reset'], check=True)
   subprocess.run(['python', 'tests/seed/seed_dashboard.py', '--reset'], check=True)
   ```

2. **Replace hardcoded path in seed_agents.py** (line 27):
   ```python
   # Current (broken in CI):
   sys.path.insert(0, '/home/greennm1/anms/anms-core')
   # Should be:
   ANMS_ROOT = os.environ.get('ANMS_ROOT', '/home/greennm1/anms')
   sys.path.insert(0, os.path.join(ANMS_ROOT, 'anms-core'))
   ```

3. **Integrate into global-setup.ts:**
   - After all services are healthy, spawn `seed_full.py` subprocess
   - Wait for completion before tests start
   - Handle seed failures by failing the setup (not continuing to broken state)

4. **Add seed isolation:** Tests should seed a clean state before each test suite (not rely on previous state). Consider `seed_reset` in `beforeAll` per test file.

### 6.2 Seed Scripts Use Hardcoded Paths
`seed_agents.py` line 27:
```python
sys.path.insert(0, '/home/greennm1/anms/anms-core')
```
This will **fail in CI** where the repo may be at `/home/runner/work/anms/anms` or similar.

### 6.3 Seed Scripts Have No Teardown/Cleanup Between Tests
`seed_agents.py` has `--reset` flag that clears all agents. But there's no per-test cleanup, meaning:
- Agent count grows across test files
- Test assertions about "X agents in table" may fail if previous tests added agents
- OpenSearch index accumulates documents across test runs

---

## 7. OpenSearch Password — FRAGILE `.env` File Parsing
**Severity: MEDIUM**

`tests/opensearch.test.ts` lines 27-44:
```typescript
function getOpenSearchPassword(): string {
  const envPath = path.resolve(__dirname, '../../../.env');
  try {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    const match = envContent.match(/^OPENSEARCH_INITIAL_ADMIN_PASSWORD=(.+)$/m);
    // ...
  } catch {
    console.warn('[opensearch] WARNING: Could not read password from .env, using default');
    return 'Str0ng!Pass#2026';
  }
}
```

**Problems:**
1. **Path resolution is fragile:** `path.resolve(__dirname, '../../../.env')` assumes a fixed directory structure relative to the test file. In CI, different test runner configurations may resolve differently.
2. **Secret parsing from file:** Other parts of the codebase use `process.env.OPENSEARCH_INITIAL_ADMIN_PASSWORD` for configuration. This test bypasses that convention and reads the file directly.
3. **Silent fallback to hardcoded default:** If the `.env` file is missing or the regex doesn't match, it silently falls back to `'Str0ng!Pass#2026'`. This means tests could be authenticating with the wrong password against a differently-configured OpenSearch instance, causing misleading failures.

**Fix:** Use `process.env.OPENSEARCH_INITIAL_ADMIN_PASSWORD` as the primary source, falling back to `'Str0ng!Pass#2026'` only as a last resort:
```typescript
const OPENSEARCH_PASS = process.env.OPENSEARCH_INITIAL_ADMIN_PASSWORD || 'Str0ng!Pass#2026';
```

---

## 8. Outstanding Priorities from Wiki

### 8.1 From `36-stress-test-and-integration-test-cleanup-audit.md`
| Priority | Item | Status |
|----------|------|--------|
| P0 | Fix `global-teardown.ts` | ✅ FIXED (implementation now exists) |
| P0 | Fix `stress-test-harder.sh` trap overwrite | ⚠️ OUTSTANDING (stress scripts, not integration tests) |
| P0 | Fix `stress-test-detailed.sh` cleanup | ⚠️ OUTSTANDING (stress scripts) |
| P1 | Auto-podman-detection in integration tests | ✅ PARTIALLY FIXED (teardown auto-detects, setup doesn't) |
| P1 | Create podman overrides for `docker-compose.yml` | ⚠️ Partially done (override exists but not auto-applied in CI) |

### 8.2 From `32-anms-testing-architecture-review.md`
- **Authentication model mismatch:** Tests login via authnz form but then navigate directly to port 9030 (bypassing authnz). The AUDIT_REPORT (Finding 1.1) confirms this gives a "false sense of real authnz testing."
- **URL fragmentation:** 17 test files each have their own `BASE_URL` constant with different defaults (9030 or 8084), ignoring the centralized `playwright.config.ts` value.

### 8.3 From `AUDIT_REPORT.md`
| Severity | Finding | Action |
|----------|---------|--------|
| HIGH | 39 `waitForTimeout()` calls | Replace with explicit waits |
| HIGH | 6 tests with zero assertions | Add meaningful assertions |
| HIGH | Misleading test name: `grafana-live-reconnect` | Fix or rename |
| MEDIUM | Brittle CSS selectors (19 `.first()` usages) | Add `data-qa` attributes |
| MEDIUM | Memory leak detection duplicated verbatim | Centralize to `utils/metrics.ts` |
| MEDIUM | Tests silently pass when prerequisites missing | Add prerequisite checks with skip |

### 8.4 From `30-playwright-expanded-test-suite.md`
- Test spec mapping exists but is incomplete — not all 45 spec cases have test implementations
- `spec-driven.test.ts` covers ~20 of 45 spec cases

### 8.5 From `03-extraction-summary.md` (Spec Extraction)
- 45 test cases mapped across 6 domain areas
- Coverage gap: Build tab tests cover only 3 of 10 spec cases (ANMS_FUN_BLD_001 through BLD_010)
- System Admin tests (ANMS_FUN_SYS_001, EXP_SYS_001/002) are present but may have weak assertions

---

## 9. Summary: Gap Priority Matrix

### P0 — Must Fix (blocking CI deployment, causes consistent flakiness)

| # | Gap | Impact | Effort |
|---|-----|--------|--------|
| 1 | **Health checks missing for anms-core, amp-manager, postgres** | Tests start before services ready → flaky failures | Low (add 4 health check URLs to global-setup.ts and start-integration-tests.sh) |
| 2 | **Data seeding never wired in** | Tests run on unpredictable data state | Medium (create seed orchestrator, integrate into global-setup.ts) |
| 3 | **No dedicated CI workflow for Playwright tests** | Integration tests never run in CI | Medium (create `.github/workflows/integration-test.yaml`) |
| 4 | **OpenSearch password uses file parsing instead of env var** | Silent fallback to hardcoded password; path fragility | Low (use `process.env.OPENSEARCH_INITIAL_ADMIN_PASSWORD`) |

### P1 — Should Fix (significant reliability improvements)

| # | Gap | Impact | Effort |
|---|-----|--------|--------|
| 5 | **Testenv mode health checks too sparse** (only waits for anms-ui) | Same flakiness risk in fast CI mode | Low (add health checks for anms-core, postgres) |
| 6 | **39 `waitForTimeout()` calls** replaceable with explicit waits | Brittle, timing-dependent failures | Medium (systematic replacement across 10+ test files) |
| 7 | **6 tests with zero assertions** | Silent passes on broken features | Low (add meaningful assertions or remove test) |
| 8 | **`INTEGRATION_TEST_COMPOSE` env var not set by default** | Teardown may use wrong compose file | Low (set default in playwright.config.ts) |
| 9 | **No test tagging/sharding** | Cannot run subsets or parallelize on CI | Medium (add @tags, configure workers) |

### P2 — Nice to Have (quality of life improvements)

| # | Gap | Impact | Effort |
|---|-----|--------|--------|
| 10 | **Brittle CSS selectors** (19 `.first()` usages) | Maintenance burden on UI changes | Medium (add `data-qa` attributes) |
| 11 | **Memory leak detection code duplicated** | Copy-paste maintenance | Low (centralize to `utils/metrics.ts`) |
| 12 | **Hardcoded path in seed_agents.py** | Seeds fail in CI | Low (use env var for ANMS root path) |
| 13 | **authnz disabled in full stack** | No coverage of real auth flow | Low-High (requires TLS cert setup) |

---

## 10. Recommended Action Plan

### Immediate (1-2 weeks)
1. Add health checks for anms-core (5555), amp-manager (8089), postgres (5432) to both `global-setup.ts` and `start-integration-tests.sh`
2. Fix OpenSearch password to use `process.env.OPENSEARCH_INITIAL_ADMIN_PASSWORD`
3. Create basic CI workflow skeleton that runs Playwright tests with `docker-compose-testenv.yml` (no privileged mode needed)
4. Set `INTEGRATION_TEST_COMPOSE` default in `playwright.config.ts`

### Short-term (2-4 weeks)
5. Wire seed scripts into global-setup.ts — create `seed_all.py` orchestrator, call from global-setup after services are healthy
6. Replace top 15 most impactful `waitForTimeout()` calls with explicit waits
7. Add assertions to the 6 zero-assertion tests

### Medium-term (1-2 months)
8. Create podman override for `docker-compose.yml` (foundational, affects stress-test.sh users)
9. Add test tagging system (`@smoke`, `@regression`) and configure sharding
10. Fix `grafana-live-reconnect.test.ts` — either implement actual reconnection testing or rename
