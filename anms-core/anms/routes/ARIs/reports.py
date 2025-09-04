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
from urllib.parse import unquote

from anms.components.schemas import ARIs
from anms.models.relational import get_async_session, get_session

from anms.models.relational.report import Report
from anms.models.relational.execution_set import ExecutionSet
from anms.shared.opensearch_logger import OpenSearchLogger
import io

import anms.routes.transcoder as transcoder

# for handling report set and exec set  
import ace
import ace.models


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
            exc_set = result.all()
            for res in exc_set:
                ari_val = ""
                if(res):
                    ari_val = await transcoder.transcoder_put_cbor_await("0x"+res.entries.hex())
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
    ari = None
    dec = ace.ari_cbor.Decoder()
    buf = io.StringIO()
    # Load in adms 
    # get command that made the report as first entry 
    stmt = select(ExecutionSet).where(and_(ExecutionSet.agent_id == agent_id, ExecutionSet.correlator_nonce == correlator_nonce) )
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        
        # there should only be one execution per agent per correlator_nonce
        # in the event that two occur pull the latest one  
        result = result.all()
        exec_set_dir = {}
        
        if result:
            result = result[-1]
            exec_set = result.entries.hex()
            # use ACE to handle report set decoding  
            in_text = '0x'+exec_set
            try:
                in_bytes = ace.cborutil.from_hexstr(in_text)
                ari = dec.decode(io.BytesIO(in_bytes))
                
            except Exception as err:
                logger.info(err)
                
    # current ARI should be  an exection set 
    if ari:
        if type(ari.value) == ace.ari.ExecutionSet: 
            try:
                enc = ace.ari_text.Encoder()
                # run through targets and their parameters to get all things parts translated 
                for targ in ari.value.targets: 
                    buf = io.StringIO()
                    exec_set_entry=["time"]
                    enc.encode(targ, buf)
                    out_text_targ = buf.getvalue()    
                    if targ is ace.LiteralARI and targ.type_id is  ace.StructType.AC:
                        for part in targ.value:
                            buf = io.StringIO()
                            enc.encode(part, buf)
                            out_text = buf.getvalue()
                            exec_set_entry.append(out_text)
                    else:
                        exec_set_entry.append(out_text_targ)
                    
                    exec_set_dir[out_text_targ] = [exec_set_entry]
                    
            except Exception as err:
                logger.info(err)
                
                    
    # final_res.append(exec_set_entry)
    ari = None
    stmt = select(Report).where(and_(Report.agent_id == agent_id, Report.correlator_nonce == correlator_nonce) )
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        for res in result.all():
            # used to hold final report set 
            addition = [res.reference_time]
            rpt_set = res.report_list_cbor.hex()
            # Using Ace to translate CBOR into ARI object to process individual parts  
            in_text = '0x'+rpt_set
            try:
                in_bytes = ace.cborutil.from_hexstr(in_text)
                ari = dec.decode(io.BytesIO(in_bytes))

            except Exception as err:
                logger.error(err)
                
            # current ARI should be  an report set 
            if ari:
                if type(ari.value) == ace.ari.ReportSet:                    
                    for rpt in ari.value.reports:
                        try:
                            enc = ace.ari_text.Encoder()
                            # running through and translating all parts of rptset
                            for item in rpt.items:
                                buf = io.StringIO()
                                enc.encode(item, buf)
                                out_text = buf.getvalue()    
                                addition.append(out_text)
                            buf = io.StringIO()
                            enc.encode(rpt.source, buf)
                            out_text = buf.getvalue()    
                            
                            exec_set_dir[out_text].append(addition)  
                        except Exception as err:
                            logger.error(err)
                
                
    
    return list(exec_set_dir.values())
    