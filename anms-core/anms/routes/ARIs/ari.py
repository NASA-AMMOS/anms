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
import asyncio
from functools import cache
from typing import List

from fastapi import Depends, APIRouter
from fastapi import status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select, and_
from sqlalchemy.engine import Result

from anms.components.schemas import ARIs
from anms.models.relational import get_async_session
from anms.models.relational.actual_parameter import ActualParameter
from anms.models.relational.ari import ARI
from anms.models.relational.formal_parameter import FormalParameter
from anms.models.relational.literal_object import LiteralObject

from anms.shared.opensearch_logger import OpenSearchLogger
from cachetools import Cache

logger = OpenSearchLogger(__name__, log_console=True)

router = APIRouter(tags=["ARIs"])

#Note: this patch is needed due to bool('False') is True
bool_convert = {"True": True, "False": False} 

# expensive to compute, generating string ari from the database values  
async def _generate_aris(ari_id):
    obj_metadata_id, obj_id, actual = ari_id.split('.')
    stmt = select(ARI).where(and_(ARI.obj_metadata_id == int(obj_metadata_id), ARI.obj_id == int(obj_id), ARI.actual == bool_convert[actual]))
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        ari = None
        try:
            ari = result.one_or_none()
        except Exception as e:
            logger.error(f"_generate_aris ERROR: obj_metadata_id: {obj_metadata_id} obj_id: {obj_id}")
            logger.error(e.args)
        if ari is not None:
            if ari.parm_id is None and ari.actual:
                display = "ari:/IANA:" + ari.data_model_name + "/" + ari.type_name + "." + ari.obj_name
                curr_ari = ari
                curr_ari.display = display
                curr_ari.param_names = []
                curr_ari.param_types = []
                return curr_ari
            else:
                if ari.actual:  # has params and an actual ari
                    a_parm_values = []
                    actual_parameter: Result = await session.scalars(
                        select(ActualParameter).where(ActualParameter.ap_spec_id == ari.parm_id))
                    actual_param = actual_parameter.all()[0]
                    formal_parameter: Result = await session.scalars(
                        select(FormalParameter).where(FormalParameter.fp_spec_id == actual_param.fp_spec_id))
                    formal_param = formal_parameter.all()[0]
                    type_names = formal_param.parm_type_name.split(",")
                    param_names = formal_param.parm_names.split(",")

                    list_of_values = {
                        "fp_values": None if actual_param.fp_values is None else actual_param.fp_values.split(","),
                        "obj_values": None if actual_param.obj_values is None else actual_param.obj_values.split(
                            ","), "STR": None if actual_param.str_values is None else actual_param.str_values.split(","),
                        "INT": None if actual_param.int_values is None else actual_param.int_values.split(","),
                        "UINT": None if actual_param.uint_values is None else actual_param.uint_values.split(","),
                        "VAST": None if actual_param.vast_values is None else actual_param.vast_values.split(","),
                        "UVAST": None if actual_param.uvast_values is None else actual_param.uvast_values.split(
                            ","),
                        "REAL32": None if actual_param.real32_values is None else actual_param.real32_values.split(
                            ","),
                        "REAL64": None if actual_param.real64_values is None else actual_param.real64_values.split(
                            ",")}

                    for i in range(0, formal_param.num_parms):
                        type_name_upper = type_names[i].upper()
                        if list_of_values["fp_values"] is not None:
                            # reference ari should not be in builder since need value from wrapping ari
                            return None
                        # check if the values is stored as a literal if so pull its actual value 
                        if list_of_values["obj_values"] is not None: 
                                lit_results: Result = await session.scalars(
                                    select(LiteralObject).where(
                                        LiteralObject.obj_actual_definition_id == int(
                                            list_of_values["obj_values"].pop())))
                                lit_results = lit_results.all()[0].data_value
                                a_parm_values.append(type_name_upper + "." + lit_results)
                        # if not just pop from values list 
                        else:
                            a_parm_values.append(type_name_upper + "." + list_of_values[type_name_upper].pop())
                            
                    results = "ari://IANA:" + ari.data_model_name + "/" + ari.type_name + "." + ari.obj_name + "(" + ' '.join(
                        str(e) for e in a_parm_values) + ")"
                    curr_ari = ari
                    curr_ari.display = results
                    curr_ari.param_names = param_names
                    curr_ari.param_types = type_names
                    return curr_ari
                else:  # has params and is formal ari
                    formal_parameter: Result = await session.scalars(
                        select(FormalParameter).where(FormalParameter.fp_spec_id == ari.parm_id))
                    curr_formal_param = formal_parameter.all()
                    parms = curr_formal_param[0].parm_type_name
                    types = parms.split(",")
                    names = curr_formal_param[0].parm_names.split(",")
                    display = "ari:/IANA:" + ari.data_model_name + "/" + ari.type_name + "." + ari.obj_name + "(" + parms + ")"
                    curr_ari = ari
                    curr_ari.display = display
                    curr_ari.param_names = names
                    curr_ari.param_types = types
                    return curr_ari
        return None

# for chaching the display names of ari
class ResourceCache(Cache):
    def __missing__(self, key):
        resource = asyncio.create_task(_generate_aris(key))
        self[key] = resource
        return resource


resource_cache = ResourceCache(maxsize=16384)


@router.get("", status_code=status.HTTP_200_OK, response_model=Page[ARIs.ARI])
async def paged_ARI(params: Params = Depends()):
    async with get_async_session() as session:
        return await paginate(session, select(ARI), params)


@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[ARIs.ARI])
async def all_ARI():
    stmt = select(ARI)
    final_result = []
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        for ari in result.all():
            display = "ari:/IANA:" + ari.data_model_name + "/" + ari.type_name + "." + ari.obj_name + "()" if ari.parm_id is None else "ari:/IANA:" + ari.data_model_name + "/" + ari.type_name + "." + ari.obj_name + "(has parameters)"
            curr_ari = ari
            curr_ari.display = display
            final_result.append(curr_ari)
        return final_result


@router.get("/all/display", status_code=status.HTTP_200_OK, response_model=List[ARIs.ARIDisplayAndParams])
async def all_ARI_display():
    ret = []
    stmt = select(ARI)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        for ari in result.all():
            if not ari.actual and ari.parm_id is None: # if is a formal ari with no parameters just need actual ari
                continue
            key = str(ari.obj_metadata_id) + "." + str(ari.obj_id) + "." + str(ari.actual)
            response = await resource_cache[key]
            if response is None:
                logger.info(f"all_ARI_display key: {key} return None value")
            else:
                ret.append(response)

    return ret


@router.get("/id/display/{obj_metadata_id}/{obj_id}", status_code=status.HTTP_200_OK,
            response_model=List[ARIs.ARIDisplayAndParams])
async def ari_display_by_id(obj_metadata_id: int, obj_id: int):
    key = str(obj_metadata_id) + "." + str(obj_id) + ".{actual}"
    res = await resource_cache[key.format(actual=True)]
    if res is None:
        res = await resource_cache[key.format(actual=False)]
    if res is None:
        logger.info(f"ari_display_by_id key: {key} has None value")
    return [res]


@router.get("/id/{obj_metadata_id}/{obj_id}", status_code=status.HTTP_200_OK, response_model=ARIs.ARI)
async def ari_by_id(obj_metadata_id: int, obj_id: int):
    stmt = select(ARI).where(and_(ARI.obj_metadata_id == obj_metadata_id, ARI.obj_id == obj_id))
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.one_or_none()


@router.get("/name/display/{obj_name}", status_code=status.HTTP_200_OK, response_model=List[ARIs.ARIDisplayAndParams])
async def ari_display_by_name(obj_name: str):
    ret = []
    stmt = select(ARI).where(ARI.obj_name == obj_name)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        for ari in result.all():
            key = str(ari.obj_metadata_id) + "." + str(ari.obj_id)
            ret.append(await resource_cache[key])
    return ret


@router.get("/name/{obj_name}", status_code=status.HTTP_200_OK, response_model=ARIs.ARI)
async def ari_by_name(obj_name: str):
    stmt = select(ARI).where(ARI.obj_name == obj_name)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.all()
