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
from anms.models.relational.adms.data_model_view import DataModel 
from anms.models.relational.formal_parameter import FormalParameter


from anms.shared.opensearch_logger import OpenSearchLogger
from cachetools import Cache

logger = OpenSearchLogger(__name__, log_console=True)

router = APIRouter(tags=["ARIs"])

#Note: this patch is needed due to bool('False') is True
bool_convert = {"True": True, "False": False} 
async def _generate_aris(ari_id):
    obj_metadata_id, obj_id, actual = ari_id.split('.')
    stmt = select(ARI).where(and_(ARI.obj_metadata_id == int(obj_metadata_id), ARI.obj_id == int(obj_id), ARI.actual == bool_convert[actual]))

    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        ari = None
        try:
            ari = result.one_or_none()
        except Exception as e:
            logger.info(f"_generate_aris ERROR: obj_metadata_id: {obj_metadata_id} obj_id: {obj_id}")
            logger.info(e)
            return None
        
        if ari is not None:
            if ari.parm_id is None and ari.actual: # has no paramterized 
                display = "ari:/" + ari.namespace + "/" + ari.data_model_name + "/" + ari.type_name + "/" + ari.name
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
                    formal_param = actual_parameter.parameters.decode('utf-8').split(",")
                    type_names = []
                    param_names = []
                    # TODO look at nested parameters 
                    for param   in formal_param.split(','):
                        param_split = param.split('/')
                        if len(param_split) > 1:
                            type_names.append('/'.join(param_split[:-1]))
                        else:
                            type_names.append('')
                        param_names.append(param_split[-1])
                    # value_set
                    a_parm_values = actual_param.value_set.decode('utf-8')
                            
                    results = "ari:/" + ari.namespace + "/"  + ari.data_model_name + "/" + ari.type_name + "/" + ari.name 
                    if a_parm_values:
                        results = results+ "(" + a_parm_values + ")"
                    curr_ari = ari
                    curr_ari.display = results
                    curr_ari.param_names = param_names
                    curr_ari.param_types = type_names
                    return curr_ari
                else:  # has params and is formal ari
                    formal_parameter: Result = await session.scalars(
                        select(FormalParameter).where(FormalParameter.fp_spec_id == ari.parm_id))
                    formal_param = formal_parameter.all()[0]
                    formal_param = formal_param.parameters.decode('utf-8')
                    type_names = []
                    param_names = []
                    # TODO look at nested parameters 
                    for param   in formal_param.split(','):
                        param_split = param.split('/')
                        if len(param_split) > 1:
                            type_names.append('/'.join(param_split[:-1]))
                        else:
                            type_names.append('')
                        param_names.append(param_split[-1])

                    display = "ari:/" + ari.namespace + "/" + ari.data_model_name + "/" + ari.type_name + "/" + ari.name + "(" + str(formal_param) + ")"
                    curr_ari = ari
                    curr_ari.display = display
                    curr_ari.param_names = param_names
                    curr_ari.param_types = type_names
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
            display = "ari:/"+ ari.namespace+ "/" + ari.data_model_name + "/" + ari.type_name + "/" + ari.name  if ari.parm_id is None else "ari:/" + ari.namespace+ ":" + ari.data_model_name + "/" + ari.type_name + "/" + ari.name + "(has parameters)"
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
                logger.warn(f"all_ARI_display key: {key} return None value")
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
        logger.warn(f"ari_display_by_id key: {key} has None value")
        return[ARIs.ARIDisplayAndParams]
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
