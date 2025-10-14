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
import ast 

from fastapi import APIRouter, Depends
from fastapi import status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select, and_
from sqlalchemy.engine import Result

from urllib.parse import unquote

from anms.components.schemas import ARIs
from anms.models.relational import get_async_session, get_session

from anms.models.relational.report import Report
from anms.models.relational.execution_set import ExecutionSet
from anms.models.relational.registered_agent import RegisteredAgent

from anms.shared.opensearch_logger import OpenSearchLogger
import io

import anms.routes.transcoder as transcoder

# for handling report set and exec set  
import ace

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
async def report_def_by_id(agent_id: int):
    # select all reports belonging to the agent
    final_res = []
    agent_id_str = ""
    dec = ace.ari_cbor.Decoder()
    enc = ace.ari_text.Encoder()
    adms = ace.AdmSet()
    adms.load_default_dirs()
    nn_func = ace.nickname.Converter(ace.nickname.Mode.FROM_NN , adms.db_session(), False)
    stmt = select(Report).where(Report.agent_id == agent_id)
    agent_id_stmt =  select(RegisteredAgent).where(RegisteredAgent.registered_agents_id == agent_id)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        # Execution set uses URI as agent_id
        result_agent: Result = await session.scalars(agent_id_stmt)
        agent_id_str = result_agent.one_or_none()
        agent_id_str = agent_id_str.agent_endpoint_uri
        for res in result.all():   
            # select from exec_set 
            try:
                nonce_cbor = res.nonce_cbor
                if(nonce_cbor != b'\xf6'): # not a null nonce
                    stmt = select(ExecutionSet).where(and_(ExecutionSet.agent_id == agent_id_str, ExecutionSet.nonce_cbor == nonce_cbor) )
                    result: Result = await session.scalars(stmt)
                    exc_set = result.all()
                    for res_exec in exc_set:
                        ari_val = ""
                        if(res_exec):
                            hex_str = res_exec.entries.hex()
                            hex_str = "0x"+hex_str.upper()
                            ari_val = await transcoder.transcoder_put_cbor_await(hex_str)
                            ari_val =  ari_val['data']
                            addition = {'exec_set': ari_val,'nonce_cbor':str(nonce_cbor)}    
                            if addition not in final_res:
                                final_res.append(addition)
                else: #null nonce use report source
                    rpt_set = res.report_list_cbor.hex()
                    # Using Ace to translate CBOR into ARI object to process individual parts  
                    in_text = '0x'+rpt_set
                    ari_rpt = None
                    try:
                        in_bytes = ace.cborutil.from_hexstr(in_text)
                        ari_rpt = dec.decode(io.BytesIO(in_bytes))
                    except Exception as err:
                        logger.error(err)

                    # running through and translating all parts of rptset
                    for rpt in ari_rpt.value.reports:
                        try:
                            enc = ace.ari_text.Encoder()
                            buf = io.StringIO()
                            enc.encode(rpt.source, buf)
                            out_text = buf.getvalue()    
                            ari_val = out_text
                            # TODO look at better way to handle storing nonce with null
                            addition = {'exec_set': ari_val,'nonce_cbor':str(nonce_cbor)}    
                            if addition not in final_res:
                                final_res.append(addition)
                        except Exception as err:
                            logger.error(err)

            except Exception as e:
                logger.error(f"Error {e}, while processing nonce:{nonce_cbor} for agent: {agent_id_str}")

    return final_res

# entries tabulated returns header and values in correct order
# handling if nonce_cbor is null
@router.get("/entries/table/{agent_id}/{nonce_cbor}", status_code=status.HTTP_200_OK)
async def report_ac(agent_id: int, nonce_cbor: str) -> dict:
    ari = None
    dec = ace.ari_cbor.Decoder()
    enc = ace.ari_text.Encoder()
    exec_set_dir = {}
    logger.info(nonce_cbor)
    logger.info(type(nonce_cbor))
    try:
        store_nonce = nonce_cbor 
        nonce_cbor = ast.literal_eval(nonce_cbor)
    except Exception as e:
        try:
            nonce_cbor = ast.literal_eval(str(bytes.fromhex(nonce_cbor)))
        except Exception as e:
            logger.error(f"{e} while processing nonce")
            return []
        
                                                        
    # process each report in the rpt set and place inside appropiate nonce case or if null use source as key
    # TODO use td off set in report set to update actual time 
    # 
    ari = None
    stmt = select(Report).where(and_(Report.agent_id == agent_id, Report.nonce_cbor == nonce_cbor) )
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        for res in result.all():
            # used to hold final report set 
            curr_time = res.reference_time
            # addition = {time:}
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
                    # for each report in a rptset 
                    # add to the top level nonce dict or to source dict if nonce is null null
                    for rpt in ari.value.reports:
                        try:
                            # structure for the reports 
                            # time: source_name:{[values of reprots ]}
                            buf = io.StringIO()
                            enc.encode(rpt.source, buf)
                            rpt_src = buf.getvalue()    
                            addition = {"time":curr_time, rpt_src:[]}
                            rpt_entries = []
                            enc = ace.ari_text.Encoder()
                            # running through and translating all parts of rptset
                            for item in rpt.items:
                                # using ace to decode the components 
                                # item = dec.decode(item)
                                if type(item.value) == ace.ari.Table:
                                    table_vals = []
                                    for tab_val in item.value:
                                        table_vals.append([t.value for t in tab_val])
                                    rpt_entries.append(table_vals)
                                else:#handle values as normal    
                                    buf = io.StringIO()
                                    enc.encode(item, buf)
                                    out_text = buf.getvalue()    
                                    rpt_entries.append(out_text)
                        
                            # placing all the values in the sources section 
                            addition[rpt_src] = rpt_entries
                            
                            if(nonce_cbor == b'\xf6' ):
                                curr_dic = exec_set_dir.get(rpt_src,[])
                                curr_dic.append(addition)  
                                exec_set_dir[rpt_src] = curr_dic 
                            else:
                                curr_dic = exec_set_dir.get(store_nonce,[])
                                curr_dic.append(addition)  
                                exec_set_dir[store_nonce] = curr_dic 
                        except Exception as err:
                            logger.error(err)            
    return exec_set_dir
    
