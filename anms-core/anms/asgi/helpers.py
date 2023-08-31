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
import secrets
import shelve
from pathlib import Path
from typing import Optional

from fastapi.templating import Jinja2Templates
from starlette import datastructures

from anms.shared.config_utils import ConfigBuilder

config = ConfigBuilder.get_config()


class ModifiedJinja2Templates(Jinja2Templates):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for attr, attr_val in dict(block_start_string="<%", block_end_string="%>",
                                   variable_start_string="<$", variable_end_string="$>",
                                   comment_start_string="<#", comment_end_string="#>").items():
            setattr(self.env, attr, attr_val)


class SecretsManager(object):
    app_secret_key: Optional[datastructures.Secret] = None

    def __new__(cls, *args, **kwargs):
        cls.initialize_app_secret_key()
        return super().__new__(cls)

    @classmethod
    def initialize_app_secret_key(cls) -> datastructures.Secret:
        if isinstance(cls.app_secret_key, datastructures.Secret):
            return cls.app_secret_key
        if isinstance(config['APP_SECRET_KEY'], str):
            secret_key = datastructures.Secret(config['APP_SECRET_KEY'])
            config['APP_SECRET_KEY'] = secret_key
            cls.app_secret_key = secret_key
            return cls.app_secret_key
        # else... create one...
        secret_key = secrets.token_urlsafe(32)
        secret_key_wrapped = datastructures.Secret(secret_key)
        print(f"dir: {config['BASE_DATA_DIR']}")
        secret_disk_path = os.path.join(config['BASE_DATA_DIR'], ".secret")
        with shelve.open(secret_disk_path, flag="c") as db:
            if "secret" in db:
                secret_key_wrapped = db["secret"]
            else:
                db["secret"] = secret_key_wrapped
        # Update Configuration
        cls.app_secret_key = secret_key_wrapped
        config['APP_SECRET_KEY'] = secret_key_wrapped
        # Try to fix the permissions
        try:
            Path(secret_disk_path).chmod(mode=0o640)
        except OSError:
            pass
        return cls.app_secret_key
