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

    # SSL Settings
    should_start_with_ssl = (
        config['SERVER_SSL'] is True
        and config['SERVER_BEHIND_PROXY'] is False
        and isinstance(config['SERVER_SSL_CRT'], str)
        and isinstance(config['SERVER_SSL_KEY'], str)
    )
    # Preferred method is to use NGINX/reverse proxy with SSL Termination
    if should_start_with_ssl:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)  # disable SSLv3
        ssl_context.options |= ssl.OP_NO_TLSv1  # disable TLSv1
        ssl_context.options |= ssl.OP_NO_TLSv1_1  # disable TLSv1.1
        ssl_crt_path = config['SERVER_SSL_CRT']
        ssl_key_path = config['SERVER_SSL_KEY']
        ssl_key_pass = config['SERVER_SSL_PWD']
        # https://github.com/encode/uvicorn/issues/806
        uvicorn.run(f"{__name__}:app", host=config['SERVER_BIND'], port=config['SERVER_PORT'],
                    log_config=None, log_level=config['LOGGER_LEVEL'], access_log=False,  # We use our own logger
                    reload=config['DEBUG'],
                    ssl_certfile=ssl_crt_path, ssl_keyfile=ssl_key_path, ssl_keyfile_password=ssl_key_pass,
                    ssl_version=ssl_context.protocol, ssl_ciphers=":".join(map(lambda c: c["name"], ssl_context.get_ciphers()))  # type: ignore
                    )
    else:
        uvicorn.run(f"{__name__}:app", host=config['SERVER_BIND'], port=config['SERVER_PORT'],
                    log_config=None, log_level=config['LOGGER_LEVEL'], access_log=False,  # We use our own logger
                    reload=config['DEBUG'])


if __name__ == "__main__":
    sys.exit(main())  # type: ignore
