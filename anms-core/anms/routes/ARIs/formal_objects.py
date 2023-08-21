#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 The Johns Hopkins University Applied Physics
# Laboratory LLC.
#
# This file is part of the Asynchronous Network Managment System (ANMS).
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
from sqlalchemy import select
from sqlalchemy.engine import Result

from anms.components.schemas import ARIs
from anms.models.relational import get_async_session
from anms.models.relational.formal_object import FormalObject, Control, EddFormal, MacFormal, RptFormal

from anms.shared.opensearch_logger import OpenSearchLogger

logger = OpenSearchLogger(__name__, log_console=True)

router = APIRouter(tags=["ARIs"])

# routes for ARIs
@router.get("", status_code=status.HTTP_200_OK, response_model=Page[ARIs.FormalObject], tags=["FORMAL"])
async def paged_formal_object(params: Params = Depends()):
    async with get_async_session() as session:
        return await paginate(session, select(FormalObject), params)


@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[ARIs.FormalObject], tags=["FORMAL"])
async def all_formal_object():
    stmt = select(FormalObject)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.all()


@router.get("/id/{obj_metadata_id}", status_code=status.HTTP_200_OK, response_model=ARIs.FormalObject, tags=["FORMAL"])
async def formal_object_by_id(obj_metadata_id: int):
    stmt = select(FormalObject).where(FormalObject.obj_metadata_id == obj_metadata_id)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.one_or_none()


@router.get("/name/{obj_name}", status_code=status.HTTP_200_OK, response_model=ARIs.FormalObject, tags=["FORMAL"])
async def formal_object_by_name(obj_name: str):
    stmt = select(FormalObject).where(FormalObject.obj_name == obj_name)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.one_or_none()


####
# Edd defs
####
@router.get("/edd/all", status_code=status.HTTP_200_OK, response_model=List[ARIs.EddFormal], tags=["FORMAL"])
async def all_edd_formal():
    stmt = select(EddFormal)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.all()


@router.get("/edd/id/{obj_metadata_id}", status_code=status.HTTP_200_OK, response_model=ARIs.EddFormal, tags=["FORMAL"])
async def edd_formal_by_id(obj_metadata_id: int):
    stmt = select(EddFormal).where(EddFormal.obj_metadata_id == obj_metadata_id)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.one_or_none()


####
# mac defs
####
@router.get("/mac/all", status_code=status.HTTP_200_OK, response_model=ARIs.MacFormal, tags=["FORMAL"])
async def mac_formal():
    stmt = select(MacFormal)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.all()

@router.get("/mac/id/{obj_metadata_id}", status_code=status.HTTP_200_OK, response_model=ARIs.MacFormal, tags=["FORMAL"])
async def mac_formal_by_id(obj_metadata_id: int):
    stmt = select(MacFormal).where(MacFormal.obj_metadata_id == obj_metadata_id)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.one_or_none()


####
# rptt defs
####
@router.get("/rptt/all", status_code=status.HTTP_200_OK, response_model=List[ARIs.RptFormal], tags=["FORMAL"])
async def all_rpt_formal():
    stmt = select(RptFormal)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.all()


@router.get("/rptt/id/{obj_metadata_id}", status_code=status.HTTP_200_OK, response_model=ARIs.RptFormal,
            tags=["FORMAL"])
async def rpt_formal_by_id(obj_metadata_id: int):
    stmt = select(RptFormal).where(RptFormal.obj_metadata_id == obj_metadata_id)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.one_or_none()


####
# CTRL defs
####
@router.get("/ctrl/all", status_code=status.HTTP_200_OK, response_model=List[ARIs.Control], tags=["FORMAL"])
async def all_control():
    stmt = select(Control)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.all()


@router.get("/ctrl/id/{obj_metadata_id}", status_code=status.HTTP_200_OK, response_model=ARIs.Control, tags=["FORMAL"])
async def control_by_id(obj_metadata_id: int):
    stmt = select(Control).where(Control.obj_metadata_id == obj_metadata_id)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.one_or_none()

# returns num_parms and name from obj_id
@router.get("/ctrl/name/id/{obj_metadata_id}", status_code=status.HTTP_200_OK, response_model=List[ARIs.ControlNameId], tags=["FORMAL"])
async def name_id_control(obj_metadata_id: int):
    stmt = select(Control).where(Control.obj_metadata_id == obj_metadata_id)
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        return result.all()



