<!--
Copyright (c) 2022-2026 The Johns Hopkins University Applied Physics
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
#  AMMOS ANMS

This is the quickstart documentation for the AMMOS Asynchronous Network Management System (ANMS).

### Copyright

Copyright (C) 2022-2026 The Johns Hopkins University Applied Physics Laboratory LLC.

# Start Here: Which Documentation Should You Use?

ANMS supports multiple types of users. The appropriate documentation depends on how you are interacting with the system.

**1. Are you installing ANMS from this source repository?**

If yes, then use this README for:
* Quickstart instructions
* Installation steps
* Basic configuration
* High-level overview

For detailed operational guidance after installation, refer to the ANMS User Guide, found here: www.nasa-ammos.github.io/anms-docs/.

**2. Are you an AMMOS user or operating an already-installed ANMS instance (not from source)?**

If yes, do not rely on this README for operational guidance. Refer to the ANMS Product Guide and ANMS User Guide for:
* System usage
* Operational workflows
* Configuration details

**NOTE:** These guides apply to *all* users once ANMS is installed.

**3. Are you a developer contributing to ANMS or setting up a development environment?**

If yes, refer to both this README and the ANMS Wiki [Development Guide](https://github.com/NASA-AMMOS/anms/wiki/Development-Guide) for:
* Local development environment configuration
* Testing workflows
* Contribution guidelines
* Additional troubleshooting guidance

# Quick Start

This section details prerequisites to installing the ANMS from source on a development system and gives a brief explanation of the container configuration.

## Dependencies

### Software and OS Versions

The setup of ANMS and demos listed in this README have been tested on macOS 11.6.4 (Big Sur), RHEL 9 and Ubuntu 20.04.
To run the ANMS tool, you must also install Docker Engine version 20.10.10 or newer or Podman 5.2.2+.  You will also need either Docker Compose version 1.29.2+ or podman-compose.  Docker and Podman can generally be used interchangeably. 

**NOTE:** `docker-compose` can be used with `podman`, and `docker-compose` is generally preferred for environment stability.

## Installation

To get started with a local instance of ANMS, clone this repository and use the provided orchestration scripts:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NASA-AMMOS/anms.git
   cd anms
   ```
2. **Launch the environment:**
   ```bash
   docker-compose up -d
   ```
3. **Access the Interface:**
   Once the containers are healthy, the ANMS dashboard is typically available at `http://localhost:3000`.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file or the header of this document for full details.