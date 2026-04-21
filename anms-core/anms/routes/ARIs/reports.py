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

# for handling report set and exec set
import ace

import ast
import asyncio

from cachetools import LFUCache

from fastapi import APIRouter, Depends
from fastapi import status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate
from fastapi.responses import JSONResponse
from anms.shared.transmogrifier import TRANSMORGIFIER

import io

from sqlalchemy import select, and_
from sqlalchemy.engine import Result

from typing import List

from urllib.parse import unquote

from anms.components.schemas import ARIs

from anms.models.relational import get_async_session
from anms.models.relational.report import Report
from anms.models.relational.const import Const
from anms.models.relational.registered_agent import RegisteredAgent

from anms.shared.opensearch_logger import OpenSearchLogger

from datetime import datetime

logger = OpenSearchLogger(__name__, log_console=True)

router = APIRouter(tags=["REPORTS"])


# routes for ARIs
@router.get(
    "/page",
    status_code=status.HTTP_200_OK,
    response_model=Page[ARIs.RptEntryFull],
    tags=["REPORTS"],
)
async def paged_reports(params: Params = Depends()):
    async with get_async_session() as session:
        return await paginate(session, select(Report), params)


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    response_model=List[ARIs.RptEntryFull],
    tags=["REPORTS"],
)
async def all_reports():
    stmt = select(Report)
    res = []
    async with get_async_session() as session:
        result: Result = await session.scalars(stmt)
        res = result.all()
    return res


# report_source is cbor
async def _report_from_id_source(
    agent_idx: int, report_source: str, start_time: str = None, end_time: str = None
):
    res = []
    report_dict = []

    if agent_idx:
        if start_time is None:
            start_time = datetime.fromisoformat("2010-01-01T00:00:00+00:00")
        if end_time is None:
            end_time = datetime.fromisoformat("2100-01-01T00:00:00+00:00")
        start_time = start_time.replace(tzinfo=None)
        end_time = end_time.replace(tzinfo=None)

        stmt = (
            select(Report)
            .where(Report.agent_id == agent_idx)
            .where(Report.report_source == bytes.fromhex(report_source))
            .filter(Report.reference_time >= start_time)
            .filter(Report.reference_time <= end_time)
        )
        async with get_async_session() as session:
            result: Result = await session.scalars(stmt)
            res = result.all()

    if res:
        # translate report_source  if its const use its values as the forms for the final report
        report_source_ari = TRANSMORGIFIER.transcode("0x" + report_source)
        report_source_columns = [f"col {x}" for x, _ in enumerate(res[0].report_items)]
        if isinstance(report_source_ari["ari"], ace.ari.ReferenceARI):
            if report_source_ari["ari"].ident.type_id == ace.ari.StructType.CONST:
                stmt = (
                    select(Const.data_value)
                    .where(Const.name == str(report_source_ari["ari"].ident.obj_id))
                    .where(
                        Const.data_model_name
                        == str(report_source_ari["ari"].ident.model_id)
                    )
                    .where(
                        Const.namespace == str(report_source_ari["ari"].ident.org_id)
                    )
                )
                async with get_async_session() as session:
                    result: Result = await session.scalars(stmt)
                    result = result.all()
                    if result:
                        report_source_columns = []
                        for val in TRANSMORGIFIER.transcode(result[0])["ari"].value:
                            report_source_columns.append(val.ident.obj_id)
            else:
                if isinstance(report_source_ari["ari"].ident, ace.ari.LiteralARI):
                    if isinstance(report_source_ari["ari"].ident.value, list):
                        report_source_columns = []
                        for val in report_source_ari.value:
                            report_source_columns.append(val.ident.obj_id)

    # data_value
    for row in res:
        new_item = {
            "reference_time": row.reference_time,
            "mgr_time": row.mgr_time,
            "agent_time": row.agent_time,
            "rpt_set_nonce": row.nonce_cbor,
            "report_source": report_source_ari["uri"],
        }

        for index, value in enumerate(row.report_items):
            new_item[report_source_columns[index]] = value
        report_dict.append(new_item)

    return report_dict


async def _source_from_id(agent_idx: int):
    res = []
    if agent_idx:
        stmt = (
            select(Report.report_source).distinct().where(Report.agent_id == agent_idx)
        )
        async with get_async_session() as session:
            result: Result = await session.scalars(stmt)
            for x in result.all():
                res.append(
                    {
                        "ari": TRANSMORGIFIER.transcode("0x" + x.hex())["uri"],
                        "cbor": x.hex(),
                    }
                )
    return res


async def _reports_from_id(agent_idx: int):
    res = []
    if agent_idx:
        stmt = select(Report).where(Report.agent_id == agent_idx)
        async with get_async_session() as session:
            result: Result = await session.scalars(stmt)
            res = result.all()
    return res


@router.get(
    "/all/eid/{agent_eid}",
    status_code=status.HTTP_200_OK,
    response_model=List[ARIs.RptEntry],
    tags=["REPORTS"],
)
async def reports_agent_by_name(agent_eid: str):
    agent_idx = None
    agent_id_stmt = select(RegisteredAgent).where(
        RegisteredAgent.agent_endpoint_uri == unquote(agent_eid)
    )
    async with get_async_session() as session:
        # Execution set uses URI as agent_id
        result_agent: Result = await session.scalars(agent_id_stmt)
        agent_idx = result_agent.one_or_none()
        if agent_idx:
            agent_idx = agent_idx.registered_agents_id

    return await _reports_from_id(agent_idx)


@router.get(
    "/all/idx/{agent_idx}",
    status_code=status.HTTP_200_OK,
    response_model=List[ARIs.RptEntry],
    tags=["REPORTS"],
)
async def reports_agent_by_id(agent_idx: int):
    return await _reports_from_id(agent_idx)


@router.get(
    "/report_source/eid/{agent_eid}",
    status_code=status.HTTP_200_OK,
    response_model=list,
    tags=["REPORTS"],
)
async def reports_source_agent_by_name(agent_eid: str):
    agent_idx = None
    agent_id_stmt = select(RegisteredAgent).where(
        RegisteredAgent.agent_endpoint_uri == unquote(agent_eid)
    )
    async with get_async_session() as session:
        # Execution set uses URI as agent_id
        result_agent: Result = await session.scalars(agent_id_stmt)
        agent_idx = result_agent.one_or_none()
        if agent_idx:
            agent_idx = agent_idx.registered_agents_id

    reports = await _source_from_id(agent_idx)
    return reports


@router.get(
    "/report_source/idx/{agent_idx}/",
    status_code=status.HTTP_200_OK,
    response_model=list,
    tags=["REPORTS"],
)
async def reports_source_agent_by_id(agent_idx: int):
    reports = await _source_from_id(agent_idx)
    return reports


@router.get(
    "/dictionary/idx/{agent_idx}/{source_cbor}",
    status_code=status.HTTP_200_OK,
    response_model=list,
    tags=["REPORTS"],
)
async def reports_dictionary_by_id_and_report_source(agent_idx: int, source_cbor: str):
    reports = await _report_from_id_source(agent_idx, source_cbor)
    return reports


@router.get(
    "/dictionary/eid/{agent_eid}/{source_cbor}",
    status_code=status.HTTP_200_OK,
    response_model=list,
    tags=["REPORTS"],
)
async def reports_dictionary_by_name_and_report_source(
    agent_eid: str, source_cbor: str
):
    agent_idx = None
    agent_id_stmt = select(RegisteredAgent).where(
        RegisteredAgent.agent_endpoint_uri == unquote(agent_eid)
    )
    async with get_async_session() as session:
        # Execution set uses URI as agent_id
        result_agent: Result = await session.scalars(agent_id_stmt)
        agent_idx = result_agent.one_or_none()
        if agent_idx:
            agent_idx = agent_idx.registered_agents_id

    reports = await _report_from_id_source(agent_idx, source_cbor)
    return reports


# using the  known search criteria to filter the reports
@router.post(
    "/dictionary/search/idx/",
    status_code=status.HTTP_200_OK,
    response_model=list,
    tags=["REPORTS"],
)
async def reports_dictionary_by_search_idx(
    agent_idxs: list[int],
    source_cbors: list,
    start_time: datetime = None,
    end_time: datetime = None,
):
    reports = []
    for agent_idx in agent_idxs:
        rpt_cur = []
        for source_cbor in source_cbors:
            rpt_cur.append(
                await _report_from_id_source(
                    agent_idx, source_cbor, start_time, end_time
                )
            )
        reports.append({"agent": agent_idx, "reports": rpt_cur})
    return reports


@router.post(
    "/dictionary/search/eid/",
    status_code=status.HTTP_200_OK,
    response_model=list,
    tags=["REPORTS"],
)
async def reports_dictionary_by_search_eid(
    agent_eids: list[str],
    source_cbors: list,
    start_time: datetime = None,
    end_time: datetime = None,
):
    reports = []
    for agent_eid in agent_eids:
        rpt_cur = []
        agent_idx = None
        agent_id_stmt = select(RegisteredAgent).where(
            RegisteredAgent.agent_endpoint_uri == unquote(agent_eid)
        )
        async with get_async_session() as session:
            # Execution set uses URI as agent_id
            result_agent: Result = await session.scalars(agent_id_stmt)
            agent_idx = result_agent.one_or_none()
            if agent_idx:
                agent_idx = agent_idx.registered_agents_id
            for source_cbor in source_cbors:
                rpt_cur.append(
                    await _report_from_id_source(
                        agent_idx, source_cbor, start_time, end_time
                    )
                )
        reports.append({"agent": agent_eid, "reports": rpt_cur})
    return reports
