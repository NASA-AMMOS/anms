# ANMS Testing Runbook

## Overview

This document describes how to run and maintain all testing infrastructure for the ANMS project.

**Key principle: containers are automatically cleaned up after every test run. You should never need to manually run `docker compose down`.**

---

## Container Runtime

ANMS supports both **Docker** and **Podman**. The scripts auto-detect which is available and apply the correct configuration.

### Docker (default)
```bash
# Everything just works — no overrides needed
./stress-test.sh
cd ~/anms/anms-ui/integration_test && npx playwright test
```

### Podman
```bash
# All scripts auto-apply podman-specific overrides
./stress-test.sh          # auto-adds docker-compose-podman-override.yml
./stress-test-detailed.sh # auto-adds docker-compose-podman-override.yml
./stress-test-harder.sh   # auto-adds docker-compose-podman-override.yml

# Playwright integration tests
cd ~/anms/anms-ui/integration_test && npx playwright test  # uses podman if docker not found

# Or use the helper script which handles everything:
cd ~/anms/anms-ui/integration_test && ./start-integration-tests.sh
```

### Force a specific runtime
```bash
DOCKER_CMD=podman ./stress-test.sh
DOCKER_CMD=docker ./stress-test.sh
```

---

## Stress Tests

Located in `~/anms/`. Three levels of intensity.

### `./stress-test.sh` — Basic smoke test

Three-phase load test:
1. Landing page — 3000 requests at 100 concurrency
2. Core API — 2000 requests at 100 concurrency  
3. Grafana — 2000 requests at 100 concurrency

**Output:** JSON metrics in temp file, printed summary table, per-container CPU/memory peak stats.

```bash
./stress-test.sh

# Override defaults:
AUTHNZ_PORT=8084 HTTP_CONCURRENCY=200 LANDING_REQS=5000 ./stress-test.sh
```

### `./stress-test-detailed.sh` — Fine-grained analysis

Eight phases (A-H) with per-endpoint latency, proxy overhead, DB pool saturation, Redis sessions, Apache thread analysis, and Grafana rendering path.

**Outputs:** Per-phase JSON files in a temp directory, detailed metrics files.

```bash
./stress-test-detailed.sh                    # via authnz (default)
DIRECT=1 ./stress-test-detailed.sh          # bypass authnz, hit API directly on :5555
```

### `./stress-test-harder.sh` — Full stress suite

Five phases with 81+ endpoints:
1. Authenticated session throughput (landing, core/hello, grafana)
2. Core API read paths (ARI, objects, agents, reports — 10 endpoints)
3. Write operations (logging, ADM, users, transcoder, alerts)
4. Grafana API (health, org, search, UI)
5. Sustained load (60s mixed traffic)

```bash
./stress-test-harder.sh

# Override phase parameters:
PHASE1_REQS=5000 PHASE5_DURATION=120 ./stress-test-harder.sh
```

### `./run-stress.sh` — Resource-limited wrapper

Runs any stress script inside a systemd cgroup with CPU, memory, and I/O limits:

```bash
./run-stress.sh ./stress-test-harder.sh
./run-stress.sh ./stress-test.sh
HTTP_CONCURRENCY=200 ./run-stress.sh ./stress-test-harder.sh
```

**CGroup limits:**
- CPU: 200% (2 cores) — leaves at least one core for the agent
- Memory: 4 GB
- I/O: weight 50 (out of 100)

---

## Playwright Integration Tests

Located in `~/anms/anms-ui/integration_test/`.

### Quick start (recommended)

```bash
# Full stack with auto-detection of docker/podman
./start-integration-tests.sh

# Lightweight testenv (faster, fewer services)
./start-integration-tests.sh testenv
```

### Manual workflow

```bash
# 1. Start the stack (docker or podman)
cd ~/anms/anms-ui/integration_test
docker compose -f docker-compose-full.yml up -d
# or with podman:
podman compose -f docker-compose-full.yml -f docker-compose-full-podman-override.yml up -d

# 2. Run tests
npx playwright test

# 3. Containers are cleaned up automatically by globalTeardown()
# No need to run `docker compose down` manually
```

### Test modes

Two compose files, two environments:

| File | Services | Base URL | Auth | Use case |
|------|----------|----------|------|----------|
| `docker-compose-full.yml` | 14 services (authnz, OpenSearch, Grafana, adminer, etc.) | `http://localhost:8084` | Form-based login through authnz | Production-parity testing |
| `docker-compose-testenv.yml` | 6 services (postgres, redis, anms-core, ion-manager, amp-manager, anms-ui) | `http://localhost:9031` | None (bypassed) | Fast iteration, CI |

### Test files

| File | Description |
|------|-------------|
| `sanity.test.ts` | Quick health check (1 test) |
| `agents.test.ts` | Agent CRUD operations |
| `authnz.test.ts` | Authentication flow |
| `base.test.ts` | Base navigation and layout |
| `build.test.ts` | Build artifact verification |
| `concurrent.test.ts` | Simultaneous user sessions |
| `error-recovery.test.ts` | Error handling and recovery |
| `grafana-live-reconnect.test.ts` | Grafana live stream reconnection |
| `grafana-proxy.test.ts` | Grafana proxy routing |
| `monitor.test.ts` | Monitoring dashboard |
| `navigation.test.ts` | Page navigation and links |
| `opensearch.test.ts` | OpenSearch indexing and query |
| `session.test.ts` | User session persistence |
| `spec-driven.test.ts` | 26 tests derived from the 9-section test spec DOCX |
| `visual-regression.test.ts` | Visual comparison screenshots |
| `api-performance.test.ts` | API latency benchmarks |

### Seed data pipeline

Before running spec-driven tests, seed the database:
```bash
cd ~/anms/anms-ui/integration_test
python3 tests/seed/seed_full.py
```

---

## anms-core Integration Tests

Located in `~/anms/anms-core/integration_test/`.

Uses [Postman](https://www.postman.com/) collections + [Newman](https://www.npmjs.com/package/newman) for REST API testing.

```bash
cd ~/anms/anms-core/integration_test
yarn install          # install newman
./run_test.sh         # run against running API
```

Tests are defined in `integration_tests.json` (exported from Postman). The test runner container is built from the `anms.Containerfile` using the `anms-core-integration` target.

---

## Troubleshooting

### Containers won't start

```bash
# Check which compose implementation is being used
podman compose version
docker compose version

# Check for network conflicts
podman network ls
docker network ls

# Manual cleanup (only if automatic cleanup fails)
podman compose down --remove-orphans
# or
docker compose down --remove-orphans
```

### "driver_opts unknown" error with podman

This means the podman override isn't being applied. The override files (`*-podman-override.yml`) remove Docker-specific `driver_opts`. If you're running compose manually, include the override:

```bash
podman compose -f docker-compose.yml -f docker-compose-podman-override.yml up -d
```

### Port conflicts

The testenv stack uses port 9031 (not 9030) to avoid conflicting with the main ANMS stack. If you see port conflicts:

```bash
# Find what's using the port
lsof -i :9031
lsof -i :8084
lsof -i :5555

# Or kill the conflicting process
fuser -k 9031/tcp
```

### Test failures

1. Check container logs: `podman logs <container-name>` or `docker logs <container-name>`
2. Check if services are healthy: `podman compose ps` or `docker compose ps`
3. Run tests individually: `npx playwright test tests/sanity.test.ts`
4. Run with visible browser: `npx playwright test --headed`
5. Check the HTML report: `npx playwright show-report`

---

## Cleanup (if needed)

Scripts handle cleanup automatically via EXIT traps (stress tests) and globalTeardown (Playwright). Only needed when a script crashes mid-run:

```bash
# All ANMS containers
docker compose -f docker-compose.yml -f testenv-compose.yml down --remove-orphans
podman compose -f docker-compose.yml -f testenv-compose.yml down --remove-orphans

# Integration test containers only
cd ~/anms/anms-ui/integration_test
docker compose -f docker-compose-full.yml down --remove-orphans
podman compose -f docker-compose-full.yml -f docker-compose-full-podman-override.yml down --remove-orphans

# Clean unused images/volumes
podman image prune -f
podman volume prune -f
docker system prune -f
```
