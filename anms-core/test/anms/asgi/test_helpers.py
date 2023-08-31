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
import os
from pathlib import Path

import pytest
from starlette import datastructures

from anms.asgi.helpers import ModifiedJinja2Templates, SecretsManager
from anms.shared.config_utils import ConfigBuilder

config = ConfigBuilder.get_config()
config['MQTT_HOST'] = None


class TestModifiedJinja2Templates:

    def test_init(self):
        test_resource_path = os.path.join("test", "resources", "public")
        templates = ModifiedJinja2Templates(directory=Path(test_resource_path))
        assert templates.env.loader, \
            "The result of loading a template directory should be that the loader is initialized."
        assert test_resource_path in templates.env.loader.searchpath, \
            "The result of loading a template directory should be that the loader is initialized."


class TestSecretsManager:

    def tests_new(self):
        key = config['APP_SECRET_KEY']
        config['APP_SECRET_KEY'] = None
        default_secrets_manager = SecretsManager()
        configured_secret_key = datastructures.Secret(key)
        assert default_secrets_manager.app_secret_key != configured_secret_key
