# ANMS Angular UI — Playwright Integration Tests

Full-stack integration tests for the ANMS Angular UI using Playwright. Tests exercise the
complete stack (Postgres, anms-core, Redis, real amp-manager, ion-manager, Angular UI) through real browser
navigation, measuring performance and reliability.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Full Stack (docker-compose-full.yml)           │
│                                                                     │
│  authnz (demo mode — disabled, requires TLS certs)                  │
│  adminer (dev tool)                                                 │
│  opensearch + opensearch-dashboards (search/monitoring)             │
│  grafana + grafana-image-renderer (dashboarding)                    │
│  postgres (database)                                                │
│  redis (session/cache)                                              │
│  anms-core (Flask REST API)                                         │
│  anms-ui (Angular UI + Express proxy)                               │
│  amp-manager (refdm-proxy — HTTP REST API ↔ DTN socket)             │
│  ion-manager (DTN management daemon — creates Unix socket)          │
│  ion-agent2, ion-agent3 (DTN agents — full ION mesh)                │
│  mqtt-broker, transcoder, aricodec (external transcode pipeline)    │
│                                                                     │
│  Playwright tests → UI:9030 → /api/nm/* → amp-manager:8089         │
│                     → /api/core/* → anms-core:5555                  │
│                     → postgres:5432, redis:6379                     │
│                                                                     │
│  amp-manager ↔ ion-manager via /var/tmp/nm/proxy.sock (Unix socket) │
└─────────────────────────────────────────────────────────────────────┘
```

The real `amp-manager` (refdm-proxy) exposes the HTTP REST API (`/nm/api/*`) and bridges
to ION via a Unix SEQPACKET socket. The `ion-manager` is the DTN node (Bundle Protocol /
LTP over UDP).

## Two Compose Files

| File | Services | Use case |
|------|----------|----------|
| `docker-compose-full.yml` | ALL services (authnz, adminer, opensearch, grafana, postgres, redis, anms-core, anms-ui, amp-manager, ion-manager, ion-agent2/3, mqtt, transcoder, aricodec) | Full-stack integration test, stress testing |
| `docker-compose-testenv.yml` | postgres, redis, anms-core, ion-manager, amp-manager, anms-ui | Fast CI runs, Angular UI-only testing |

## Requirements

- **APL infrastructure** — Requires `privileged: true` mode (NET_ADMIN, NET_RAW, SYS_NICE)
  for the amp-manager and ion-manager containers. These cannot run on restricted Docker
  environments (GitHub Actions, GitLab CI, podman without privileges).
- **`sockdir` external volume** — The Unix socket shared between amp-manager and ion-manager
  uses the same external volume name as production. It must exist:
  ```bash
  docker volume create sockdir
  ```
- **Rocky Linux 9** — Only Chromium browser is supported (Firefox/WebKit require GTK4 which is not available in EL9 repos).

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
# Full stack (all services — mirrors stress-test.sh exactly)
docker compose -f docker-compose-full.yml up -d --build

# Or lightweight (faster — just the UI + backend services)
docker compose -f docker-compose-testenv.yml up -d --build

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
# or for lightweight:
docker compose -f docker-compose-testenv.yml down --remove-orphans
```

## Test Coverage

| Test File | What It Tests | User Guide Section |
|-----------|--------------|-------------------|
| `base.test.ts` | Login/logout, session, profile | User Accounts, Login/Logout |
| `monitor.test.ts` | Monitor tab, Grafana iframe, Infinity datasource | Monitoring |
| `agents.test.ts` | Agent listing, search, detail views, management | Agents |
| `build.test.ts` | ARI Builder, String Input, transcoding, AC Builder | Build |
| `concurrent.test.ts` | N concurrent users, memory leaks, rapid navigation | — |
| `api-performance.test.ts` | API latency per endpoint, concurrency comparison | — |
| `navigation.test.ts` | Tab switching latency, memory leak over 50 cycles | — |
| `session.test.ts` | Session persistence, concurrent sessions, cross-tab logout | — |
| `error-recovery.test.ts` | 500 errors, timeout, offline, 429, malformed JSON | — |

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

Copy `.env` to `.env.local` for local overrides. All variables have sensible defaults.

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCKER_IMAGE_PREFIX` | `ghcr.io/nasa-ammos/anms/` | Docker image prefix |
| `DOCKER_IMAGE_TAG` | `latest` | Docker image tag |
| `DB_USER` | `root` | PostgreSQL user |
| `DB_PASSWORD` | `changeme` | PostgreSQL password |
| `DB_NAME` | `amp_core` | PostgreSQL database name |
| `BASE_URL` | `http://localhost:9030` | UI server URL |
| `AUTHNZ_PORT` | `80` | Authnz HTTP port |
| `OPENSEARCH_PORT1` | `9200` | OpenSearch HTTP port |
| `OPENSEARCH_PORT2` | `9600` | OpenSearch transport port |
| `OPENSEARCH_DASH_PORT` | `5601` | OpenSearch Dashboards port |
| `OPENSEARCH_INITIAL_ADMIN_PASSWORD` | `Str0ng!Pass#2026` | OpenSearch admin password (must be ≥8 chars) |
| `ADMINER_PORT` | `8080` | Adminer dev tool port |
| `RENDERER_PORT` | `8081` | Grafana image renderer port |
| `ION_MGR_PORT` | `8089` | Host port for amp-manager HTTP API |
| `HOST_SOCKDIR` | `/var/tmp/nm` | Host path for Unix socket |
| `CTR_SOCKDIR` | `/var/tmp/nm` | Container path for Unix socket |

### Docker Services

**Full stack (`docker-compose-full.yml`):**

| Service | Source | Port | Purpose |
|---------|--------|------|---------|
| `postgres` | `anms.Containerfile::anms-sql` | 5432 | Relational store (with init scripts) |
| `redis` | `redis:6.0-alpine` | 6379 | Sessions + caching |
| `anms-core` | `${DOCKER_IMAGE_PREFIX}anms-core` | 5555 | Flask REST API |
| `anms-ui` | `${DOCKER_IMAGE_PREFIX}anms-ui` | 9030/9443 | Angular UI + Express |
| `amp-manager` | `anms.Containerfile::amp-manager` | 8089 | Real refdm-proxy HTTP API |
| `ion-manager` | `ghcr.io/nasa-ammos/anms/ion-manager` | — | Real ION DTN daemon (privileged) |
| `ion-agent2` | `ghcr.io/nasa-ammos/anms/ion-agent` | 1113/udp, 4556/udp | DTN agent node 2 (privileged) |
| `ion-agent3` | `ghcr.io/nasa-ammos/anms/ion-agent` | 1113/udp, 4556/udp | DTN agent node 3 (privileged) |
| `grafana` | `anms.Containerfile::grafana` | 3000 | Monitoring dashboard |
| `grafana-image-renderer` | `docker.io/grafana/grafana-image-renderer` | 8081 | Dashboard image rendering |
| `opensearch` | `docker.io/opensearchproject/opensearch:2.19.5` | 9200, 9600 | Search engine |
| `opensearch-dashboards` | `docker.io/opensearchproject/opensearch-dashboards:2.19.5` | 5601 | OpenSearch dashboards |
| `authnz` | `auth/demo` | 80 | Auth/proxy (disabled by default) |
| `adminer` | `docker.io/library/adminer` | 8080 | Database admin tool |
| `mqtt-broker` | `anms.Containerfile::mqtt-broker` | 1883 | MQTT broker for transcode pipeline |
| `transcoder` | `anms.Containerfile::transcoder` | — | Audio transcoder |
| `aricodec` | `anms.Containerfile::aricodec` | — | ARI codec for transcode pipeline |

**Lightweight (`docker-compose-testenv.yml`):**

| Service | Source | Port | Purpose |
|---------|--------|------|---------|
| `postgres` | `anms.Containerfile::anms-sql` | 5432 | Relational store |
| `redis` | `redis:6.0-alpine` | 6379 | Sessions + caching |
| `anms-core` | `${DOCKER_IMAGE_PREFIX}anms-core` | 5555 | Flask REST API |
| `anms-ui` | `${DOCKER_IMAGE_PREFIX}anms-ui` | 9030/9443 | Angular UI + Express |
| `amp-manager` | `anms.Containerfile::amp-manager` | 8089 | Real refdm-proxy HTTP API |
| `ion-manager` | `ghcr.io/nasa-ammos/anms/ion-manager` | — | ION DTN daemon (privileged) |

## Test Results

| Config | Tests | Time | Notes |
|--------|-------|------|-------|
| Lightweight (`docker-compose-testenv.yml`) | 41/41 pass | ~57s | All services healthy |
| Full stack (`docker-compose-full.yml`) | 39/41 pass | ~2.1m | 2 timeouts on 50-page-reload tests (expected — additional services compete for resources) |

## Troubleshooting

### Services not starting

```bash
# Check container logs
docker compose -f docker-compose-full.yml logs -f

# Check individual service health
docker exec -it integration_test-anms-ui-1 pm2 status
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

# Verify Grafana
curl -I http://localhost:3000/

# Verify OpenSearch
curl http://localhost:9200/
```

### OpenSearch won't start

Requires `OPENSEARCH_INITIAL_ADMIN_PASSWORD` to be ≥8 characters with uppercase, lowercase,
digit, and special character. Update the value in `.env`:

```bash
OPENSEARCH_INITIAL_ADMIN_PASSWORD=Str0ng!Pass#2026
```

### authnz not available

The authnz service is temporarily disabled in `docker-compose-full.yml` because it requires
TLS certificates from the `ammos-tls` volume. To enable it:

1. Create dummy certificates:
   ```bash
   docker run --rm -v ammos-tls:/mnt alpine sh -c '
     mkdir -p /mnt/etc/pki/tls/certs /mnt/etc/pki/tls/private
     openssl req -x509 -newkey rsa:2048 -keyout /mnt/etc/pki/tls/private/key.pem \
       -out /mnt/etc/pki/tls/certs/ammos-ca-bundle.crt -days 365 -nodes \
       -subj "/CN=localhost" 2>/dev/null'
   ```
2. Uncomment the authnz service in `docker-compose-full.yml`.

### Playwright can't find selectors

The test selectors are based on the Vue.js → Angular migration. Selectors may need
updating based on the current Angular implementation. Check the browser DevTools
for the actual element attributes and update selectors in test files.

## File Structure

```
anms-ui/integration_test/
├── docker-compose-full.yml       # Full stack — ALL services (stress-test.sh parity)
├── docker-compose-testenv.yml    # Lightweight — just UI + backend (fast CI)
├── .env                          # Default environment variables (copy to .env.local to override)
├── playwright.config.ts          # Chromium headless, 2 workers, trace collection
├── package.json                  # Test dependencies (manually installed)
├── tests/
│   ├── global-setup.ts           # Docker stack health check
│   ├── global-teardown.ts        # Cleanup instructions
│   ├── sanity.test.ts            # Playwright + Chromium verification (2/2 PASS)
│   ├── base.test.ts              # Auth flow, session, page load baseline
│   ├── monitor.test.ts           # Monitor tab, Grafana iframe
│   ├── agents.test.ts            # Agents tab, search, detail
│   ├── build.test.ts             # Build tab, ARI builder
│   ├── concurrent.test.ts        # Parallel user load simulation (N=1,5,10)
│   ├── api-performance.test.ts   # API latency per endpoint, concurrency
│   ├── navigation.test.ts        # Tab switching, memory leak, stale data
│   ├── session.test.ts           # Session persistence, concurrent sessions
│   └── error-recovery.test.ts    # 500 errors, timeout, offline, rate limiting
├── utils/
│   ├── api-helpers.ts            # API health checks, seeded data helpers
│   └── metrics.ts                # DOM size, load time, memory, performance
└── README.md                     # This file
```