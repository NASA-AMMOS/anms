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
from fastapi import APIRouter, status

from anms.shared.opensearch_logger import OpenSearchLogger
from anms.shared.manager_checker import MANAGER_CECKER

router = APIRouter(tags=["alerts"])
logger = OpenSearchLogger(__name__, log_console=True)


@router.get("/incoming", status_code=status.HTTP_200_OK)
def alerts_get():
    MANAGER_CECKER.check_list()
    alerts = MANAGER_CECKER.alerts
    return list(alerts.values())


@router.put("/acknowledge/{index}", status_code=status.HTTP_200_OK)
def alerts_get(index: int):
    MANAGER_CECKER.acknowledge(index)
    return status.HTTP_200_OK