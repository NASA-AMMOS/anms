"""Auto-generated from ANMS Test Specification section 3.6.
  Cases: 2, Steps available: 2/2
  Run: pytest -xvs tests/generated/test_exp_system_admin.py
  Requires: docker/podman compose up -d (in repo root)
"""

import pytest

# Section: 3.6 | Cases: 2 | With steps: 2

async def test_anms_fun_sys_001(http_client):
    """ANMS_FUN_SYS_001: System Status"""
    # Section: 3.6 System Administration
    # Purpose: This test compares the displayed current system status to the functions provided in the user interface.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: The services (containers) have a dependency hierarchy. Randomly stopping service
    # TODO: map to API call
    # assert ...

    # Step 2: Nominal Status
    # TODO: map to API call
    # assert ...

    # Step 3: Select the System Status option to view the currently executing services.
    resp = await client.get("http://localhost:5555/nm/api/sys_status")  # path=/nm/api/sys_status
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 4: Verify the executing services with one or more:
    # TODO: add assertion
    # assert ...

    # Step 5: command line command \"sudo podman ps”
    # TODO: map to API call
    # assert ...

    # Step 6: http://localhost:5555/docs/#/SYS_STATUS/sys_status_get_db_status_sys_status_db_status_get and select
    resp = await client.get("http://localhost:5555/docs/#/SYS_STATUS/sys_status_get_db_status_sys_status_db_status_get")  # path=http://localhost:5555/docs/#/SYS_STATUS/sys_status_get_db_status_sys_status_db_status_get
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 7: logs (/opt/ammos-anms/anms-ui/logs/debug.[date].log)
    # TODO: map to API call
    # assert ...

    # Step 8: Halt a Service
    # TODO: map to API call
    # assert ...

    # Step 9: Use terminal commands to halt the first service listed:
    # TODO: map to API call
    # assert ...

    # Step 10: podman compose -p anms stop <container_name>
    # TODO: map to API call
    # assert ...

    # Step 11: (URL already called above) where <container_name> is a name listed in the System Status option.
    # Step 12: Verify the System Status option is updated to reflect the halted service and the number of services 
    # TODO: add assertion
    # assert ...

    # Step 13: (URL already called above) Capture a screenshot of the System Status option.
    # Step 14: Verify the executing services with one or more:
    # TODO: add assertion
    # assert ...

    # Step 15: command line command \"sudo podman ps”
    # TODO: map to API call
    # assert ...

    # Step 16: (URL already called above) http://localhost:5555/docs/#/SYS_STATUS/sys_status_get_db_status_sys_status_db_s
    # Step 17: logs (/opt/ammos-anms/anms-ui/logs/debug.[date].log)
    # TODO: map to API call
    # assert ...

    # Step 18: Use terminal commands to restart the first service halted:
    # TODO: map to API call
    # assert ...

    # Step 19: podman compose -p anms stop <container_name>
    # TODO: map to API call
    # assert ...

    # Step 20: (URL already called above) where <container_name> is a name listed in the System Status option.
    # Step 21: Verify the System Status option is updated to reflect the running service.
    # TODO: add assertion
    # assert ...

    # Step 22: Verify the executing services with one or more:
    # TODO: add assertion
    # assert ...

    # Step 23: command line command \"sudo podman ps”
    # TODO: map to API call
    # assert ...

    # Step 24: (URL already called above) http://localhost:5555/docs/#/SYS_STATUS/sys_status_get_db_status_sys_status_db_s
    # Step 25: logs (/opt/ammos-anms/anms-ui/logs/debug.[date].log)
    # TODO: map to API call
    # assert ...

    # Step 26: Repeat this section for another service listed.
    # TODO: map to API call
    # assert ...

    # Step 27: Halt Multiple Services
    # TODO: map to API call
    # assert ...

    # Step 28: Use terminal commands to halt the several services listed:
    # TODO: map to API call
    # assert ...

    # Step 29: podman compose -p anms stop <container_name>
    # TODO: map to API call
    # assert ...

    # Step 30: (URL already called above) where <container_name> is a name listed in the System Status option.
    # Step 31: Verify the System Status option is updated to reflect the halted services and the number of services
    # TODO: add assertion
    # assert ...

    # Step 32: Verify the executing services with one or more:
    # TODO: add assertion
    # assert ...

    # Step 33: command line command \"sudo podman ps”
    # TODO: map to API call
    # assert ...

    # Step 34: (URL already called above) http://localhost:5555/docs/#/SYS_STATUS/sys_status_get_db_status_sys_status_db_s
    # Step 35: logs (/opt/ammos-anms/anms-ui/logs/debug.[date].log)..
    # TODO: map to API call
    # assert ...

    # Step 36: (URL already called above) Capture a screenshot of the System Status option.
    # Step 37: Use terminal commands to restart a service halted:
    # TODO: map to API call
    # assert ...

    # Step 38: podman compose -p anms start <container_name>
    # TODO: map to API call
    # assert ...

    # Step 39: where <container_name> is a name of a sevice previously stopped.
    # TODO: map to API call
    # assert ...

    # Step 40: Verify the System Status option is updated to reflect the running services.
    # TODO: add assertion
    # assert ...

    # Step 41: Verify the executing services with one or more:
    # TODO: add assertion
    # assert ...

    # Step 42: command line command \"sudo podman ps”
    # TODO: map to API call
    # assert ...

    # Step 43: (URL already called above) http://localhost:5555/docs/#/SYS_STATUS/sys_status_get_db_status_sys_status_db_s
    # Step 44: logs (/opt/ammos-anms/anms-ui/logs/debug.[date].log).
    # TODO: map to API call
    # assert ...

    # Step 45: Use terminal commands to restart the remainingservices halted:
    # TODO: map to API call
    # assert ...

    # Step 46: podman compose -p anms start <container_name>
    # TODO: map to API call
    # assert ...

    # Step 47: where <container_name> is a name of a sevice previously stopped.
    # TODO: map to API call
    # assert ...

    # Step 48: Verify the System Status option is updated to reflect the running services.
    # TODO: add assertion
    # assert ...

    # Step 49: Verify the executing services with one or more:
    # TODO: add assertion
    # assert ...

    # Step 50: command line command \"sudo podman ps”
    # TODO: map to API call
    # assert ...

    # Step 51: (URL already called above) http://localhost:5555/docs/#/SYS_STATUS/sys_status_get_db_status_sys_status_db_s
    # Step 52: logs (/opt/ammos-anms/anms-ui/logs/debug.[date].log).
    # TODO: map to API call
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "Selected services may be stopped and restarted"
    # assert ...  # "The status of a service is display correctly"


async def test_anms_exp_sys_002(http_client):
    """ANMS_EXP_SYS_002: Login"""
    # Section: 3.6 System Administration
    # Purpose: This test verifies users may login to the GUI and logs record the activities.  This test also explores the ability to bring up the system without an interface.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Valid Login and Logout
    # TODO: map to API call
    # assert ...

    # Step 2: Note the time and supply a valid user name and password to login.
    # TODO: add assertion
    # assert ...

    # Step 3: From a terminal window, use  \"podman compose -p anms logs authnz \" to check the logins.
    # TODO: add assertion
    # assert ...

    # Step 4: Verify the logs provide information about the valid login results for the login time.
    # TODO: add assertion
    # assert ...

    # Step 5: Logout of the GUI.
    # TODO: map to API call
    # assert ...

    # Step 6: Verify the logs provide information about the user IDs and times.
    # TODO: add assertion
    # assert ...

    # Step 7: Invalid Login
    # TODO: map to API call
    # assert ...

    # Step 8: Note the time and supply an invalid user name and valid password to login.
    # TODO: add assertion
    # assert ...

    # Step 9: From a terminal window, use \"socker compose -p anms logs authnz\" to check the logins.
    # TODO: add assertion
    # assert ...

    # Step 10: Verify the logs provide information about the invalid password results for the login time.
    # TODO: add assertion
    # assert ...

    # Step 11: Note the time and supply a valid user name and invalid password to login.
    # TODO: add assertion
    # assert ...

    # Step 12: Verify the  logs provide information about the invalid login results for the login time.
    # TODO: add assertion
    # assert ...

    # Step 13: Login without GUI
    # TODO: map to API call
    # assert ...

    # Step 14: Halt the system from a terminal:
    # TODO: map to API call
    # assert ...

    # Step 15: cd /ammos/deploy/anms
    # TODO: map to API call
    # assert ...

    # Step 16: podman compose -p anms down
    # TODO: map to API call
    # assert ...

    # Step 17: podman compose -p test-env down
    # TODO: map to API call
    # assert ...

    # Step 18: podman compose -f light-compose.yml up -d
    # TODO: map to API call
    # assert ...

    # Step 19: podman compose -f testenv-compose.yml up -d
    # TODO: map to API call
    # assert ...

    # Step 20: Register an agent:
    # TODO: map to API call
    # assert ...

    # Step 21: HYPERLINK "http://localhost:5555/docs/#/NM/nm_register_agent_nm_agents_post"http://localhost:5555/do
    resp = await client.request("POST", "http://localhost:5555/nm/api/agents")  # path=http://localhost:5555/nm/api/agents
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 22: with
    # TODO: map to API call
    # assert ...

    # Step 23: {
    # TODO: map to API call
    # assert ...

    # Step 24: \"data\": \"ipn:2.6\"
    # TODO: map to API call
    # assert ...

    # Step 25: }
    # TODO: map to API call
    # assert ...

    # Step 26: Add the agent:
    # TODO: map to API call
    # assert ...

    # Step 27: (URL already called above) HYPERLINK "http://localhost:5555/docs/#/NM/nm_put_hex_eid_nm_agents_eid__eid__he
    # Step 28: with ipn:2.6 and
    # TODO: map to API call
    # assert ...

    # Step 29: {
    # TODO: map to API call
    # assert ...

    # Step 30: \"data\": \" 0x82148218498564696574666B64746E6D612D6167656E742267696E73706563748
    # TODO: map to API call
    # assert ...

    # Step 31: }
    # TODO: map to API call
    # assert ...

    # Step 32: Verify the reports:
    # TODO: add assertion
    # assert ...

    # Step 33: HYPERLINK \"http://localhost:5555/docs/#/REPORTS/report_ac_report_entries_table_
    # GUI interaction
    # Step 34: with
    # TODO: map to API call
    # assert ...

    # Step 35: agent_id ipn:2.6
    # TODO: map to API call
    # assert ...

    # Step 36: correlator_nonce= 73
    # TODO: map to API call
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "Only valid users are logged in"
    # assert ...  # "System may be accessed without an interface"

