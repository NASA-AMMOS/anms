"""Auto-generated from ANMS Test Specification section 2.5.
  Cases: 5, Steps available: 5/5
  Run: pytest -xvs tests/generated/test_adm.py
  Requires: docker/podman compose up -d (in repo root)
"""

import pytest

# Section: 2.5 | Cases: 5 | With steps: 5

async def test_anms_fun_adm_001(http_client):
    """ANMS_FUN_ADM_001: ADM Listing"""
    # Section: 2.5 Application Data Model (ADM)
    # Purpose: This test verifies the user may display the current ADMs with related information.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Export an ADM
    resp = await client.get("http://localhost:5555/nm/api/adms")  # path=/nm/api/adms
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 2: (URL already called above) Using the ADM option, select an ADM.
    # Step 3: Select the option to export the ADM.
    # GUI interaction
    # Step 4: Verify no errors occur for the ADM export.
    # TODO: add assertion
    # assert ...

    # Step 5: (URL already called above) Repeat this section for another ADM listed.
    # Step 6: Review ADMs
    # TODO: map to API call
    # assert ...

    # Step 7: (URL already called above) Retrieve the IETF ADM specifications for the ADMs dowloaded.
    # Step 8: (URL already called above) Compare to the IETF specification to the exported  ADMs .
    # Step 9: Verify there are no discrepancies in the definitions.
    # TODO: add assertion
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "ADMs displayed comply with the IETF specifications"


async def test_anms_fun_adm_002(http_client):
    """ANMS_FUN_ADM_002: Upload New, Valid ADM"""
    # Section: 2.5 Application Data Model (ADM)
    # Test data: Test ADM Use the ADM supplied in \\ANMS\Testing\Data\ADMs\ANMS_FUN_ADM_002 (Upload New, Valid ADM) to upload the initial...
    # Purpose: This test allows the user to upload a new Application Data Model (ADM)
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Upload New ADM
    # TODO: map to API call
    # assert ...

    # Step 2: Remove any instance of the test ADM before executing the test:
    # TODO: map to API call
    # assert ...

    # Step 3: HYPERLINK "http://anms-test:5555/docs/#/ADM/remove_adm_adms_remove__adm_enum__post"http://anms-test:
    resp = await client.request("POST", "http://localhost:5555/nm/api/adms")  # path=http://localhost:5555/nm/api/adms
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 4: with the enum of the added ADM.
    # TODO: map to API call
    # assert ...

    # Step 5: Using the ADM option, select the option to upload a new ADM, as defined in Secti
    # GUI interaction
    # Step 6: Verify no errors are generated when the new ADM is uploaded.
    # TODO: add assertion
    # assert ...

    # Step 7: Select the option to display available ADMs.
    # GUI interaction
    # Step 8: Verify the new ADM is displayed.
    # TODO: add assertion
    # assert ...

    # Step 9: Verify the ARIs panel under the Monitor option displays the ARIs from the upload
    # GUI interaction
    # Step 10: Verify the ARIs from the uploaded ADM are displayed in the ARI Builder.
    # TODO: add assertion
    # assert ...

    # Step 11: (URL already called above) Export New ADM
    # Step 12: (URL already called above) Using the ADM option, select the new ADM.
    # Step 13: Select the option to export the ADM.
    # GUI interaction
    # Step 14: Verify no errors occur for the ADM export.
    # TODO: add assertion
    # assert ...

    # Step 15: Verify the exported ADM matches the source of the selected ADM.
    # TODO: add assertion
    # assert ...

    # Step 16: Verify Database
    # TODO: add assertion
    # assert ...

    # Step 17: Open the database table for ADMs.
    # TODO: execute SQL against PostgreSQL
    # assert ...

    # Step 18: Verify the table includes the uploaded ADM.
    # GUI interaction
    # Step 19: Verify the namespace database table for the new namespace
    # TODO: add assertion
    # assert ...

    # Step 20: Run an SQL query to retrieve the metadata for the new namespace.
    # TODO: execute SQL against PostgreSQL
    # assert ...

    # Step 21: Verify the obj_metadata database table contains the data from the new ADM
    # TODO: add assertion
    # assert ...

    # Step 22: To remove the uploaded ADM, exercise:
    # TODO: map to API call
    # assert ...

    # Step 23: (URL already called above) HYPERLINK "http://anms-test:5555/docs/#/ADM/remove_adm_adms_remove__adm_enum__po
    # Step 24: with the enum of the added ADM.
    # TODO: map to API call
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "New ADMs are uploaded"
    # assert ...  # "New ADM display complies with the definition for it"
    # assert ...  # "New ADM exports matches the definition and display"


async def test_anms_fun_adm_003(http_client):
    """ANMS_FUN_ADM_003: Upload New, Invalid ADM"""
    # Section: 2.5 Application Data Model (ADM)
    # Test data: Test ADM files are found under \\ANMS\Testing\Data\ADMs\ANMS_FUN_ADM_003 (Upload New, Invalid ADM) include the following...
    # Purpose: This test informs the user when a new, invalid Application Data Model (ADM) is being uploaded.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Upload ADM with Missing Delimiter
    resp = await client.request("DELETE", "http://localhost:5555/nm/api/adms")  # path=/nm/api/adms
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 2: Remove any instance of the test ADM before executing the test:
    # TODO: map to API call
    # assert ...

    # Step 3: (URL already called above) HYPERLINK "http://anms-test:5555/docs/#/ADM/remove_adm_adms_remove__adm_enum__po
    # Step 4: with the enum of the added ADM.
    # TODO: map to API call
    # assert ...

    # Step 5: Using the ADM option, select the option to upload the ADM with missing delimiter
    # GUI interaction
    # Step 6: Supply any details needed to upload the new ADM.
    # TODO: map to API call
    # assert ...

    # Step 7: Verify errors are generated when the new ADM is uploaded.
    # TODO: add assertion
    # assert ...

    # Step 8: Select the option to display available ADMs.
    # GUI interaction
    # Step 9: Verify the new ADM is not displayed.
    # TODO: add assertion
    # assert ...

    # Step 10: Open the database table for ADMs.
    # TODO: execute SQL against PostgreSQL
    # assert ...

    # Step 11: Verify the table(s) do not include the invalid ADM.
    # GUI interaction
    # Step 12: Upload ADM with Invalid Type
    # TODO: map to API call
    # assert ...

    # Step 13: Remove any instance of the test ADM before executing the test:
    # TODO: map to API call
    # assert ...

    # Step 14: (URL already called above) HYPERLINK "http://anms-test:5555/docs/#/ADM/remove_adm_adms_remove__adm_enum__po
    # Step 15: with the enum of the added ADM.
    # TODO: map to API call
    # assert ...

    # Step 16: Using the ADM option, select the option to upload the ADM with type errors, as d
    # GUI interaction
    # Step 17: Supply any details needed to upload the new ADM .
    # TODO: map to API call
    # assert ...

    # Step 18: Verify errors are generated when the new ADM is uploaded.
    # TODO: add assertion
    # assert ...

    # Step 19: Select the option to display available ADMs.
    # GUI interaction
    # Step 20: Verify the new ADM is not displayed.
    # TODO: add assertion
    # assert ...

    # Step 21: Verify errors found with the ADM are displayed.
    # TODO: add assertion
    # assert ...

    # Step 22: Open the database table for ADMs.
    # TODO: execute SQL against PostgreSQL
    # assert ...

    # Step 23: Verify the table(s) do not include the invalid ADM.
    # GUI interaction
    # Step 24: Upload ADM with Invalid Operation
    # TODO: map to API call
    # assert ...

    # Step 25: Remove any instance of the test ADM before executing the test:
    # TODO: map to API call
    # assert ...

    # Step 26: (URL already called above) HYPERLINK "http://anms-test:5555/docs/#/ADM/remove_adm_adms_remove__adm_enum__po
    # Step 27: with the enum of the added ADM.
    # TODO: map to API call
    # assert ...

    # Step 28: Using the ADM option, select the option to upload the ADM with the invalid opera
    # GUI interaction
    # Step 29: Supply any details needed to upload the new ADM .
    # TODO: map to API call
    # assert ...

    # Step 30: Verify errors are generated when the new ADM is uploaded.
    # TODO: add assertion
    # assert ...

    # Step 31: Select the option to display available ADMs.
    # GUI interaction
    # Step 32: Verify the new ADM is not displayed.
    # TODO: add assertion
    # assert ...

    # Step 33: Verify errors found with the ADM are displayed.
    # TODO: add assertion
    # assert ...

    # Step 34: Open the database table for ADMs.
    # TODO: execute SQL against PostgreSQL
    # assert ...

    # Step 35: Verify the table(s) do not include the invalid ADM.
    # GUI interaction
    # Step 36: Verify Database
    # TODO: add assertion
    # assert ...

    # Step 37: Open the database table for ADMs.
    # TODO: execute SQL against PostgreSQL
    # assert ...

    # Step 38: Verify the table(s) do not include the invalid ADM.
    # GUI interaction
    # === Expected outcomes from specification ===
    # assert ...  # "Invalid ADMs generate error messages"
    # assert ...  # "Database ADM tables are not updated"


async def test_anms_fun_adm_004(http_client):
    """ANMS_FUN_ADM_004: Valid Modifications to Existing ADM"""
    # Section: 2.5 Application Data Model (ADM)
    # Test data: Use the modified ADMs provided in \\ANMS\Testing\Data\ADMs\ANMS_FUN_ADM_004 (Valid Modifications to Existing ADM). This ...
    # Purpose: This test allows the user to modify an existing Application Data Model (ADM).
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Remove any instance of the test ADM before executing the test:
    # TODO: map to API call
    # assert ...

    # Step 2: HYPERLINK "http://anms-test:5555/docs/#/ADM/remove_adm_adms_remove__adm_enum__post"http://anms-test:
    resp = await client.request("POST", "http://localhost:5555/nm/api/adms")  # path=http://localhost:5555/nm/api/adms
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 3: with the enum of the added ADM.
    # TODO: map to API call
    # assert ...

    # Step 4: Execute the following sections for each modified ADM.
    # TODO: map to API call
    # assert ...

    # Step 5: Uploaded Modification for Existing ADM
    # TODO: map to API call
    # assert ...

    # Step 6: (URL already called above) Use the ADM option to upload each modified ADM.
    # Step 7: Verify no errors are generated.
    # TODO: add assertion
    # assert ...

    # Step 8: Verify the modification is reflected in the Build option ARI selections.
    # TODO: add assertion
    # assert ...

    # Step 9: (URL already called above) Export Modified ADM
    # Step 10: (URL already called above) Using the ADM option, select the modified ADM.
    # Step 11: Select the option to export the ADM.
    # GUI interaction
    # Step 12: Verify no errors occur for the ADM export.
    # TODO: add assertion
    # assert ...

    # Step 13: Verify the exported ADM matches the source of the selected ADM.
    # TODO: add assertion
    # assert ...

    # Step 14: Verify Database
    # TODO: add assertion
    # assert ...

    # Step 15: Open the database table for ADMs.
    # TODO: execute SQL against PostgreSQL
    # assert ...

    # Step 16: Verify the table(s) match the modified ADM.
    # GUI interaction
    # Step 17: Run an SQL query to retrieve the metadata for the modified namespace.
    # TODO: execute SQL against PostgreSQL
    # assert ...

    # Step 18: Verify the database table contains the data from the new ADM.
    # TODO: add assertion
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "An existing ADM may be modified"
    # assert ...  # "Database reflects ADM modifications"
    # assert ...  # "Modified ADM may be exported"


async def test_anms_fun_adm_005(http_client):
    """ANMS_FUN_ADM_005: Invalid Modifications to Existing ADM"""
    # Section: 2.5 Application Data Model (ADM)
    # Test data: Test ADM files are found under \\ANMS\Testing\Data\ADMs\ANMS_FUN_ADM_004 (Invalid Modifications to Existing ADM) include...
    # Purpose: This test verifies an ADM is verified for completeness and compliance.  This test also verifies modifications to an existing ADM are verified.
    # Preconditions: The test environment, procedures, and tools identified in Section Test Environment are available.

    client = await http_client()

    # Step 1: Valid baseline ADM
    # TODO: map to API call
    # assert ...

    # Step 2: Remove any instance of the test ADM before executing the test:
    # TODO: map to API call
    # assert ...

    # Step 3: HYPERLINK "http://anms-test:5555/docs/#/ADM/remove_adm_adms_remove__adm_enum__post"http://anms-test:
    resp = await client.request("POST", "http://localhost:5555/nm/api/adms")  # path=http://localhost:5555/nm/api/adms
    assert resp.status_code in (200, 201, 204, 206), f"GET {resp.url}: {resp.status_code} {resp.text[:200]}"
    data = resp.json()  if resp.headers.get("content-type","").startswith("application/json") else None

    # Step 4: with the enum of the added ADM(s).
    # TODO: map to API call
    # assert ...

    # Step 5: (URL already called above) Use the ADM option to upload the baseline ADM (see Section Test Data).
    # Step 6: Verify no errors are generated.
    # TODO: add assertion
    # assert ...

    # Step 7: (URL already called above) Use the ADM option to export the selected ADM.
    # Step 8: Verify the obj_metadata database table contains the data from the baseline ADM.
    # TODO: add assertion
    # assert ...

    # Step 9: (URL already called above) Use the obj_metadata or similar database table to export the data from the basel
    # Step 10: Invalid Modifications to existing ADM
    # TODO: map to API call
    # assert ...

    # Step 11: Import an ADM  given in Section Test Data.
    # TODO: map to API call
    # assert ...

    # Step 12: Verify errors messages are generated.
    # TODO: add assertion
    # assert ...

    # Step 13: (URL already called above) Use the ADM option to export the ADM.
    # Step 14: (URL already called above) Compare the export to the export from the baseline ADM.
    # Step 15: Verify the ADM is not modified.
    # TODO: add assertion
    # assert ...

    # Step 16: (URL already called above) Use the obj_metadata or similar database table to export the data from the ADM.
    # Step 17: Verify this export matches the database export for the baseline ADM.
    # TODO: add assertion
    # assert ...

    # Step 18: Refresh the ADM page.
    # TODO: map to API call
    # assert ...

    # Step 19: Repeat this section for the remaining invalid modifications to the ADM.
    # TODO: map to API call
    # assert ...

    # === Expected outcomes from specification ===
    # assert ...  # "Invalid modifications to an existing ADM are rejected"
    # assert ...  # "Database tables retain the original ADM data"

