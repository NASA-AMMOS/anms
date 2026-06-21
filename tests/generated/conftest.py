"""Shared fixtures for ANMS acceptance test suite.

Automatically spins up both Docker Compose stacks (main ANMS + testenv),
waits for all services to become healthy, then runs tests against localhost.

Required environment variables (from .env):
  AUTHNZ_PORT       - authnz port (default 8084)
  ANMS_CORE_HTTP_PORT - core API port (default 5555)
  ION_MGR_PORT      - ion-manager direct port (default 9089)

Usage:
  # Run with explicit port overrides:
  ANMS_BASE_URL=http://localhost:8084 pytest tests/generated/

  # Or let the fixture pull from .env:
  pytest tests/generated/

Dependencies: pip install pytest httpx docker
"""
import os
import socket
import subprocess
import sys
import time as _time
from pathlib import Path

import httpx
import pytest

# ── Paths ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
DOCKER_COMPOSE = REPO_ROOT / "docker-compose.yml"
TESTENV_COMPOSE = REPO_ROOT / "testenv-compose.yml"
ENV_FILE = REPO_ROOT / ".env"

# Container runtime
_RUNTIME = "podman" if Path("/usr/bin/podman").exists() else "docker"

# Ports (from .env)
AUTHNZ_PORT = os.environ.get("AUTHNZ_PORT", "8084")
CORE_PORT = os.environ.get("ANMS_CORE_HTTP_PORT", "5555")
ION_MGR_PORT = os.environ.get("ION_MGR_PORT", "9089")


# ── Helpers ──────────────────────────────────────────────────────────────
def _load_env():
    """Load environment variables from .env file into os.environ."""
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip("'\"")
                if key not in os.environ:
                    os.environ[key] = val


def _compose(cmd_lines):
    """Run docker compose or podman compose with given subcommands."""
    cmd = [_RUNTIME, "compose"]
    for extra in ("--project-name", "anms-test", "--environment-file",
                  str(ENV_FILE.resolve())):
        cmd.extend((extra, ""))  # placeholder — overridden below
    # Build properly
    cmd = [_RUNTIME, "compose", "-p", "anms-test"]
    cmd.extend(("-f", str(cmd_lines[0])))
    cmd.extend(cmd_lines[1:])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return r
    except subprocess.TimeoutExpired:
        r = subprocess.CompletedProcess(cmd, 1, "", f"timeout>300s")
        r.stderr += "\n" + r.stderr if r.stderr else "" + "\nTIMEOUT"
        return r
    except Exception as e:
        return type("Err", (), {"returncode": 1, "stderr": str(e)})()


def _compose_up(env_file, desc):
    """Start a compose stack in the background."""
    print(f"\n[spawn] {desc}...")
    r = _compose(("-f", str(env_file), "up", "-d"))
    if r.returncode != 0:
        print(f"  ERROR: {r.stderr[:500]}")
        return False
    return True


def _compose_down(env_file, desc):
    """Destroy a compose stack."""
    r = _compose(("-f", str(env_file), "down", "--remove-orphans"))
    if r.returncode == 0:
        print(f"  [teardown] {desc} down")


def _wait_tcp(host, port, timeout, desc):
    """Block until a TCP port is open or timeout."""
    for _ in range(timeout):
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            _time.sleep(1)
    print(f"  WARN: {desc} not reachable at {host}:{port}")
    return False


# Load .env at import time so compose sub-routines see the vars
_load_env()


# ── Session fixtures ─────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def anms_spawn():
    """Spawn both Docker stacks before the test session begins.

    1. Pre-creates the sockdir required by testenv-compose.yml
    2. Starts the main ANMS stack (docker-compose.yml)
    3. Waits for authnz and core API to respond
    4. Starts the testenv stack (ion-manager, ion-agents)
    5. Waits for ion-manager port

    Teardown occurs automatically via pytest_sessionfinish.
    """
    # Pre-create volume mount directory for testenv
    sockdir = REPO_ROOT / os.environ.get("HOST_SOCKDIR", "sockdir")
    sockdir.mkdir(parents=True, exist_ok=True)

    # Clean up any leftovers
    subprocess.run(
        [_RUNTIME, "compose", "-p", "anms-test", "down", "--remove-orphans"],
        capture_output=True, text=True, timeout=30,
    )

    # Start main ANMS stack
    if not _compose_up(DOCKER_COMPOSE, "ANMS main stack"):
        pytest.fail("Could not start main ANMS stack. Is docker/podman running?")

    _time.sleep(15)  # initial wait for DB init + service startup

    # Wait for authnz
    if not _wait_tcp("localhost", int(AUTHNZ_PORT), 120, "authnz"):
        pytest.fail("authnz not ready after 120s")

    # Wait for core API
    if not _wait_tcp("localhost", int(CORE_PORT), 60, "core api"):
        pytest.fail("core /nm/api not ready after 60s")

    # Start testenv stack (ion-manager, ion-agents)
    if DOCKER_COMPOSE.exists():
        # testenv depends on sockdir which we've created
        _compose_up(TESTENV_COMPOSE, "testenv (ion-manager)")
        _time.sleep(15)
        _wait_tcp("localhost", int(ION_MGR_PORT), 90, "ion-manager")

    print(f"\n[ready] ANMS at localhost:{AUTHNZ_PORT}, "
          f"core at localhost:{CORE_PORT}, ion-manager at localhost:{ION_MGR_PORT}")
    yield


@pytest.fixture(scope="session")
def anms_base(anms_spawn):
    """Base URL of the ANMS authnz layer."""
    return f"http://localhost:{os.environ.get('AUTHNZ_PORT', '8084')}"


@pytest.fixture(scope="session")
def anms_core(anms_spawn):
    """Base URL of the ANMS core API layer."""
    return f"http://localhost:{os.environ.get('ANMS_CORE_HTTP_PORT', '5555')}"


@pytest.fixture(scope="session")
def ion_mgr(anms_spawn):
    """Base URL of the ion-manager direct REST API."""
    return f"http://localhost:{os.environ.get('ION_MGR_PORT', '9089')}"


@pytest.fixture(scope="session")
def http_client(anms_base):
    """Async httpx client pre-configured for ANMS localhost.

    Usage:
        async def test_example(http_client):
            async with http_client() as client:
                resp = await client.get("/nm/api/agents")
                assert resp.status_code == 200
    """
    async def make():
        return httpx.AsyncClient(
            base_url=anms_base,
            timeout=httpx.Timeout(30.0, connect=5.0),
            follow_redirects=True,
        )
    return make


@pytest.fixture(scope="session")
def http_client_core(anms_core):
    """Async httpx client for the core API layer."""
    async def make():
        return httpx.AsyncClient(
            base_url=anms_core,
            timeout=httpx.Timeout(30.0, connect=5.0),
            follow_redirects=True,
        )
    return make


@pytest.fixture(scope="session")
def http_client_ion(ion_mgr):
    """Async httpx client for the ion-manager / AMP manager direct API."""
    async def make():
        return httpx.AsyncClient(
            base_url=ion_mgr,
            timeout=httpx.Timeout(30.0, connect=5.0),
            follow_redirects=True,
        )
    return make


# ── Session teardown ─────────────────────────────────────────────────────
def pytest_sessionfinish(session, exitstatus):
    """Teardown Docker stacks after all tests complete."""
    print("\n[teardown] Shutting down ANMS test environment...")
    _compose_down(TESTENV_COMPOSE, "testenv")
    _compose_down(DOCKER_COMPOSE, "ANMS main")
    print("[teardown] Done")
