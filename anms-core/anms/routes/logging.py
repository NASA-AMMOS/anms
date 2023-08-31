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
from typing import Dict

from fastapi import APIRouter, Depends, status
import datetime
import logging
import pydash as _
from sqlalchemy.ext.asyncio import AsyncSession

from anms.components.injects import (get_async_session_inject)
from anms.components.schemas.logging import LoggingMessageBase, LoggingQueryModel
from anms.shared.opensearch_logger import OpenSearchLogger

router = APIRouter(tags=["Logging"])

logger = OpenSearchLogger(log_console=True)


@router.post("", status_code=status.HTTP_200_OK)
async def log(
        logging_request: LoggingMessageBase,
        session: AsyncSession = Depends(get_async_session_inject)) -> str:
    """This function allows for storing of logging messages and data to connected OpenSearch capabilities"""
    if _.objects.get(logging_request, 'datetime'):
        date_time = _.objects.get(logging_request, 'datetime')
    else:
        date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    real_date_time = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    level = logging._nameToLevel[logging_request.level]
    result = logger.log_to_opensearch(level=level, message=logging_request.message,
                                      data=_.objects.get(logging_request, 'data', None),
                                      component_name=logging_request.component,
                                      date_time=real_date_time, )
    if not result:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        return result


@router.post("/query", status_code=status.HTTP_200_OK)
async def get_logs(
        logging_query: LoggingQueryModel,
        session: AsyncSession = Depends(get_async_session_inject)) -> Dict:
    """This function allows for query of logged messages and returns results from connected OpenSearch capabilities"""
    level = logging._nameToLevel[logging_query.level]
    result = logger.get_logs(level=level, component_name=logging_query.component,
                             start_datetime=logging_query.start_datetime,
                             end_datetime=logging_query.end_datetime,
                             size=logging_query.size,
                             offset=logging_query.offset)
    if not result:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        return result
