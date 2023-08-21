<!--
Copyright (c) 2023 The Johns Hopkins University Applied Physics
Laboratory LLC.

This file is part of the Asynchronous Network Managment System (ANMS).

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
# anms-core

Python-based Uvicorn centralized server for ANMS

## Copyright

Copyright (C) 2022 The Johns Hopkins University Applied Physics Laboratory LLC.

## Setting up environment and installing dependencies

1. pip install virtualenv
2. python3 -m virtualenv venv
3. source venv/bin/activate
4. pip3 install --upgrade pip pip-tools
5. pip-compile pyproject.toml
6. pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

### Running

During development the system can be started with `python3 run_dev.py`.

## Configuration

A default set of configuration values are defined in `anms/shared/config.py`. Configuration items may be overridden via
a configuration file or by setting environment variables. Configuration items read from the configuration file override
the default values and items read from environment variables override both those defined in a configuration file and the
default configuration.  
When running locally, the argument `-c LocalConfig` can be used to set hostnames to `localhost`

### Configuration by File

A configuration file named `config.yaml` may be placed in the `anms` directory. This file is expected to contain
configuration in YAML file format (e.g. `NAME: VALUE`). Configuration items defined in this file will override the
default configuration value with a matching name.

### Configuration by Environment Variables

Environment variables with the prefix "ANMS_CORE_" are applied as configuration overrides. Environment variables will
override the file-based and default configuration value with a matching name (excluding the prefix). For example, to
override the configuration item SERVER_HOST, set an environment variable named ANMS_CORE_SERVER_HOST.