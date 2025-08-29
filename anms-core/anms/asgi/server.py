#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 The Johns Hopkins University Applied Physics
# Laboratory LLC.
#
# This file is part of the Asynchronous Network Management System (ANMS).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This work was performed for the Jet Propulsion Laboratory, California
# Institute of Technology, sponsored by the United States Government under
# the prime contract 80NM0018D0004 between the Caltech and NASA under
# subcontract 1658085.
#
import ssl
import sys

import uvicorn

from anms.asgi import FastApiApp
from anms.shared.config_utils import ConfigBuilder

app = FastApiApp.get_new_app()


def main() -> None:
    config = ConfigBuilder.get_config()

    uvicorn.run(f"{__name__}:app", host=config['SERVER_BIND'], port=config['SERVER_PORT'],
                    log_config=None, log_level=config['LOGGER_LEVEL'], access_log=False,  # We use our own logger
                    reload=config['DEBUG'])


if __name__ == "__main__":
    sys.exit(main())  # type: ignore
