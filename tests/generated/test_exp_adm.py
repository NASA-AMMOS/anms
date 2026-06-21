"""Auto-generated from ANMS Test Specification section 3.5.
  Cases: 2, Steps available: 2/2
  Run: pytest -xvs tests/generated/test_exp_adm.py
  Requires: docker/podman compose up -d (in repo root)
"""

import pytest

# Section: 3.5 | Cases: 2 | With steps: 2

async def test_anms_exp_adm_001(http_client):
    """ANMS_EXP_ADM_001: Display"""
    # Section: 3.5 Application Data Module (ADM)
    # Purpose: This test displays the available Application Data Models (ADMs)
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Areas of Interest
    # TODO: map to API call
    # assert ...

    # Step 2: ADMs may be downloaded
    resp = await client.request("POST", "http://localhost:5555/nm/api/adms")  # path=/nm/api/adms
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 3: (URL already called above) Download Listed ADM
    # Step 4: Using the ADM option, verify ADMs are displayed.
    # TODO: add assertion
    # assert ...

    # Step 5: Select the option to download one of the displayed ADMs.
    # GUI interaction
    # Step 6: Verify no errors occur for the ADM export.
    # TODO: add assertion
    # assert ...

    # Step 7: Open the ADM downloaded. (Note: a text tool must be used to view the ADM.)
    # TODO: add assertion
    # assert ...

    # Step 8: Close the ADM.
    # TODO: map to API call
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "Existing ADMs are listed"
    # assert ...  # "Selected ADMs may be downloaded"


async def test_anms_exp_sys_001(http_client):
    """ANMS_EXP_SYS_001: User Profile"""
    # Section: 3.5 Application Data Module (ADM)
    # Purpose: This test case exercises the option for a user to manage her profile.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Areas of Interest
    # TODO: map to API call
    # assert ...

    # Step 2: Log in.
    # TODO: map to API call
    # assert ...

    # Step 3: Display current user information.
    # TODO: map to API call
    # assert ...

    # Step 4: Manage user information.
    # TODO: map to API call
    # assert ...

    # Step 5: Review User Profile
    # TODO: map to API call
    # assert ...

    # Step 6: Log on with valid user ID and password.
    # TODO: map to API call
    # assert ...

    # Step 7: Select the 'User' information option for the current user.
    # TODO: map to API call
    # assert ...

    # Step 8: Review the information displayed for the current user.
    # TODO: map to API call
    # assert ...

    # Step 9: Create User Profile
    # TODO: map to API call
    # assert ...

    # Step 10: If no information is displayed for the current user, supply the available fields.  Otherwise, modify
    # TODO: add assertion
    # assert ...

    # Step 11: Select the option to save the change.
    # GUI interaction
    # Step 12: Logout of the session.
    # TODO: map to API call
    # assert ...

    # Step 13: Login as the same user.
    # TODO: map to API call
    # assert ...

    # Step 14: Select the 'User' option.
    # TODO: map to API call
    # assert ...

    # Step 15: Review the information displayed for the current user.
    # TODO: map to API call
    # assert ...

    # Step 16: Verify the user information supplied was retained.
    # TODO: add assertion
    # assert ...

    # Step 17: Modify and Save User Email
    # TODO: map to API call
    # assert ...

    # Step 18: Modify the Email address for the user.
    # TODO: map to API call
    # assert ...

    # Step 19: Select the option to save the change.
    # GUI interaction
    # Step 20: Logout of the session.
    # TODO: map to API call
    # assert ...

    # Step 21: Login as the same user.
    # TODO: map to API call
    # assert ...

    # Step 22: Select the 'User' option.
    # TODO: map to API call
    # assert ...

    # Step 23: Review the information displayed for the current user.
    # TODO: map to API call
    # assert ...

    # Step 24: Verify the user Email change was retained.
    # TODO: add assertion
    # assert ...

    # Step 25: Modify and Abandon
    # TODO: map to API call
    # assert ...

    # Step 26: Modify the Email address for the user.
    # TODO: map to API call
    # assert ...

    # Step 27: Select the option to abandon the change.
    # GUI interaction
    # Step 28: Logout of the session.
    # TODO: map to API call
    # assert ...

    # Step 29: Login as the same user.
    # TODO: map to API call
    # assert ...

    # Step 30: Select the 'User' option.
    # TODO: map to API call
    # assert ...

    # Step 31: Review the information displayed for the current user.
    # TODO: map to API call
    # assert ...

    # Step 32: Verify the user Email change was not retained.
    # TODO: add assertion
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "User's details may be modified and updated without errors, and modifications may be abandoned"

