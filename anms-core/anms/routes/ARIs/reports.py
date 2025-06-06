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
from sqlalchemy import select, and_
from sqlalchemy.engine import Result
import io
import asyncio

from anms.components.schemas import ARIs
from anms.models.relational import get_async_session, get_session

from anms.models.relational.report import Report
from anms.models.relational.execution_set import ExecutionSet
from anms.shared.opensearch_logger import OpenSearchLogger

from ace import ari_text, ari_cbor



logger = OpenSearchLogger(__name__, log_console=True)

router = APIRouter(tags=["REPORTS"])


# routes for ARIs
@router.get("/all", status_code=status.HTTP_200_OK, response_model=Page[ARIs.RptEntry], tags=["REPORTS"])
async def paged_report(params: Params = Depends()):
    async with get_async_session() as session:
        return await paginate(session, select(Report), params)


@router.get("/name/all", status_code=status.HTTP_200_OK, response_model=List[ARIs.RptEntryBaseInDBBase], tags=["REPORTS"])
async def all_report_name():
    stmt = select(Report)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.all()


@router.get("/entry/name/{agent_id}", status_code=status.HTTP_200_OK, response_model=list,
            tags=["REPORTS"])
async def report_def_by_id(agent_id: str):
    # select all reports belonging to the agent
    agent_id = agent_id.strip()
    final_res = []
    stmt = select(Report).where(Report.agent_id == agent_id)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        for res in result.all():
            # byte = res.entries

            text_dec = ari_text.Decoder()
            text_enc = ari_text.Encoder()
            cbor_dec = ari_cbor.Decoder()
            cbor_enc = ari_cbor.Encoder()
            
            logger.info(res.correlator_nonce)
            addition = {'correlator_nonce':res.correlator_nonce}
            # select from exec_set 
            stmt = select(ExecutionSet).where(and_(ExecutionSet.agent_id == agent_id, ExecutionSet.correlator_nonce == res.correlator_nonce) )
            result: Result = await session.scalars(stmt)
            res = result.one_or_none()
            # logger.info(res.entries)
            ari = cbor_dec.decode(io.BytesIO(res.entries))
            logger.info(ari)
            if addition not in final_res:
                final_res.append(addition)
    return final_res


# entries tabulated returns header and values in correct order
@router.get("/entries/table/{agent_id}/{correlator_nonce}", status_code=status.HTTP_200_OK,
            response_model=list)
async def report_ac(agent_id: str, correlator_nonce: int):
    agent_id = agent_id.strip()
    final_res = []
    # get command that made the report as first entry 
    stmt = select(ExecutionSet).where(and_(ExecutionSet.agent_id == agent_id, ExecutionSet.correlator_nonce == correlator_nonce) )
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        result = result.one_or_none()
        if result:
            exec_set = result.entries.hex()
            # translate hex to ari 
             
        

    stmt = select(Report).where(and_(Report.agent_id == agent_id, Report.correlator_nonce == correlator_nonce) )
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        for res in result.all():
            curr = res.report_list.split(';')
            curr = curr[2:]
            

            addition = [res.reference_time] 
            addition.extend(curr)
            if addition not in final_res:
                final_res.append(addition)
    return final_res
    