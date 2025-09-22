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

from sqlalchemy.exc import IntegrityError
from typing import List

from fastapi import Depends, APIRouter
from fastapi import status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate

from sqlalchemy import select
from sqlalchemy.engine import Result

from anms.components.schemas.agent_parameter import AgentParameterBase, AgentParameterReceivedBase
from anms.models.relational import get_async_session, get_session
from anms.models.relational.agent_parameter import AgentParameter, AgentParameterReceived
from anms.models.relational.registered_agent import RegisteredAgent
from anms.shared.agent_parameter import AGENT_PARAMETER, Command, process_command

from anms.shared.opensearch_logger import OpenSearchLogger

logger = OpenSearchLogger(__name__, log_console=True)

router = APIRouter(tags=["Agent_Parameters"])


@router.get("/definition/page", status_code=status.HTTP_200_OK, response_model=Page[AgentParameterBase])
async def paged_definition(params: Params = Depends()):
    async with get_async_session() as session:
        return await paginate(session, select(AgentParameter), params)


@router.get("/definition/all", status_code=status.HTTP_200_OK, response_model=List[AgentParameterBase])
async def all_definition():
    async with get_async_session() as session:
        result: Result = await session.scalars(select(AgentParameter))
        return result.all()


@router.post("/definition/send/", status_code=status.HTTP_200_OK)
async def send_parameter(command: Command):
    result = AGENT_PARAMETER.add_new_parameter(command)
    if result:
        return status.HTTP_200_OK
    return status.HTTP_400_BAD_REQUEST


@router.get("/received/page", status_code=status.HTTP_200_OK, response_model=Page[AgentParameterReceivedBase])
async def all_received(params: Params = Depends()):
    async with get_async_session() as session:
        return await paginate(session, select(AgentParameterReceived), params)


@router.get("/received/agent/{agent_id}", status_code=status.HTTP_200_OK,
            response_model=List[AgentParameterReceivedBase])
async def all_ARI(registered_agents_id: int):
    stmt = select(AgentParameterReceived).where(AgentParameterReceived.registered_agents_id == registered_agents_id)
    res = []

    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        res = result.all()

    if not res:
        logger.info(f"No received parameters for Agent {registered_agents_id}")

    return res


# recieve a request for agent paramatations and handle
@router.put("/send/{agent_id}/{agent_parameter_id}", status_code=status.HTTP_200_OK)
def send_parameter(agent_id: int, agent_parameter_id: int, command_parameters: dict):
    with get_session() as session:
        in_stm = AgentParameterReceived(registered_agents_id=agent_id,
                                        agent_parameter_id=agent_parameter_id,
                                        command_parameters=str(command_parameters))
        try:
            session.add(in_stm)
            session.commit()
            # getting agent_endpoint_uri
            agent_endpoint_uri = session.execute(select(RegisteredAgent.agent_endpoint_uri).where(
                RegisteredAgent.registered_agents_id == agent_id))
            agent_endpoint_uri = agent_endpoint_uri.one_or_none()[0]
            err = process_command(agent_parameter_id, command_parameters,
                            AGENT_PARAMETER.get_agent(),agent_endpoint_uri)
            if not err:
                return err
        except IntegrityError:
            session.rollback()
            logger.error(f'AgentParameterReceived Insert Error {agent_parameter_id} not know')
            return status.HTTP_400_BAD_REQUEST
    return status.HTTP_200_OK
