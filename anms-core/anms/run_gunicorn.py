# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 The Johns Hopkins University Applied Physics
# Laboratory LLC.
#
# This file is part of the Asynchronous Network Managment System (ANMS).
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

import os
import secrets
import ssl
import sys
import gunicorn.app.base

from anms.shared.config import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger


config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger


# https://docs.gunicorn.org/en/stable/custom.html#custom-application
class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self):
        super().__init__()

    def load(self):
        # Import must be here in case of pre-fork model
        from anms.asgi.server import app
        return app

    def load_config(self):

        if config['SERVER_PORT'] is not None:
            bind = config['SERVER_BIND'] + ":" + str(config['SERVER_PORT'])
        else:
            bind = config['SERVER_BIND']

        self.cfg.set("bind", bind)
        self.cfg.set("workers", config['SERVER_WORKERS'] or max((os.cpu_count() or 1) - 1, 1))
        self.cfg.set("timeout", config['SERVER_TIMEOUT'])
        self.cfg.set("reload", False)  # No reload for gunicorn given the uvicorn.workers.UvicornWorker
        self.cfg.set("worker_class", "uvicorn.workers.UvicornWorker")  # https://www.uvicorn.org/deployment/
        self.cfg.set("accesslog", "-")
        self.cfg.set("errorlog", "-")
        self.cfg.set("proc_name", "anms")
        self.cfg.set("preload_app", False)

        # SSL Settings
        should_start_with_ssl = (
            config['SERVER_SSL'] is True
            and config['SERVER_BEHIND_PROXY'] is False
            and isinstance(config['SERVER_SSL_CRT'], str)
            and isinstance(config['SERVER_SSL_KEY'], str)
        )
        if should_start_with_ssl:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.options |= ssl.OP_NO_TLSv1
            ssl_context.options |= ssl.OP_NO_TLSv1_1
            self.cfg.set("ssl_version", ssl_context.protocol)
            self.cfg.set("certfile", config['SERVER_SSL_CRT'])
            self.cfg.set("keyfile", config['SERVER_SSL_KEY'])

        # App Secret Manager Help?
        if not config['APP_SECRET_KEY']:
            # Ensures all workers have the same application secret key... (this should be provided honestly)
            print("APP_SECRET_KEY IS NOT SET!!! ---> Subsequent Restart will Invalidate All Logins!!!", file=sys.stderr)
            config['APP_SECRET_KEY'] = secrets.token_urlsafe(32)

        # Register Hooks...
        def on_starting(server):
            pass

        self.cfg.set("on_starting", on_starting)


if __name__ == "__main__":
    # NOTE (for MAC users) export OBJC_DISABLE_INITIALIZE_FORK_SAFETY = YES before running this file
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
    StandaloneApplication().run()
