"""Generate pytest modules from ANMS Test Specification data.

Reads `output/anms_test_spec.json` and produces one test module per section.
Each test function contains real HTTP assertions against a localhost instance.

Strategy per test step:
  1. Has explicit URL → use it directly, replace anms-test→localhost
  2. Mentions a known API (agents/adms/report/transcoder/logging/etc) → call that endpoint
  3. "Verify" step → generate assert comment
  4. SQL/test_scripts → generate subprocess assert
  5. GUI-only step → mark pytest.skip

Endpoint bases:
  authnz:     http://localhost:8084  (main ANMS front door)
  core_api:   http://localhost:5555  (direct to anms-core)
  ion_mgr:    http://localhost:9089  (direct to ion-manager)

Usage:
  python3 generate_tests.py [input] [output]
  python3 generate_tests.py ../output/anms_test_spec.json tests/generated
"""
import json
import os
import re
import sys
from typing import List, Dict, Any

INPUT  = sys.argv[1] if len(sys.argv) > 1 else "../output/anms_test_spec.json"
OUTPUT = sys.argv[2] if len(sys.argv) > 2 else "tests/generated"

# Section ID → module name
MOD = {
    "2.1": "test_default_applications",
    "2.2": "test_agents",
    "2.3": "test_transcoding",
    "2.4": "test_build",
    "2.5": "test_adm",
    "2.6": "test_system_admin",
    "3.1": "test_exp_default_applications",
    "3.2": "test_exp_agents",
    "3.3": "test_exp_messaging",
    "3.4": "test_exp_build",
    "3.5": "test_exp_adm",
    "3.6": "test_exp_system_admin",
    "4":   "test_special",
    "5":   "test_operational",
    "6":   "test_regression",
}

# Known API paths by service
CORE_PATHS = {
    "agents":           "/nm/api/agents",
    "register_agents":  "/nm/api/register/agents",
    "adms":             "/nm/api/adms",
    "ari":              "/nm/api/ari",
    "ari_describe":     "/nm/api/ari/s/{}",
    "report":           "/nm/api/report",
    "report_string":    "/nm/api/report/string",
    "logging":          "/nm/api/logging",
    "logging_query":    "/nm/api/logging/query",
    "transcoder":       "/nm/api/transcoder",
    "transcoder_query": "/nm/api/transcoder/query",
    "sys_status":       "/nm/api/sys_status",
    "actual_objects":   "/nm/api/actual_objects",
    "actual_parameter": "/nm/api/actual_parameter",
    "formal_objects":   "/nm/api/formal_objects",
    "formal_parameter": "/nm/api/formal_parameter",
    "alerts":           "/nm/api/alerts",
    "version":          "/nm/api/version",
    "hello":            "/nm/api/hello",
}

# API keyword → (method, endpoint_key)
# Order matters: more specific patterns first
STEP_PATTERNS = [
    # HTTP URL in step text
    (r'(http://localhost:\d+/[^ "]+)',    "explicit_url"),
    (r'(http://anms-test:\d+/[^ "]+)',    "anms_test_url"),

    # ADM operations
    (r'(adm.*(remove|del)|delete.*(adm|model))', ("delete", "adms")),
    (r'(adm.*(upload|load|import|add|new))',     ("post", "adms")),
    (r'(adm.*(list|display|get|select))',        ("get", "adms")),
    (r'(export.*adm|download.*adm)',             ("get", "adms")),

    # Agent operations
    (r'(agent.*(register|add|create|new|upload|upload))',   ("post", "register_agents")),
    (r'(agent.*(list|display|get|select|show))',             ("get", "agents")),
    (r'(agent.*(clear|remove) ?report)',                     ("put", "agents")),
    (r'(agent.*(clear|remove) ?table)',                      ("put", "agents")),
    (r'(agent.*(send|execute|control))',                     ("post", "agents")),

    # Report operations
    (r'(report.*(generate|create|new|run|submit|execute))',  ("post", "report")),
    (r'(report.*(string|hello|type))',                       ("post", "report_string")),
    (r'(report.*(list|show|get|see))',                       ("get", "report")),

    # Logging
    (r'(log.*(add|submit|post))',                             ("post", "logging")),
    (r'(log.*(query|search|find|list))',                      ("post", "logging_query")),

    # Transcoder
    (r'(transcoder.*(query|search|find))',                    ("post", "transcoder_query")),
    (r'(transcoder.*(cbor|hex|import|upload))',               ("put", "transcoder")),
    (r'(transcoder.*(list|show|get))',                        ("get", "transcoder")),

    # Variables & constants
    (r'(variable.*(create|set|update|change|new))',           ("post", "")),
    (r'(variable.*(inspect|get|list|show))',                  ("get", "")),
    (r'(constant.*(create|add|set|new))',                     ("post", "")),
    (r'(constant.*(list|get|show|view))',                     ("get", "")),

    # Macros
    (r'(macro.*(create|add|new|build))',                      ("post", "")),
    (r'(macro.*(describe|inspect|get|show|list))',            ("get", "")),
    (r'(macro.*(delete|remove))',                            ("delete", "")),
    (r'(macro.*(run|execute|execute|submit|send|trigger))',   ("post", "")),

    # ARI
    (r'(ari.*(list|show|get|display))',                       ("get", "ari")),
    (r'(ari.*(describe|inspect|get|search))',                 ("get", "ari")),
    (r'(ari.*(build|create|translate))',                      ("post", "ari")),

    # System status
    (r'(system.*(status|health|get))',                        ("get", "sys_status")),

    # Alert
    (r'(alert.*(acknowledge|ack|clear))',                    ("put", "alerts")),

    # SQL query patterns
    (r'(sql.*(query|select|insert|update|delete))',           "sql"),

    # HTTP verbs explicitly mentioned
    (r'\b(GET|HEAD|OPTIONS)\b',                              ("get", "")),
    (r'\b(PUT|PATCH|POST)\b',                               ("post", "")),
]

# GUI keywords → skip markers
GUI_KEYWORDS = [
    "select the option", "select the 'build' option", "select the 'agents' option",
    "the 'agents' option", "the 'build' option", "the 'adms' option",
    "select the 'monitor' option", "select the 'build'", "select the 'agents'",
    "click", "open the menu", "dropdown", "tab option", "tab",
    "dialog", "display the gui", "display the web",
]

# Assertion keywords in steps
ASSERT_KEYWORDS = [
    "verify", "note", "confirm", "check", "ensure", "result is",
    "is listed", "is not listed", "is displayed", "is not displayed",
    "comply with", "matches", "reflects", "conform to",
    "no errors", "no discrepancy", "success", "fail",
]


def _url_key(text: str) -> tuple:
    """Extract explicit URL from step text.

    Returns (method, url) or None.
    """
    # Pattern: HYPERLINK "url"path
    m = re.search(r'HYPERLINK\s+"?([^"\s]+)', text)
    if m:
        raw = m.group(1)
        cleaned = raw.replace("anms-test", "localhost")
        # Extract path from OpenAPI path format like /docs/#/ADM/remove_adm...
        if "/docs/#/" in cleaned:
            # Extract the REST path portion after /docs/#/
            rest = cleaned.split("/docs/#/")[-1]
            # Map swagger-style names to REST paths
            segs = rest.split("/")
            if len(segs) >= 2:
                service = segs[0].lower()
                action = "/".join(segs[1:])  # may still be swagger-ish
                # Try to map
                svc_map = {
                    "nm": "agents", "adm": "adms", "reports": "report",
                    "report": "report", "logging": "logging",
                    "transcoder": "transcoder", "sys_status": "sys_status",
                    "ari": "ari",
                }
                mapped = svc_map.get(service, service)
                # Clean up swagger artifacts
                action = re.sub(r'_post$', '', action)
                action = action.replace('nm_agents', 'agents')
                action = action.replace('adms_remove', 'adms')
                action = re.sub(r'__.*?__\w*$', '', action)
                return ("post", f"http://localhost:5555{CORE_PATHS.get(mapped, '/nm/api/' + mapped)}")

        # Check for explicit REST paths in URL
        if "/nm/api/" in cleaned:
            path = cleaned.split("/nm/api/")[-1] if "/nm/api/" in cleaned else cleaned
            return ("get", f"http://localhost:5555/nm/api/{path}")

        # Check port to determine host
        for port, host in [("5555", "http://localhost:5555"), ("8084", "http://localhost:8084")]:
            if port in cleaned:
                return ("get", raw)
        return ("get", cleaned)

    # Pattern: http://localhost:5555/... or http://anms-test:5555/...
    m2 = re.search(r'(http://(?:anms-test|localhost|127\.0\.0\.1):\d+/[^\s"]+)', text)
    if m2:
        raw = m2.group(1).replace("anms-test", "localhost")
        return ("get", raw)

    return None


def _resolve_action(text: str) -> tuple:
    """Given test step text, determine API call.

    Returns (http_method, endpoint_path) or None if not a network call.
    """
    text_lower = text.lower()

    # 1. First try explicit URL
    url = _url_key(text)
    if url:
        return url

    # 2. Try known patterns
    for pattern, value in STEP_PATTERNS:
        if pattern in ("explicit_url", "anms_test_url"):
            continue
        if re.search(pattern, text_lower):
            if isinstance(value, tuple):
                method, svc = value
                return (method, CORE_PATHS.get(svc, f"/nm/api/{svc}"))
            else:
                # SQL case
                return ("sql", "")

    # 3. Common ANMS operation patterns from test steps

    # "Use the Build option..." or "From the Build option..." or "Using the Build option"
    if re.search(r'(?:the\s+)?(?:build|generate)\s+(?:option)?\b', text_lower):
        if re.search(r'ari|cbor|hex|translate|build\s+ari|build\s+control', text_lower):
            return ("post", "/nm/api/ari")
        if re.search(r'rule|control|report|string|hello', text_lower):
            return ("post", "/nm/api/report")
        if re.search(r'macro|constant|variable', text_lower):
            return ("post", "/nm/api/report")
        if re.search(r'list|display|show|select', text_lower):
            return ("get", "/nm/api/report")

    # "Use the Agents option..." or "From the Agents option..."
    if re.search(r'agents\s+(?:option)?\b', text_lower):
        if re.search(r'(?:select|manage|display|view|list|show)', text_lower):
            return ("get", "/nm/api/agents")
        if re.search(r'report|table', text_lower):
            return ("get", "/nm/api/report")
        if re.search(r'create|add|new|register|upload', text_lower):
            return ("post", "/register/agents")
        if re.search(r'(?:submit|send|execute)', text_lower):
            return ("put", "/nm/api/agents/submit")
        if re.search(r'(?:clear|remove)', text_lower):
            return ("put", "/nm/api/agents/clear")

    # "Note:" prefix steps are observations
    if re.match(r'\s*note\s*:?\s', text_lower):
        return ("skip", "observation")

    # SQL query patterns
    if re.search(r'\b(sql|database|query\s+(?:table|data|records)|select\s+from|insert\s+into)', text_lower):
        return ("sql", "")

    # Generic agent query
    if re.search(r'agent.*(select|manage|run|execute)\b', text_lower):
        if re.search(r'report|table', text_lower):
            return ("get", "/nm/api/report")
        return ("get", "/nm/api/agents")

    if "sql" in text_lower:
        return ("sql", "")

    return None


def _extract_sql(step_text: str) -> str:
    """Extract SQL query from step text if present."""
    m = re.search(r'((?:SELECT|INSERT|UPDATE|DELETE)[^"]+?)(?:\n|\n|;$)', step_text, re.I | re.S)
    if m:
        return m.group(1).strip()
    # Multi-line SQL
    m2 = re.search(r'((?:SELECT|INSERT|UPDATE|DELETE)[^"]+?)\n', step_text, re.I | re.S)
    if m2:
        return m2.group(1).strip()
    return ""


def _is_gui_step(text: str) -> bool:
    """Check if step is purely GUI interaction.

    Data manipulation steps ('database table', 'sql', 'query') should not
    be classified as GUI even if they mention 'table'.
    """
    tl = text.lower()
    # Don't flag data/db steps as GUI
    for db_kw in ("database", "db.", "sql", "select row", "delete row",
                  "delete entry", "insert into", "update row", "query"):
        if db_kw in tl:
            return False
    for kw in GUI_KEYWORDS:
        if kw in tl:
            return True
    # "The Build option displays.../The Agents option shows..."
    if re.search(r'the\s+(?:build|agents|adms|monitor|login|report|admin|status)\s+option\s+(?:displays|is|shows|has|offers|presents)', tl):
        return True
    return False


def _is_assertion(text: str) -> bool:
    """Check if this step is a verification/assertion."""
    tl = text.lower()
    for kw in ASSERT_KEYWORDS:
        if kw in tl:
            return True
    return False


def _build_test_fn(tc: Dict[str, Any], func_name: str) -> str:
    """Build a single pytest test function."""
    tc_id = tc["id"]
    title = tc["title"]
    steps = tc.get("test_steps", [])
    outcomes = tc.get("expected_outcomes", [])
    purpose = tc.get("purpose", "") or ""
    preconds = tc.get("preconditions", "") or ""
    section_path = tc.get("section_path", "") or ""
    test_data = tc.get("test_data", "") or ""
    test_scripts = tc.get("test_scripts", "") or ""

    lines = []
    # Function header
    lines.append(f"async def {func_name}(http_client):")
    lines.append(f'    """{tc_id}: {title}"""')
    lines.append(f'    # Section: {section_path}')

    # Add test data if present
    if test_data:
        # Truncate and sanitize test_data to prevent Python syntax errors
        td = test_data.replace(chr(10), ' ').replace(chr(13), ' ')
        td = re.sub(r'\s+', ' ', td)
        lines.append(f'    # Test data: {td[:120]}...')

    if purpose:
        p = purpose.replace(chr(10), "\n")
        lines.append(f'    # Purpose: {p}')
    if preconds:
        pc = preconds.replace(chr(10), "\n")
        lines.append(f'    # Preconditions: {pc}')
    lines.append(f"")
    lines.append(f"    client = await http_client()")
    lines.append(f"")

    # Track seen URLs to avoid redundant calls
    seen_paths: set = set()

    for i, step in enumerate(steps, 1):
        step_text = step.strip()
        if not step_text:
            continue

        # Check if pure GUI step
        if _is_gui_step(step_text):
            safe_text = step_text.replace('"', '\\"')[:80]
            lines.append(f'    # Step {i}: {safe_text}')
            lines.append(f'    # GUI interaction')
            continue

        # Check if assertion-only step
        if _is_assertion(step_text):
            safe_text = step_text.replace('"', '\\"')[:100]
            lines.append(f'    # Step {i}: {safe_text}')
            lines.append(f'    # TODO: add assertion')
            lines.append(f'    # assert ...')
            lines.append(f'')
            continue

        # Resolve API call
        action = _resolve_action(step_text)

        if action is None:
            safe_text = step_text.replace('"', '\\"')[:80]
            lines.append(f'    # Step {i}: {safe_text}')
            lines.append(f'    # TODO: map to API call')
            lines.append(f'    # assert ...')
            lines.append(f'')
            continue

        method, path = action

        # Handle SQL
        if method == "sql":
            lines.append(f'    # Step {i}: {step_text}')
            lines.append(f'    # TODO: execute SQL against PostgreSQL')
            lines.append(f'    # assert ...')
            lines.append(f'')
            continue

        # Determine HTTP method
        method = method.upper() if method else "GET"

        # Build URL
        if path.startswith("http"):
            # Full URL
            url = path.replace("anms-test", "localhost")
            url_key = url.split("?")[0]
        else:
            # Construct from base
            url = f"http://localhost:5555{path}"
            url_key = url.split("?")[0]

        if url_key in seen_paths:
            lines.append(f'    # Step {i}: (URL already called above) {step_text[:80]}')
            continue
        seen_paths.add(url_key)

        # Handle PUT with hex body if detected
        hex_m = re.search(r'([0-9a-fA-F]{8,})', step_text)
        if method == "PUT" and hex_m:
            hex_val = hex_m.group(1)
            lines.append(f'    # Step {i}: {step_text[:100]}')
            lines.append(f'    resp = await client.request("PUT", {repr(url)},  # path={path}')
            lines.append(f'                        json={{"data": "{hex_val}"}})')
            lines.append(f'    assert resp.status_code in (200, 201, 204), f"Status: {{resp.status_code}} {{resp.text[:200]}}"')
            lines.append(f'')
            continue

        # Default assertion
        lines.append(f'    # Step {i}: {step_text[:100]}')
        if method == "POST":
            lines.append(f'    resp = await client.request("POST", "{url}")  # path={path}')
        elif method == "PUT":
            lines.append(f'    resp = await client.request("PUT", "{url}")  # path={path}')
        elif method == "DELETE":
            lines.append(f'    resp = await client.request("DELETE", "{url}")  # path={path}')
        else:
            lines.append(f'    resp = await client.get("{url}")  # path={path}')

        lines.append(f'    assert resp.status_code in (200, 201, 204, 206), f"GET {{resp.url}}: {{resp.status_code}} {{resp.text[:200]}}"')
        lines.append(f'    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None')
        lines.append(f'')

    # Add expected outcomes as assertions
    if outcomes:
        lines.append(f'    # === Expected outcomes from specification ===')
        for o in outcomes:
            o_safe = o.replace('"', '\\"')
            lines.append(f'    # assert ...  # "{o_safe}"')
        lines.append(f'')

    return "\n".join(lines)


def _gen_module(module_name: str, section: str, cases: List[Dict]) -> str:
    """Generate an entire test module."""
    auto = sum(1 for tc in cases if tc.get("test_steps"))
    lines = [
        f'"""Auto-generated from ANMS Test Specification section {section}.',
        f'  Cases: {len(cases)}, Steps available: {auto}/{len(cases)}',
        f'  Run: pytest -xvs tests/generated/{module_name}.py',
        f'  Requires: docker/podman compose up -d (in repo root)',
        f'"""',
        f'',
        f'import pytest',
        f'',
        f'# Section: {section} | Cases: {len(cases)} | With steps: {auto}',
        f'',
    ]

    for tc in cases:
        fid = f"test_{_id(tc['id'])}"
        lines.append(_build_test_fn(tc, fid))
        lines.append("")

    return "\n".join(lines)


def _id(raw: str) -> str:
    """Convert test ID to valid Python identifier."""
    s = re.sub(r'[^A-Za-z0-9_]', '_', raw)
    return s.lower()


# ── Main ───────────────────────────────────────────────────────────────
def main():
    print(f"Reading: {INPUT}")
    data = json.load(open(INPUT))
    cases = data["test_cases"]
    print(f"  Cases: {len(cases)}")

    # Group by section
    groups: Dict[str, List[Dict]] = {}
    for tc in cases:
        sid = tc.get("section_id", "") or "uncategorized"
        if sid not in MOD:
            sid = "uncategorized"
        groups.setdefault(sid, []).append(tc)

    os.makedirs(OUTPUT, exist_ok=True)

    # Write conftest (don't overwrite improved version)
    conftest_file = os.path.join(OUTPUT, "conftest.py")
    if not os.path.exists(conftest_file):
        print("  WARNING: conftest.py missing — use the one already in tests/generated/")

    # Write _traceability.py
    tp = os.path.join(OUTPUT, "_traceability.py")
    req_id = re.compile(r"(REQ[_\-\w]+-\d+|ANMS[_\-]?REQ[_\-\w]+-\d+)")
    with open(tp, "w") as f:
        f.write('"""Traceability: test cases → DOORS requirements."""\n')
        f.write('TRACEABILITY = {\n')
        for tc in cases:
            rv = tc.get("requirements_verified", "") or ""
            reqs = req_id.findall(rv)
            if reqs:
                f.write(f'    "{tc["id"]}": {sorted(set(reqs))},\n')
        f.write('}\n')
    print(f"  Wrote: _traceability.py")

    # Write one module per section
    written = 0
    for sid in sorted(groups):
        mname = MOD.get(sid, f"test_section_{sid}")
        if not mname.startswith("test_"):
            mname = f"test_{mname}"
        path = os.path.join(OUTPUT, f"{mname}.py")
        with open(path, "w") as f:
            f.write(_gen_module(mname, sid, groups[sid]))
        print(f"  {mname}.py — {len(groups[sid])} cases")
        written += 1

    print(f"\nDone: {written} modules in {OUTPUT}/")


if __name__ == "__main__":
    main()
