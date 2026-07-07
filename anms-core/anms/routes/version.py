#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 The Johns Hopkins University Applied Physics
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
from fastapi import APIRouter
from fastapi import status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

router = APIRouter(tags=["VERSION"])

class VersionInfo(BaseModel):
    # Build time version information
    build_version: str
    build_date: str
    # Git version information (runtime, if available. If this doesn't match above, user may not have rebuilt)
    git_version: str
    git_date: str



# GET 	/version 	Return version information
@router.get("/", response_model=VersionInfo, status_code=status.HTTP_200_OK)
async def anms_get_version():
    return VersionInfo(
        build_version=os.getenv("BUILD_VERSION", "unknown"),
        build_date=os.getenv("BUILD_DATE", "unknown"),

        git_version=os.getenv("GIT_VERSION", "unknown"),
        git_date=os.getenv("GIT_DATE", "unknown"),
    )
