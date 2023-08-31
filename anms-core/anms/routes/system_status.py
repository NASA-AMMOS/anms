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
import json
import docker
from pydantic import BaseModel

from anms.models.relational import  nm_url
from anms.shared.opensearch_logger import OpenSearchLogger
from anms.models.relational import get_async_session

from sqlalchemy.orm import (Query, Session, as_declarative, declared_attr,
                            scoped_session, sessionmaker)



router = APIRouter(tags=["SYS_STATUS"])
logger = OpenSearchLogger(__name__).logger


def get_containers_status():
  '''
  Returns the status of all containers in the system
  Parameters: None
  Returns:
    statuses (dict): dictionary with service's name and status
  '''
  docker_client = docker.from_env()
  api_client = docker.APIClient()
  statuses = {}
  try:
    for container in docker_client.containers.list():
      inspect_results = api_client.inspect_container(container.name)
      statuses[container.name] = inspect_results.get('State',{}).get('Health',{}).get('Status',container.status)
  except Exception(e):
    logger.error(f"Error proccessing services:{e}")  
    return {}
  
  return statuses

class Address(BaseModel):
    data: str

# GET 	/version 	Return version information
@router.get("/version", status_code=status.HTTP_200_OK)
async def sys_status_get_version():
  # We are going to want a way to piece together and validate what is sent to this endpoint (this is currently not very secure)
  url = nm_url+'/version'
  logger.info('GET request to %s', url)
  request = requests.get(url=url)
  return request.json()

# GET 	/services 	    status for all running services
@router.get("/services",status_code=status.HTTP_200_OK)
async def sys_status_get_services_status():
  statuses = get_containers_status()
  logger.debug(f"Checking all services' status: {str(statuses)}")
  return json.dumps(statuses)

# POST 	/agents 	Register a new Agent at specified eid (in body of request)
@router.post("/agents",status_code=status.HTTP_200_OK)
async def nm_register_agent(addr: Address):
  url = nm_url + "/agents"
  logger.info('POST to nm manager %s with addr %s', url, addr)
  request = requests.post(url=url, data=addr.data)
  return request.status_code

# PUT 	/agents/eid/{addr}/clear_tables 	Clear all tables for given node
@router.put("/agents/eid/{addr}/clear_tables",status_code=status.HTTP_200_OK)
async def nm_clear_tables(addr: str):
  url = nm_url + "/agents/eid/{}/clear_tables".format(addr)
  logger.info('PUT to nm manager %s with addr %s', url, addr)
  request = requests.put(url=url)
  return request.status_code
