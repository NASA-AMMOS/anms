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

from typing import List

from fastapi import APIRouter, Depends
from fastapi import status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select, or_, String
from sqlalchemy.engine import Result

from anms.components.schemas import ARIs
from anms.models.relational import get_async_session
from anms.models.relational.registered_agent import RegisteredAgent
from anms.shared.opensearch_logger import OpenSearchLogger

logger = OpenSearchLogger(__name__, log_console=True)
router = APIRouter(tags=["ARIs"])


@router.get("", status_code=status.HTTP_200_OK, response_model=Page[ARIs.RegisteredAgent])
async def paged_registered_agents(params: Params = Depends()):
    async with get_async_session() as session:
        return await paginate(session, select(RegisteredAgent).order_by(RegisteredAgent.registered_agents_id), params)


@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[ARIs.RegisteredAgent])
async def all_registered_agents():
    stmt = select(RegisteredAgent).order_by(RegisteredAgent.registered_agents_id)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.all()


@router.get("/id/{registered_agents_id}", status_code=status.HTTP_200_OK, response_model=ARIs.RegisteredAgent)
async def registered_agent_by_id(registered_agents_id: int):
    stmt = select(RegisteredAgent).where(RegisteredAgent.registered_agents_id == registered_agents_id)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.one_or_none()


@router.get("/name/{agent_endpoint_uri}", status_code=status.HTTP_200_OK, response_model=ARIs.RegisteredAgent)
async def registered_agent_by_name(agent_endpoint_uri: str):
    stmt = select(RegisteredAgent).where(RegisteredAgent.agent_endpoint_uri == agent_endpoint_uri)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.one_or_none()


@router.get("/search/{query}", status_code=status.HTTP_200_OK, response_model=Page[ARIs.RegisteredAgent])
async def paged_registered_agents(query: str, params: Params = Depends()):
    async with get_async_session() as session:
        query = '%' + query + '%'
        return await paginate(session, select(RegisteredAgent).where(or_(
            RegisteredAgent.agent_endpoint_uri.ilike(query),
            RegisteredAgent.first_registered.cast(String).ilike(query),
            RegisteredAgent.last_registered.cast(String).ilike(query)
        )).order_by(RegisteredAgent.registered_agents_id), params)
