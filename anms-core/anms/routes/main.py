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
from urllib.parse import urlparse

from fastapi import APIRouter, status
from fastapi.params import Depends
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from anms.asgi.helpers import ModifiedJinja2Templates
from anms.components.injects import SessionContainer
from anms.components.schemas import AppMainTemplate
from anms.models.relational import get_async_session
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger

# TODO Eventually: https://github.com/tiangolo/fastapi/issues/1650
router = APIRouter()

templates = ModifiedJinja2Templates(directory=config['APP_TEMPLATES_DIR'])
