<!--
Copyright (c) 2026 The Johns Hopkins University Applied Physics
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
This file will contain upgrading instructions for all future tagged releases.

# Upgrading v2.0.0 to v3.0.0

Data preservation is not currently supported and it is recommended to reset the database with  `podman volume rm anms_postgres-data` if not starting with a clean system.

If you have a need to preserve ANMS data during upgrade, please reach out to the dev team or submit a feature request to discuss.


# Upgrading v1.x to v.2.0.0

It is recommended to start fresh (delete any existing ANMS-related containers and volumes) when transitioning from ANMS v1 to v2.

If you have data or customizations in a v1 installation that you need to migrate, please contact us or open an issue to discuss.

