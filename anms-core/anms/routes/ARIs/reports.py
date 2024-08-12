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
import re 
from datetime import datetime
import multiprocessing as mp 
import asyncio

from anms.components.schemas import ARIs
from anms.models.relational import get_async_session, get_session
from anms.models.relational.actual_object import VarActual
from anms.models.relational.ari import ARICollection, ADM, ObjMetadata
from anms.models.relational.formal_object import RptFormal, RptFormalDef, EddFormal, EddFormalDef
from anms.models.relational.report import Report
from anms.shared.opensearch_logger import OpenSearchLogger

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
            addition = {'adm':res.ADM, 'name':res.report_name}
            if addition not in final_res:
                final_res.append(addition)
    return final_res



async def find_edd_type(obj_metadata):
    stmt = select(EddFormal.obj_formal_definition_id).where(EddFormal.obj_metadata_id == obj_metadata)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        formal_id = result.one_or_none()
    
    type_id = 21
    if formal_id:
        stmt = select(EddFormalDef.data_type_id).where(EddFormalDef.obj_formal_definition_id == formal_id)
        async with get_async_session() as session:
            result: Result = await session.scalars(stmt)
            type_id = result.one_or_none()
    
    return type_id


# get data type of the varaible
async def find_var_type(obj_metadata):
    stmt = select(VarActual.data_type_id).where(VarActual.obj_metadata_id == obj_metadata)
    async with get_async_session() as session:
        result: Result =  await  session.scalars(stmt)
        data_type_id = result.one_or_none()

    return data_type_id

async def _process_report_entries(x):
    entry, ac_types_and_id = x
    # for entry in entries:
    curr_values = []
    time = datetime.fromtimestamp(int(entry.time)).strftime('%Y-%m-%d %H:%M:%S')

    string_values = list(filter(None, re.split(r",|'(.*?)'", entry.string_values))) if entry.string_values else []
    uint_values = entry.uint_values.split(',') if entry.uint_values else []
    int_values = entry.int_values.split(',') if entry.int_values else []
    real32_values = entry.real32_values.split(',') if entry.real32_values else []
    real64_values = entry.real64_values.split(',') if entry.real64_values else []
    uvast_values = entry.uvast_values.split(',') if entry.uvast_values else []
    vast_values = entry.vast_values.split(',') if entry.vast_values else []
    value_matchup = {18: string_values, 19: int_values, 20: uint_values, 21: vast_values, 22: uvast_values,
                        23: real32_values, 24: real64_values}
    curr_values.append(time)
    for type_id, obj_id in ac_types_and_id:
        # find the type of ari
        curr_type = type_id
        if value_matchup[curr_type]:
                curr_values.append(value_matchup[curr_type].pop(0))        
    if not ac_types_and_id:
        if string_values: curr_values.append(','.join(string_values))
        if uint_values: curr_values.append(','.join(uint_values))
        if int_values: curr_values.append(','.join(int_values))
        if real32_values: curr_values.append(','.join(real32_values))
        if real64_values: curr_values.append(','.join(real64_values))
        if uvast_values: curr_values.append(','.join(uvast_values))
        if vast_values: curr_values.append(','.join(vast_values))
    return curr_values
    

# entries tabulated returns header and values in correct order
@router.get("/entries/table/{agent_id}/{adm}/{report_name}", status_code=status.HTTP_200_OK,
            response_model=list)
async def report_ac(agent_id: str, adm: str, report_name: str):
    adm_name = adm.strip()
    agent_id = agent_id.strip()
    report_name = report_name.strip()

    stmt = select(ADM.namespace_id).where(ADM.adm_name == adm)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        adm_id = result.one_or_none()

    if adm_id:
        # get report template id
        stmt = select(RptFormal.obj_formal_definition_id).where(
            (RptFormal.obj_name == report_name.strip()), (RptFormal.namespace_id == adm_id))

        with get_session() as session:
            result: Result = session.scalars(stmt)
            rpt_id = result.one_or_none()


        # get AC_ID
        stmt = select(RptFormalDef.ac_id).where(RptFormalDef.obj_formal_definition_id == rpt_id)
        async with get_async_session() as session:
            result: Result = await session.scalars(stmt)
            ac_id = result.one_or_none()

        # get AC
        ac_names = ["time"]
        ac_types_and_id = []
        ac_stmt = select(ARICollection).where(ARICollection.ac_id == ac_id).order_by(ARICollection.order_num)
        async with get_async_session() as session:
            result: Result = await session.scalars(ac_stmt)
            ac_entries = result.all()
            for entry in ac_entries:
                curr_name = entry.obj_name
                if curr_name is None:
                    name_stmt = select(ObjMetadata.obj_name).where(ObjMetadata.obj_metadata_id == entry.obj_metadata_id)
                    result: Result = await session.scalars(name_stmt)
                    curr_name = result.one_or_none()

                ac_names.append(curr_name)
                curr_type = entry.data_type_id
                if curr_type == 2: 
                    curr_type = await find_edd_type(entry.obj_metadata_id)
                elif curr_type == 12:
                    curr_type = await find_var_type(entry.obj_metadata_id)
                ac_types_and_id.append((curr_type, entry.obj_metadata_id))
        
        stmt = select(Report).where(Report.agent_id == agent_id , Report.ADM == adm_name
                                                               , Report.report_name == report_name)
        # if a none formal report 
        if ac_id == None: 
            ac_names.append(report_name)
            
        final_values = []
        final_values.append(ac_names)
        async with get_async_session() as session:
            result: Result = await session.scalars(stmt)
            entries = result.all()
            args_to_use = []    
            for entry in entries:
                args_to_use.append(_process_report_entries([entry, ac_types_and_id]))
            result = await asyncio.gather(*args_to_use)
            for res in result:
                final_values.append(res)

    return  final_values

