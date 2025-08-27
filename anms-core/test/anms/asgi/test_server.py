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
from unittest.mock import patch

import uvicorn

from anms.asgi import server
from anms.shared.config_utils import ConfigBuilder

config = ConfigBuilder.get_config()


class TestMain:

    def test_main(self):
        config['SERVER_SSL'] = False
        with patch.object(uvicorn, 'run') as mock_run:
            server.main()
        mock_run.assert_called_once()
        config['SERVER_SSL'] = True
        config['SERVER_BEHIND_PROXY'] = False
        config['SERVER_SSL_CRT'] = "test"
        config['SERVER_SSL_KEY'] = "test"
        config['DEBUG'] = False
        with patch.object(uvicorn, 'run') as mock_ssl_run:
            server.main()
            mock_ssl_run.assert_called_once_with('anms.asgi.server:app', access_log=False, host="0.0.0.0", log_config=None,
                                             log_level=10, port=5555, reload=False)
        