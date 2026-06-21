"""Auto-generated from ANMS Test Specification section 3.2.
  Cases: 6, Steps available: 6/6
  Run: pytest -xvs tests/generated/test_exp_agents.py
  Requires: docker/podman compose up -d (in repo root)
"""

import pytest

# Section: 3.2 | Cases: 6 | With steps: 6

async def test_anms_fun_agt_001(http_client):
    """ANMS_FUN_AGT_001: Agent Information"""
    # Section: 3.2 Agents
    # Purpose: This test verifies information for all known agents may be displayed.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: View agent information
    # TODO: map to API call
    # assert ...

    # Step 2: Select the Agents option.
    resp = await client.get("http://localhost:5555/nm/api/agents")  # path=/nm/api/agents
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 3: (URL already called above) Select an agent from the display to view details about that agent.
    # Step 4: Verify the agent details to the database registered_agents table including the agent ID, first and l
    # TODO: add assertion
    # assert ...

    # Step 5: Note the types of reports sent listed in the Agent Details display.
    # TODO: add assertion
    # assert ...

    # Step 6: (URL already called above) Use the Agent  Build option to generate a report not currently listed for the ag
    # Step 7: Submit the control for the new report for the selected agent.
    # TODO: map to API call
    # assert ...

    # Step 8: Verify the new report is in the Agent Details display for that agent.
    # TODO: add assertion
    # assert ...

    # Step 9: Add agent information
    # TODO: map to API call
    # assert ...

    # Step 10: (URL already called above) Select the Agents option.
    # Step 11: Add agents ipn:09.01 - ipn:09.22 to the database table for registered agents.  Accept the auto-gener
    resp = await client.request("POST", "http://localhost:5555/nm/api/register/agents")  # path=/nm/api/register/agents
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 12: (URL already called above) Select the Agents option.
    # Step 13: Verify the displayed agent information includes the new agents added to the database.
    # TODO: add assertion
    # assert ...

    # Step 14: Verify the displayed agent information against the database.
    # TODO: add assertion
    # assert ...

    # Step 15: (URL already called above) Delete agent  ipn:09.22 in the database table for registered agents.
    # Step 16: Verify the deleted agent information is not listed in the Agents display.
    # TODO: add assertion
    # assert ...

    # Step 17: Remove agents
    # TODO: map to API call
    # assert ...

    # Step 18: Run the following to determine the known agents: http://anms-test:8089/nm/api/agents
    resp = await client.get("http://localhost:8089/nm/api/agents")  # path=http://localhost:8089/nm/api/agents
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 19: From a command line, stop the manager service with:
    # TODO: map to API call
    # assert ...

    # Step 20: sudo podman container stop manager service or
    # TODO: map to API call
    # assert ...

    # Step 21: podman compose -p anms stopmanager service
    # TODO: map to API call
    # assert ...

    # Step 22: Verify an alert(s) is generated for the removed agents.
    # TODO: add assertion
    # assert ...

    # Step 23: Clear the alerts.
    # TODO: map to API call
    # assert ...

    # Step 24: (URL already called above) Use the Agents option to specify a removed agent and request reports to be displ
    # Step 25: Verify reports are displayed.
    # TODO: add assertion
    # assert ...

    # Step 26: From a command line, restart themanager service with:
    # TODO: map to API call
    # assert ...

    # Step 27: sudo podman container start manager service
    # TODO: map to API call
    # assert ...

    # Step 28: podman compose -p anms start manager service
    # TODO: map to API call
    # assert ...

    # Step 29: NOTE: it may be necessary to use the Agent add address option.
    # TODO: add assertion
    # assert ...

    # Step 30: Verify an alert(s) is generated for the added agents.
    # TODO: add assertion
    # assert ...

    # Step 31: (URL already called above) Using the Manage Agents option and select an agent to manage.
    # Step 32: (URL already called above) Using the Manage Agent option, display reports for the selected agent.
    # Step 33: Verify reports are displayed.
    # TODO: add assertion
    # assert ...

    # Step 34: (URL already called above) Currently known agents should need to be added.  Run the following to determine 
    # Step 35: (URL already called above) Using the Agents option, add each of the known agents through the add option.
    # Step 36: (URL already called above) Select the Manage Agent option to display reports for all known agents.
    # Step 37: Verify no errors are generated and the agent ids are displayed.
    # TODO: add assertion
    # assert ...

    # Step 38: Verify alerts were generated for the added agents.
    # TODO: add assertion
    # assert ...

    # Step 39: Agent table navigation
    # GUI interaction
    # Step 40: Modify the number of agents per page.
    # TODO: map to API call
    # assert ...

    # Step 41: Verify the specified number of agents are displayed per page.
    # TODO: add assertion
    # assert ...

    # Step 42: Exercise the option to select the next page.
    # TODO: map to API call
    # assert ...

    # Step 43: Verify the next page is displayed.
    # TODO: add assertion
    # assert ...

    # Step 44: Exercise the option to select the previous page.
    # TODO: map to API call
    # assert ...

    # Step 45: Verify the previous page is displayed.
    # TODO: add assertion
    # assert ...

    # Step 46: Exercise the option to select the last page.
    # TODO: map to API call
    # assert ...

    # Step 47: Verify the last page is displayed.
    # TODO: add assertion
    # assert ...

    # Step 48: Exercise the option to select the first page.
    # TODO: map to API call
    # assert ...

    # Step 49: Verify the first page is displayed.
    # TODO: add assertion
    # assert ...

    # Step 50: Select a page number from those displayed.
    # TODO: map to API call
    # assert ...

    # Step 51: Verify the selected page is displayed.
    # TODO: add assertion
    # assert ...

    # Step 52: Set the number per page to the lowest number available.
    # TODO: map to API call
    # assert ...

    # Step 53: (URL already called above) Filter on an agent ID not displayed on the current page.
    # Step 54: Verify the specified agent ID is displayed.
    # TODO: add assertion
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "Agent information may be viewed and filtered"
    # assert ...  # "A known agent may be added"


async def test_anms_fun_agt_002(http_client):
    """ANMS_FUN_AGT_002: Manage Agents"""
    # Section: 3.2 Agents
    # Test data: Time-Based Rule 1 Time-based rule to send "hello"report to the local manager every second, until 120 reports have been s...
    # Purpose: This test verifies commands, verified for correctness, may be issued to one or more specified agents.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Display Reports
    # TODO: map to API call
    # assert ...

    # Step 2: Using the Agents option, select an agent to manage.
    resp = await client.get("http://localhost:5555/nm/api/agents")  # path=/nm/api/agents
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 3: Select the option to display reports for this agent.
    # GUI interaction
    # Step 4: If reports are displayed, note the reports currently displayed.
    # TODO: add assertion
    # assert ...

    # Step 5: Specify the following for a time-based rule:
    # TODO: map to API call
    # assert ...

    # Step 6: Name: Tbr.agt002_830
    # TODO: map to API call
    # assert ...

    # Step 7: Enum: 830
    # TODO: map to API call
    # assert ...

    # Step 8: Initial enabled: true
    # TODO: map to API call
    # assert ...

    # Step 9: Start: 0
    # TODO: map to API call
    # assert ...

    # Step 10: Period: 2
    # TODO: map to API call
    # assert ...

    # Step 11: Count: 10
    # TODO: map to API call
    # assert ...

    # Step 12: Report: hello report
    resp = await client.request("POST", "http://localhost:5555/nm/api/report/string")  # path=/nm/api/report/string
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 13: Verify a message is displayed indicating the command was successfully built.
    # TODO: add assertion
    # assert ...

    # Step 14: Send the command and note the time the rule started.
    # TODO: add assertion
    # assert ...

    # Step 15: Verify a message is displayed indicating the command was successfully executed.
    # TODO: add assertion
    # assert ...

    # Step 16: For the specified agent, select the option to display reports.
    # GUI interaction
    # Step 17: Review the displayed reports, verifying:
    # TODO: add assertion
    # assert ...

    # Step 18: the specified report type was generated
    resp = await client.request("POST", "http://localhost:5555/nm/api/report")  # path=/nm/api/report
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 19: (URL already called above) the datetime stamp for each report was generated at the specified period
    # Step 20: (URL already called above) the number of reports generated match the number specified
    # Step 21: When the first rule is completed, repeat this section with the following for a t
    # TODO: map to API call
    # assert ...

    # Step 22: Name: Tbr.agt002_836
    # TODO: map to API call
    # assert ...

    # Step 23: Enum: 836
    # TODO: map to API call
    # assert ...

    # Step 24: Initial enabled: true
    # TODO: map to API call
    # assert ...

    # Step 25: Start: 0
    # TODO: map to API call
    # assert ...

    # Step 26: Period: 5
    # TODO: map to API call
    # assert ...

    # Step 27: Count: 20
    # TODO: map to API call
    # assert ...

    # Step 28: Report: inspect an EDD
    # TODO: map to API call
    # assert ...

    # Step 29: Multiple Rules
    # TODO: map to API call
    # assert ...

    # Step 30: (URL already called above) Select another agent and use the Manage Agent option to display the current repo
    # Step 31: Use the Manage Agent option to create and submit a time-based rule as given for Rule 1 in the Sectio
    resp = await client.request("POST", "http://localhost:5555/nm/api/register/agents")  # path=/nm/api/register/agents
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 32: Verify a message is displayed indicating the command was successfully built.
    # TODO: add assertion
    # assert ...

    # Step 33: Send the command and note the time the rule started.
    # TODO: add assertion
    # assert ...

    # Step 34: Verify a message is displayed indicating the command was successfully executed.
    # TODO: add assertion
    # assert ...

    # Step 35: For the specified agent, select the option to display reports.
    # GUI interaction
    # Step 36: Before the rule completes, for the same agent, submit the following time-based r
    # TODO: map to API call
    # assert ...

    # Step 37: Name: Tbr.agt002_844
    # TODO: map to API call
    # assert ...

    # Step 38: Enum: 844
    # TODO: map to API call
    # assert ...

    # Step 39: Initial enabled: true
    # TODO: map to API call
    # assert ...

    # Step 40: Start: 0
    # TODO: map to API call
    # assert ...

    # Step 41: Period: 2
    # TODO: map to API call
    # assert ...

    # Step 42: Count: 10
    # TODO: map to API call
    # assert ...

    # Step 43: (URL already called above) Report: hello report
    # Step 44: Note the time the rule started.
    # TODO: add assertion
    # assert ...

    # Step 45: Review the displayed reports, verifying:
    # TODO: add assertion
    # assert ...

    # Step 46: (URL already called above) the specified report types were generated
    # Step 47: (URL already called above) the datetime stamp for each report was generated at the specified period
    # Step 48: (URL already called above) the number of reports generated matched the number specified
    # Step 49: Note the number of time-based rules executed and running.
    # TODO: add assertion
    # assert ...

    # Step 50: Repeat this section, for another agent, using Time-Base Rules 2 and 3, as given in Section Test Data
    # TODO: add assertion
    # assert ...

    # Step 51: Verify the reports are displayed on the Monitor option Received Reports panel.
    # TODO: add assertion
    # assert ...

    # Step 52: Multiple Agents
    # TODO: map to API call
    # assert ...

    # Step 53: Select each known agent and then select the option to display the  reports for e
    # GUI interaction
    # Step 54: Note the number of reports for each agent.
    # TODO: add assertion
    # assert ...

    # Step 55: (URL already called above) Select all known agents and submit a request for a "hello" report.
    # Step 56: Select each known agent and then select the option to display the requested  rep
    # GUI interaction
    # Step 57: Verify the specified report was generated for selected agents.
    # TODO: add assertion
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "Reports generated with expected data at the expected rate for specified agent(s)"
    # assert ...  # "Displays on Monitor option reflect the reports generated"


async def test_anms_exp_agt_001(http_client):
    """ANMS_EXP_AGT_001: Agents"""
    # Section: 3.2 Agents
    # Purpose: This test verifies the 'Agents' page displays a list of all known actors on the agent networks.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Areas of Interest
    # TODO: map to API call
    # assert ...

    # Step 2: Confirm agents are displayed with IDs and registration data.
    # TODO: add assertion
    # assert ...

    # Step 3: Confirm displayed agents may be filtered by IDs and registration dates.
    # TODO: add assertion
    # assert ...

    # Step 4: Confirm detailed information may be displayed for a selected agent.
    # TODO: add assertion
    # assert ...

    # Step 5: Filtering
    # TODO: map to API call
    # assert ...

    # Step 6: Agent ID
    # TODO: map to API call
    # assert ...

    # Step 7: Set a filter option based on a complete Agent ID.
    # TODO: map to API call
    # assert ...

    # Step 8: Verify the agent data are filtered to the specified ID.
    # TODO: add assertion
    # assert ...

    # Step 9: Set a filter option based on a partial Agent ID.
    # TODO: map to API call
    # assert ...

    # Step 10: Verify the filtered  agent data includes the specified ID(s).
    # TODO: add assertion
    # assert ...

    # Step 11: Repeat this section with upper and lower case characters.
    # TODO: map to API call
    # assert ...

    # Step 12: Registered Dates
    # TODO: map to API call
    # assert ...

    # Step 13: Set a filter option based on a complete first registered date.  (NOTE: replace alpha characters with
    # TODO: add assertion
    # assert ...

    # Step 14: Verify the agent data are filtered to the specified complete first registered date.
    # TODO: add assertion
    # assert ...

    # Step 15: Set a filter option based on the year, month, day portion of a first registered 
    # TODO: map to API call
    # assert ...

    # Step 16: Verify the agent data are filtered to the specified year/month/day.
    # TODO: add assertion
    # assert ...

    # Step 17: Set a filter option based on the year portion of a first registered date. (NOTE: include field delim
    # TODO: add assertion
    # assert ...

    # Step 18: Verify the agent data are filtered to the specified year. (NOTE: filter may match either first or la
    # TODO: add assertion
    # assert ...

    # Step 19: Set a filter option based on the day portion of a first registered date. (NOTE: include field delimi
    # TODO: add assertion
    # assert ...

    # Step 20: Verify the agent data are filtered to the specified day. (NOTE: filter may match either first or las
    # TODO: add assertion
    # assert ...

    # Step 21: Set a filter option based on the month portion of a first registered date.  (NOTE: include field del
    # TODO: add assertion
    # assert ...

    # Step 22: Verify the agent data are filtered to the specified month.
    # TODO: add assertion
    # assert ...

    # Step 23: Set a filter option based on the time (hour:minute:seconds) portion of a first r
    # TODO: map to API call
    # assert ...

    # Step 24: Verify the agent data are filtered to the specified time.
    # TODO: add assertion
    # assert ...

    # Step 25: Set a filter option based on the hour portion of a first registered date.  (NOTE: include field deli
    # TODO: add assertion
    # assert ...

    # Step 26: Verify the agent data are filtered to the specified hour.
    # TODO: add assertion
    # assert ...

    # Step 27: Set a filter option based on the minute portion of a first registered date.  (NOTE: include field de
    # TODO: add assertion
    # assert ...

    # Step 28: Verify the agent data are filtered to the specified minute.
    # TODO: add assertion
    # assert ...

    # Step 29: Set a filter option based on the second portion of a first registered date.  (NOTE: include field de
    # TODO: add assertion
    # assert ...

    # Step 30: Verify the agent data are filtered to the specified second.
    # TODO: add assertion
    # assert ...

    # Step 31: Repeat this section for the last registered date.
    # TODO: map to API call
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "All Agents are displayed"
    # assert ...  # "Agents may be filtered"


async def test_anms_exp_agt_002(http_client):
    """ANMS_EXP_AGT_002: Manage Agents"""
    # Section: 3.2 Agents
    # Test data: Generate a report: CBOR 0xc1154105050225238187182d410000 URI : ari:/EXECSET/n=7080;(ari://ietf/dtnma-agent/CTRL/inspect(...
    # Purpose: This test verifies agents may be specified and commands may be submitted for known agents.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available. Follow the steps provided in Test Case 'Build and Send Command' to generate a report, which may be viewed in this test case.

    client = await http_client()

    # Step 1: Areas of Interest
    # TODO: map to API call
    # assert ...

    # Step 2: Select the 'Agents' option.
    # GUI interaction
    # Step 3: Confirm options are available to manage agents.
    # TODO: add assertion
    # assert ...

    # Step 4: Manage Agent - Display Agent Reports
    resp = await client.get("http://localhost:5555/nm/api/agents")  # path=/nm/api/agents
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 5: Select a valid agent address and display the details for that agent.
    resp = await client.request("POST", "http://localhost:5555/nm/api/register/agents")  # path=/nm/api/register/agents
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 6: Select the option to display reports for the selected agent.
    # GUI interaction
    # Step 7: Capture a screenshot of the reports displayed for the selected agent
    # TODO: map to API call
    # assert ...

    # Step 8: Manage Agent - Agent Time-Based Report
    # TODO: map to API call
    # assert ...

    # Step 9: Select the option to manage a valid agent from the Agent tab.
    # GUI interaction
    # Step 10: Select the option to build a time based rule.
    # GUI interaction
    # Step 11: Specify a time-based rule using valid parameter entries but specify invalid  Per
    # TODO: map to API call
    # assert ...

    # Step 12: 'o' (character)
    # TODO: map to API call
    # assert ...

    # Step 13: 2.5
    # TODO: map to API call
    # assert ...

    # Step 14: -3
    # TODO: map to API call
    # assert ...

    # Step 15: Verify error messages are generated for invalid Period entries.
    # TODO: add assertion
    # assert ...

    # Step 16: Specify a time-based rule using valid parameter entries but specify invalid Star
    # TODO: map to API call
    # assert ...

    # Step 17: 'o' (character)
    # TODO: map to API call
    # assert ...

    # Step 18: 2.5
    # TODO: map to API call
    # assert ...

    # Step 19: -2
    # TODO: map to API call
    # assert ...

    # Step 20: Verify error messages are generated for invalid Start entries.
    # TODO: add assertion
    # assert ...

    # Step 21: Specify a time-based rule using valid parameter entries but specify invalid Coun
    # TODO: map to API call
    # assert ...

    # Step 22: 'o' (character)
    # TODO: map to API call
    # assert ...

    # Step 23: 3.5
    # TODO: map to API call
    # assert ...

    # Step 24: -2
    # TODO: map to API call
    # assert ...

    # Step 25: Verify error messages are generated for invalid Count entries.
    # TODO: add assertion
    # assert ...

    # Step 26: Manage Agent - Build Command
    # TODO: map to API call
    # assert ...

    # Step 27: (URL already called above) Specify a valid agent address to manage.
    # Step 28: Submit the CBOR string specified in the Section Test Data for the test to transl
    # TODO: map to API call
    # assert ...

    # Step 29: Verify no error messages are generated.
    # TODO: add assertion
    # assert ...

    # Step 30: Select the option to send the command.
    # GUI interaction
    # Step 31: Verify there are no errors generated.
    # TODO: add assertion
    # assert ...

    # Step 32: Select the option to display the agent reports.
    # GUI interaction
    # Step 33: Verify the expected report was generated.
    # TODO: add assertion
    # assert ...

    # Step 34: Manage Agent - Clear Agent Tables [OBSOLETE]
    # GUI interaction
    # Step 35: Specify the same valid agent address to manage and select the 'Manage agent' opt
    # GUI interaction
    # Step 36: Verify a success message is generated.
    # TODO: add assertion
    # assert ...

    # Step 37: Select the option to display a report for the selected agent.
    # GUI interaction
    # Step 38: Verify the selected agent has no reports displayed.
    # TODO: add assertion
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "Specified options are executed for selected Agents."


async def test_anms_exp_agt_003(http_client):
    """ANMS_EXP_AGT_003: Registration"""
    # Section: 3.2 Agents
    # Purpose: This test verifies registration of alerts for a user.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Areas of Interest
    # TODO: map to API call
    # assert ...

    # Step 2: Register request for notification.
    # TODO: map to API call
    # assert ...

    # Step 3: Notification registrations are stored in TBD table.
    # GUI interaction
    # Step 4: Register request
    # TODO: map to API call
    # assert ...

    # Step 5: Use TBD option to send a registration request.
    # TODO: map to API call
    # assert ...

    # Step 6: Match the user-specific request for notifications with the associated alert tabl
    # GUI interaction
    # Step 7: Deny registration
    # TODO: map to API call
    # assert ...

    # Step 8: Use TBD option to send a registration request.
    # TODO: map to API call
    # assert ...

    # Step 9: Inform user of request denial.
    # TODO: map to API call
    # assert ...


async def test_anms_exp_agt_004(http_client):
    """ANMS_EXP_AGT_004: Alerts"""
    # Section: 3.2 Agents
    # Test data: NOTE: refer to Section Test Environment Setup: Current Testing for instructions on accessing a terminal. If no alerts ar...
    # Purpose: This test verifies alerts are generated and received.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Areas of Interest
    # TODO: map to API call
    # assert ...

    # Step 2: Alerts are sent.
    # TODO: map to API call
    # assert ...

    # Step 3: Alerts are displayed.
    # TODO: map to API call
    # assert ...

    # Step 4: Display Alert
    # TODO: map to API call
    # assert ...

    # Step 5: Select each page.
    # TODO: map to API call
    # assert ...

    # Step 6: Verify any alerts are displayed.  If no alerts are displayed, refer to Section Test Data in the test
    # TODO: add assertion
    # assert ...

    # Step 7: Deactivate Alert
    # TODO: map to API call
    # assert ...

    # Step 8: Deactivate a displayed alert.
    # TODO: map to API call
    # assert ...

    # Step 9: Verify alert is removed from the display.
    # TODO: add assertion
    # assert ...

    # Step 10: Deactivate any remaining displayed alerts.
    # TODO: map to API call
    # assert ...

    # Step 11: Receive Alert
    # TODO: map to API call
    # assert ...

    # Step 12: Refer to Section Test Data in the test case to restart services and add agents.
    # TODO: map to API call
    # assert ...

    # Step 13: Verify alerts are displayed.
    # TODO: add assertion
    # assert ...

    # Step 14: Deactivate any displayed alerts.
    # TODO: map to API call
    # assert ...

    # Step 15: Using the Agents option, add an agent (add node) to generate an alert.
    resp = await client.request("POST", "http://localhost:5555/nm/api/register/agents")  # path=/nm/api/register/agents
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 16: Verify the alert(s) is displayed on each page, including the user profile.
    # TODO: add assertion
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "Alerts are displayed on each page"
    # assert ...  # "Alerts may be removed from display"

