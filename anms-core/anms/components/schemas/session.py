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
from typing import List, Optional

from pydantic import BaseModel, Extra


class SessionSchema(BaseModel):
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    csrf_token: Optional[str] = None
    mfa_required: Optional[bool] = False
    mfa_verified: Optional[bool] = False
    mfa_secret_retry: Optional[str] = None
    redirect_to: Optional[str] = None
    flash_success: Optional[List[str]] = []
    flash_error: Optional[List[str]] = []

    # https://pydantic-docs.helpmanual.io/usage/model_config/
    class Config:
        extra = (
            Extra.ignore
        )  # should we ignore attributes we don't know anything about to prevent session errors?
