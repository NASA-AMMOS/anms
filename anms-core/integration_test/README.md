<!--
Copyright (c) 2023 The Johns Hopkins University Applied Physics
Laboratory LLC.

This file is part of the Asynchronous Network Management System (ANMS).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This work was performed for the Jet Propulsion Laboratory, California
Institute of Technology, sponsored by the United States Government under
the prime contract 80NM0018D0004 between the Caltech and NASA under
subcontract 1658085.
-->
# Development Notes

The steps to create/update integration tests with the anms-core REST API are the following:

1. Install Postman from [postman.com](https://www.postman.com/downloads/).
2. Install newman (CLI tool/javscript library) via `yarn install`, from this directory, or in general `yarn add global newman`.
3. Start the server, via `python run_dev.py` or via docker/docker-compose, just need to have the OpenAPI/Redocs pages
4. Retrieve the OpenAPI json specification file from either localhost:5555/docs or localhost:5555/redoc.
    - Note: The latest openapi.json file should exist in this directory, but just in case you can export it.
5. (Optional) Import the collection into postman and ensure it looks correct.
6. (Optional) If a newer version of openapi.json was imported into Postman, export it as a json file. 
   - You will need to manually merge new content from outputted json file into integration_tests.json or
   - You can make updates in Postman manually and then output as integration_tests.json
7. Run newman CLI tool to execute REST API tests in integration_tests.json, via `newman run integration_tests.json.
   - If the newman module was installed but is not part of the path you can replace above with `node node_modules/newman/bin/newman.js`.