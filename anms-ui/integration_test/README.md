# ANMS Angular UI — Playwright Integration Tests

Full-stack integration tests for the ANMS Angular UI using Playwright. Tests exercise the
complete stack (Postgres, anms-core, Redis, real amp-manager, ion-manager, Angular UI) through real browser
navigation, measuring performance and reliability.

## Architecture

```
┌───────────────────────────────────────────────────┐
│              Playwright Tests                      │
│  headless chromium ← connects to UI on port 9030  │
│  measures: DOM size, load time, memory, errors    │
└──────────────┬────────────────────────────────────┘
               │ http://ui:9030
┌──────────────┴────────────────────────────────────┐
│              anms-ui (Express)                     │
│  serves: dist/anms-ui/browser/*                   │
│  proxies: /core, /agents, /adms, /api → anms-core │
└──────┬────────────────────────────────────────────┘
       │ internal network
┌──────┴──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  anms-core      │    │ postgres │    │  redis   │    │ amp-mgr  │
│  :5555          │    │ :5432    │    │ :6379    │    │ refdm    │
│  (Flask API)    │    │          │    │          │    │ :8089    │
└─────────────────┘    └──────────┘    └──────────┘    │ (HTTP)   │
                                                      └────┬───────┘
                                                              │ Unix socket
                                                       ┌──────┴───────┐
                                                       │ ion-manager  │
                                                       │ ION DTN (BP) │
                                                       └──────────────┘
```

The real `amp-manager` (refdm-proxy) exposes the HTTP REST API (`/nm/api/*`) and bridges
to ION via a Unix SEQPACKET socket. The `ion-manager` is the DTN node (Bundle Protocol /
LTP over UDP).

## Requirements

- **APL infrastructure** — Requires `privileged: true` mode (NET_ADMIN, NET_RAW, SYS_NICE)
  for the amp-manager and ion-manager containers. These cannot run on restricted Docker
  environments (GitHub Actions, GitLab CI, podman without privileges).
- **`sockdir` external volume** — The Unix socket shared between amp-manager and ion-manager
  uses the same external volume name as production. It must exist:
  ```bash
  docker volume create sockdir
  ```

## Quick Start

### 1. Install dependencies

```bash
cd ~/anms/anms-ui/integration_test
npm install --save-dev @playwright/test
npx playwright install chromium
```

### 2. Ensure sockdir volume exists

```bash
docker volume create sockdir 2>/dev/null || true
```

### 3. Start the test environment

```bash
# Build and start all services
docker compose -f docker-compose-full.yml up -d --build

# Wait ~3-5 minutes for services to be healthy
# Check: docker compose -f docker-compose-full.yml ps
```

### 4. Run the tests

```bash
# Run all tests
npx playwright test

# Run with visible browser (for debugging)
npx playwright test --headed

# Run specific test file
npx playwright test tests/base.test.ts

# Run with HTML report
npx playwright test --reporter=html

# Run with parallelism
npx playwright test --workers 4
```

### 5. Clean up

```bash
docker compose -f docker-compose-full.yml down --remove-orphans
```

## Test Coverage

| Test File | What It Tests | User Guide Section |
|-----------|--------------|-------------------|
| `base.test.ts` | Login/logout, session, profile | User Accounts, Login/Logout |
| `monitor.test.ts` | Monitor tab, Grafana iframe, Infinity datasource | Monitoring |
| `agents.test.ts` | Agent listing, search, detail views, management | Agents |
| `build.test.ts` | ARI Builder, String Input, transcoding, AC Builder | Build |
| `concurrent.test.ts` | N concurrent users, memory leaks, rapid navigation | — |

### Test Spec References

Tests map to the ANMS Test Specification (ANMS_TestSpec_revC_em.docx):

- `ANMS_FUN_APP_001` — Verify login
- `ANMS_FUN_APP_002` — Verify logout
- `ANMS_FUN_APP_004` — Verify default applications (Monitor tab)
- `ANMS_FUN_AGENT_001` — Verify Agent listing
- `ANMS_FUN_BLD_001` — Verify ARI building
- `ANMS_FUN_TRC_001` — Verify ARI transcoding

## Performance Metrics Tracked

Each page navigation captures:

| Metric | Description | Threshold |
|--------|-------------|-----------|
| `domContentLoadedMs` | Time to DOM ready | < 5s |
| `loadEventMs` | Time to full load | < 10s |
| `domElementCount` | Total DOM elements | < 10,000 |
| `jsHeapUsedSize` | JS heap used | < 200 MB |
| `iframeCount` | Number of iframes | Track only |
| `mainThreadBlockedMs` | Estimated blocking time | < 1s |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `http://localhost:9030` | UI server URL |
| `TEST_USERNAME` | `test` | Test login username |
| `TEST_PASSWORD` | `test` | Test login password |
| `ION_MGR_PORT` | `8089` | Host port for amp-manager HTTP API |

### Docker Services

The full stack docker-compose includes:

| Service | Source | Port | Purpose |
|---------|--------|------|---------|
| `postgres` | `postgres:15-alpine` | 5432 | Relational store |
| `redis` | `redis:6.0-alpine` | 6379 | Sessions + caching |
| `anms-core` | `${DOCKER_IMAGE_PREFIX}anms-core` | 5555 | Flask REST API |
| `amp-manager` | `anms.Containerfile::amp-manager` | 8089 | Real refdm-proxy HTTP API |
| `ion-manager` | `anms.Containerfile::ion-manager` | — | Real ION DTN daemon |
| `anms-ui` | `${DOCKER_IMAGE_PREFIX}anms-ui` | 9030/9443 | Angular UI + Express |

## Troubleshooting

### Services not starting

```bash
# Check container logs
docker compose -f docker-compose-full.yml logs -f

# Check individual service health
docker exec -it anms-ui-anms-ui-1 pm2 status
```

### amp-manager takes too long to become healthy

The amp-manager health check waits for the Unix socket `/var/tmp/nm/proxy.sock` to appear.
With ion-manager starting up, this can take 60-90 seconds. The health check retries 30 times
at 2s intervals (60s timeout). If it fails, check ion-manager logs:

```bash
docker compose -f docker-compose-full.yml logs ion-manager
docker compose -f docker-compose-full.yml logs amp-manager
```

### Tests fail to connect

```bash
# Verify UI is accessible
curl http://localhost:9030/

# Verify anms-core API
curl http://localhost:5555/core/hello

# Verify amp-manager REST API
curl http://localhost:8089/nm/api/agents
```

### Playwright can't find selectors

The test selectors are based on the Vue.js → Angular migration. Selectors may need
updating based on the current Angular implementation. Check the browser DevTools
for the actual element attributes and update selectors in test files.

## File Structure

```
anms-ui/integration_test/
├── docker-compose-full.yml      # Full-stack test environment (real amp + ion)
├── config.yaml                  # UI server config
├── playwright.config.ts         # Playwright configuration
├── tests/
│   ├── global-setup.ts          # Playwright global setup
│   ├── global-teardown.ts       # Playwright global teardown
│   ├── base.test.ts             # Authentication + session
│   ├── monitor.test.ts          # Monitor tab + Grafana
│   ├── agents.test.ts           # Agents tab + search
│   ├── build.test.ts            # Build tab + ARI builder
│   └── concurrent.test.ts       # Load testing
├── utils/
│   ├── metrics.ts               # Performance measurement helpers
│   └── api-helpers.ts           # API call + waiting helpers
└── README.md                    # This file
```
