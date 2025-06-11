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
import re
from fastapi import APIRouter, Depends
from fastapi import status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select, and_
from sqlalchemy.engine import Result
from io import StringIO

from anms.components.schemas import ARIs
from anms.models.relational import get_async_session, get_session

from anms.models.relational.report import Report
from anms.models.relational.execution_set import ExecutionSet
from anms.shared.opensearch_logger import OpenSearchLogger


import anms.routes.transcoder as transcoder


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
            # select from exec_set 
            correlator_nonce = res.correlator_nonce
            stmt = select(ExecutionSet).where(and_(ExecutionSet.agent_id == agent_id, ExecutionSet.correlator_nonce == correlator_nonce) )
            result: Result = await session.scalars(stmt)
            res = result.one_or_none()
            ari_val = ""
            if(res):
                ari_val = await transcoder.transcoder_put_cbor_await("ari:0x"+res.entries.hex())
                ari_val =  ari_val['data']   

        
            addition = {'exec_set': ari_val,'correlator_nonce':correlator_nonce}
    
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
        exec_set_entry=["time"]
        if result:
            exec_set = result.entries.hex()
            exec_set = await transcoder.transcoder_put_cbor_await("ari:0x"+exec_set)
            exec_set =  exec_set['data']  
            # format 
            # TODO HANDLE RPTT and split up multiple entries 
            "ari:/EXECSET/n=12345;(//ietf/dtnma-agent/CTRL/inspect(//ietf/dtnma-agent/EDD/sw-version))"
            execset_pattern = r"ari:/EXECSET/n=.+;\((.*)\)"
            match = re.match(execset_pattern,exec_set)
            if match:
                exec_set_entry.extend(match.group(1).split(';'))
            else:
                exec_set_entry.extend([exec_set])
        final_res.append(exec_set_entry)

    stmt = select(Report).where(and_(Report.agent_id == agent_id, Report.correlator_nonce == correlator_nonce) )
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        for res in result.all():
            # translate the cbor
            logger.info(res)
            rpt_set = res.report_list_cbor.hex()
            rpt_set = await transcoder.transcoder_put_cbor_await("ari:0x"+rpt_set)
            rpt_set =  rpt_set['data']   
            logger.info(rpt_set)

            # match 
            # ari:/RPTSET/n=12345;r=/TP/20250611T114420.009992304Z;(t=/TD/PT0S;s=//1/1/CTRL/5(//1/1/EDD/1);(%220.0…
            rptset_pattern = r"ari:/RPTSET/n=.+;r=.*;\(t=.*;s=.*;\((.*)\)\)"
            match = re.match(rptset_pattern,rpt_set)
            addition = [res.reference_time] 
            if match:
                # report entries 
                rpt_entr = match.group(1)
                addition.extend(rpt_entr.split(";"))
            else:
                addition.append(rpt_set)
            
            if addition not in final_res:
                final_res.append(addition)
    return final_res
    