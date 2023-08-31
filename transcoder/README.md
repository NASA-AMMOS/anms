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
# ANMS Transcoder
An AsyncAPI component for handling encoding and decoding request from ANMS-CORE and send them to any available codex .


## Copyright

Copyright (C) 2022 The Johns Hopkins University Applied Physics Laboratory LLC.

## Setting up environment and installing dependencies

1. pip install virtualenv
2. python3 -m virtualenv venv
3. source venv/bin/activate
4. pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

## Configuration

A default set of configuration values are defined in `src/config.ini`.

set up a mqtt message broker 
docker run -it -p 0.0.0.0:1883:1883 -p 0.0.0.0:9001:9001 -v $PWD/../samples/mosquitto.conf:/mosquitto/config/mosquitto.conf  eclipse-mosquitto

### testing 

`PYTHONPATH=$(pwd)/src/ python3 -m pytest  src/`