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
from fastapi import APIRouter, status
import requests
from pydantic import BaseModel

from anms.models.relational import nm_url
from anms.shared.opensearch_logger import OpenSearchLogger
from urllib.parse import quote


class Data(BaseModel):
    data: str


router = APIRouter(tags=["NM"])
logger = OpenSearchLogger(__name__, log_console=True)

def _prepare_url(ari):
    ari = ari.strip()
    ari = quote(ari)
    return ari

# GET 	/version 	Return version information
@router.get("/version", status_code=status.HTTP_200_OK)
async def nm_get_version():
    # We are going to want a way to piece together and validate what is sent to this endpoint (this is currently not very secure)
    url = nm_url + '/version'
    logger.info('GET request to %s' % url)
    try:
        request = requests.get(url=url)
    except Exception:
        return {}
    return request.json()


# GET 	/agents 	Get a listing of registered agents
@router.get("/agents", status_code=status.HTTP_200_OK)
def nm_get_agents():
    url = nm_url + '/agents'
    logger.info('Get request to %s' % url)
    try:
        request = requests.get(url=url)
    except Exception:
        return -1
    return request.json()


# POST 	/agents 	Register a new Agent at specified eid (in body of request)
@router.post("/agents", status_code=status.HTTP_200_OK)
async def nm_register_agent(addr: Data):
    url = nm_url + "/agents"
    logger.info('POST to nm manager %s with addr %s' % (url, addr.data))
    try:
        request = requests.post(url=url, data=addr.data, headers={'Content-Type': 'text/plain'} )
    except Exception as e:
        logger.info(e)
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return request.status_code


# PUT 	/agents/idx/{idx}/hex 	Body is CBOR-encoded HEX ARI to send. $idx is index of node from agents listing
@router.put("/agents/idx/{idx}/hex", status_code=status.HTTP_200_OK)
async def nm_put_hex_idx(idx: str, ari: Data):
    url = nm_url + "/agents/idx/{}/send?form=hex".format(idx)
    logger.info('post to nm manager %s  with idx %s and data %s' % (url, idx, ari.data))
    try:
        request = requests.post(url=url, data=ari.data, headers={'Content-Type': 'text/plain'})
    except Exception:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return request.status_code


# PUT 	/agents/eid/{eid}/hex 	Body is CBOR-encoded HEX ARI to send. $eid is the agent to query
@router.put("/agents/eid/{eid}/hex", status_code=status.HTTP_200_OK)
def nm_put_hex_eid(eid: str, ari: Data):
    url = nm_url + "/agents/eid/{}/send?form=hex".format(_prepare_url(eid))
    logger.info('post to nm manager %s  with eid %s and data %s' % (url, eid, ari.data))
    try:        
        request = requests.post(url=url, data=ari.data, headers={'Content-Type': 'text/plain'})
    except Exception:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return request.status_code


# PUT 	/agents/eid/{addr}/clear_reports 	Clear all reports for given node
@router.put("/agents/eid/{addr}/clear_reports", status_code=status.HTTP_200_OK)
async def nm_clear_reports(addr: str):
    url = nm_url + "/agents/eid/{}/clear_reports".format(_prepare_url(addr))
    logger.info('PUT to nm manager %s with addr %s' % (url, addr))
    try:
        request = requests.put(url=url)
    except Exception:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return request.status_code


# PUT 	/agents/eid/{addr}/clear_tables 	Clear all tables for given node
@router.put("/agents/eid/{addr}/clear_tables", status_code=status.HTTP_200_OK)
async def nm_clear_tables(addr: str):
    url = nm_url + "/agents/eid/{}/clear_tables".format(_prepare_url(addr))
    logger.info('PUT to nm manager %s with addr %s' % (url, addr))
    try:
        request = requests.put(url=url)
    except Exception:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return request.status_code


# GET 	/agents/eid/{addr}/reports/hex 	Retrieve list of reports for node in HEX CBOR format
@router.get("/agents/eid/{addr}/reports/hex", status_code=status.HTTP_200_OK)
async def nm_get_reports_hex(addr: str):
    url = nm_url + "/agents/eid/{}/reports/hex".format(_prepare_url(addr))
    logger.info('Get to nm manger %s with addr %s' % (url, addr))
    try:
        request = requests.get(url=url)
    except Exception:
        return {}
    return request.json()


# GET 	/agents/eid/{addr}/reports
# Retrieve list of reports for node. Currently in HEX CBOR format, but may change in future
@router.get("/agents/eid/{addr}/reports", status_code=status.HTTP_200_OK)
async def nm_get_reports(addr: str):
    url = nm_url + "/agents/eid/{}/reports".format(_prepare_url(addr))
    logger.info('GET to nm manager %s with addr %s' % (url, addr))
    try:
        request = requests.get(url=url)
    except Exception:
        return {}
    return request.json()


# GET 	/agents/eid/{addr}/reports/text 	Retrieve list of reports for node in ASCII/text format
@router.get("/agents/eid/{addr}/reports/text", status_code=status.HTTP_200_OK)
async def nm_get_reports_text(addr: str):
    url = nm_url + "/agents/eid/{}/reports/text".format(_prepare_url(addr))
    logger.info('GET to nm manager %s with addr %s' % (url, addr))
    try:
        request = requests.get(url=url)
    except Exception:
        return {}
    return request.json()


# GET 	/agents/eid/{addr}/reports/json 	Retrieve list of reports for node in JSON format
@router.get("/agents/eid/{addr}/reports/json", status_code=status.HTTP_200_OK)
async def nm_get_reports_json(addr: str):
    url = nm_url + "/agents/eid/{}/reports/json".format(_prepare_url(addr))
    logger.info('GET to nm manager %s with addr %s' % (url, addr))
    try:
        request = requests.get(url=url)
    except Exception:
        return {}
    return request.json()


# GET 	/agents/eid/{addr}/reports/debug
# etrieve all reports for node. Debug information and/or multiple formats may be returned.
@router.get("/agents/eid/{addr}/reports/debug", status_code=status.HTTP_200_OK)
async def nm_get_reports_debug(addr: str):
    url = nm_url + "/agents/eid/{}/reports/debug".format(_prepare_url(addr))
    logger.info('GET to nm manager %s with addr %s' % (url, addr))
    try:
        request = requests.get(url=url)
    except Exception:
        return {}
    return request.json()


# GET 	/agents/{addr} 	Retrieve node information, including name and # reports available
@router.get("/agents/{addr}", status_code=status.HTTP_200_OK)
async def nm_get_agents_info(addr: str):
    url = nm_url + "/agents/{}".format(_prepare_url(addr))
    logger.info('GET to nm manager %s with addr %s' % (url, addr))
    try:
        request = requests.get(url=url)
    except Exception:
        return {}
    return request.json()


# PUT 	/agents/eid/{addr}/reports/clear 	Clear all cached reports
@router.put("/agents/eid/{addr}/reports/clear", status_code=status.HTTP_200_OK)
async def nm_put_clear_reports(addr: str):
    url = nm_url + "/agents/eid/{}/reports/clear".format(_prepare_url(addr))
    logger.info('PUT to nm manager %s with addr %s' % (url, addr))
    try:
        request = requests.put(url=url)
    except Exception:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return request.status_code


