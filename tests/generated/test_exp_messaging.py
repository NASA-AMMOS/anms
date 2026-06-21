"""Auto-generated from ANMS Test Specification section 3.3.
  Cases: 1, Steps available: 1/1
  Run: pytest -xvs tests/generated/test_exp_messaging.py
  Requires: docker/podman compose up -d (in repo root)
"""

import pytest

# Section: 3.3 | Cases: 1 | With steps: 1

async def test_anms_exp_bld_001(http_client):
    """ANMS_EXP_BLD_001: Navigation"""
    # Section: 3.3 Messaging [OBSOLETE]
    # Purpose: This test verifies the user has the options to build an ARI and view the results.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Areas of Interest
    # TODO: map to API call
    # assert ...

    # Step 2: Select the 'Build' option.
    # GUI interaction
    # Step 3: Confirm dialogs are available for building an ARI.
    # GUI interaction
    # Step 4: Confirm dialogs are available for translating an input string.
    # GUI interaction
    # Step 5: Confirm a table is displayed for results from building an ARI.
    # GUI interaction
    # Step 6: Confirm multiple pages of displayed results may be navigated.
    # TODO: add assertion
    # assert ...

    # Step 7: Search ARIs
    # TODO: map to API call
    # assert ...

    # Step 8: Open the list of available ARIs.
    # TODO: map to API call
    # assert ...

    # Step 9: Scroll through the list of available ARIs.
    # TODO: map to API call
    # assert ...

    # Step 10: Enter the string 'ctrl' in the search field.
    # TODO: map to API call
    # assert ...

    # Step 11: Verify the available ARIs matching the string are displayed.
    # TODO: add assertion
    # assert ...

    # Step 12: Enter the string 'edd' in the search field.
    # TODO: map to API call
    # assert ...

    # Step 13: Verify the available ARIs matching the string are displayed.
    # TODO: add assertion
    # assert ...

    # Step 14: Select one of the ARIs displayed.
    # TODO: add assertion
    # assert ...

    # Step 15: Verify all fields are cleared when the ARI cancel option is selected.
    # TODO: add assertion
    # assert ...

    # Step 16: Build ARI
    resp = await client.request("POST", "http://localhost:5555/nm/api/ari")  # path=/nm/api/ari
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 17: Select the option to list ARIs available for selection.
    # GUI interaction
    # Step 18: Enter the string 'report' in the search field.
    # TODO: map to API call
    # assert ...

    # Step 19: Verify the available ARIs matching the string are displayed.
    # TODO: add assertion
    # assert ...

    # Step 20: (URL already called above) Select any ARI from the list.
    # Step 21: Verify the parameters for the selected ARI are displayed for selection.
    # TODO: add assertion
    # assert ...

    # Step 22: Create and submit the selected parameter(s).
    # TODO: map to API call
    # assert ...

    # Step 23: Submit the specified ARI.
    # TODO: map to API call
    # assert ...

    # Step 24: NOTE: if the submission currently exists in the transcoder log, a message is expected to be displaye
    # TODO: add assertion
    # assert ...

    # Step 25: Select the option to clear the ARI string selected.
    # GUI interaction
    # Step 26: Verify the string and parameters are cleared.
    # TODO: add assertion
    # assert ...

    # Step 27: Verify the log table is updated with the results.
    # GUI interaction
    # Step 28: Verify a CBOR string is generated.
    # TODO: add assertion
    # assert ...

    # Step 29: Log Filtering
    # TODO: map to API call
    # assert ...

    # Step 30: Generate more rows in the transcoder log, if needed, to be able to display more than one page.  Redu
    resp = await client.get("http://localhost:5555/nm/api/report")  # path=/nm/api/report
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 31: Set a filter option based on a displayed Log ID.
    # TODO: map to API call
    # assert ...

    # Step 32: Verify the data are filtered to the specified ID(s).
    # TODO: add assertion
    # assert ...

    # Step 33: Set a filter option based on a displayed input string.
    # TODO: map to API call
    # assert ...

    # Step 34: Verify the data are filtered to the specified string.
    # TODO: add assertion
    # assert ...

    # Step 35: Set a filter option based on a displayed URI.
    # TODO: map to API call
    # assert ...

    # Step 36: Verify the data are filtered to the specified URI.
    # TODO: add assertion
    # assert ...

    # Step 37: Set a filter option based on a displayed CBOR string.
    # TODO: map to API call
    # assert ...

    # Step 38: Verify the data are filtered to the specified CBOR string.
    # TODO: add assertion
    # assert ...

    # Step 39: Clear all filters.
    # TODO: map to API call
    # assert ...

    # Step 40: Navigation
    # TODO: map to API call
    # assert ...

    # Step 41: Modify the number of items per page.
    # TODO: map to API call
    # assert ...

    # Step 42: Verify the specified number of items are displayed per page.
    # TODO: add assertion
    # assert ...

    # Step 43: Verify the number of pages to navigate reflects the distribution of items per page.
    # TODO: add assertion
    # assert ...

    # Step 44: Exercise the option to select the next page.
    # TODO: map to API call
    # assert ...

    # Step 45: Verify the next page is displayed.
    # TODO: add assertion
    # assert ...

    # Step 46: Exercise the option to select the previous page.
    # TODO: map to API call
    # assert ...

    # Step 47: Verify the previous page is displayed.
    # TODO: add assertion
    # assert ...

    # Step 48: Exercise the option to select the last page.
    # TODO: map to API call
    # assert ...

    # Step 49: Verify the last page is displayed.
    # TODO: add assertion
    # assert ...

    # Step 50: Exercise the option to select the first page.
    # TODO: map to API call
    # assert ...

    # Step 51: Verify the first page is displayed.
    # TODO: add assertion
    # assert ...

    # Step 52: Select a page number from those displayed.
    # TODO: map to API call
    # assert ...

    # Step 53: Verify the selected page is displayed.
    # TODO: add assertion
    # assert ...

    # Step 54: CBOR
    # TODO: map to API call
    # assert ...

    # Step 55: Paste a CBOR string into the CBOR to translate field.
    # TODO: map to API call
    # assert ...

    # Step 56: Verify the transcoder log provides the expected translation.
    # TODO: add assertion
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "Build option displays dialogs for specifying an ARI and parameters"
    # assert ...  # "Searches may be conducted for specific ARIs"
    # assert ...  # "The results log may be filtered"
    # assert ...  # "The number of results per page in the log may be modified and the pages navigated"

