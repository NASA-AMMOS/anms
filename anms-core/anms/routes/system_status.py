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
import socket
import subprocess
from pydantic import BaseModel

from anms.models.relational import nm_url
from anms.shared.opensearch_logger import OpenSearchLogger


router = APIRouter(tags=["SYS_STATUS"])
logger = OpenSearchLogger(__name__).logger

# status_cfg configures how service status is queried.
#  Status will be queried from the first configured method of: url, tcp_port, ping
#  If no other options defined, a simple ping of the hostname will be used.
# TODO: Move status_cfg to a discrete config (ie: JSON) file to load at startup
# Format:
#  name - Name of service. This must match configured services in UI display
#  hostname - Optional hostname of service. If omitted, assumed to match name
#  url - If defined, perform a GET of this URL and report success if no error is returned (HTTP 200)
status_cfg = [
  {"name": "adminer", "url": "http://adminer:8080"},
  {"name": "anms-core"}, # Self
  {"name": "anms-ui", "url": "http://anms-ui:9030"},
  {"name": "aricodec"},
  {"name": "authnz", "url": "http://authnz/authn/login.html"},
  {"name": "grafana", "url": "http://grafana:3000"},
  {"name": "grafana-image-renderer", "url": "http://grafana-image-renderer:8081"},
  {"name": "amp-manager", "url": "http://amp-manager:8089/nm/api/version"},
  {"name": "mqtt-broker"},
  {"name": "postgres", "tcp_port": 5432},
  {"name": "redis"},
  {"name": "transcoder"}
]


def get_containers_status():
  '''
  Returns the status of all configured components
  Parameters: None
  Returns:
    statuses (dict): dictionary with service's name and status
  '''
  statuses = {}

  for container in status_cfg:
    name = container['name']

    # Default hostname to container.name if not explicitly defined
    hostname = container.get("hostname", name)
    timeout = 5  # seconds

    if "url" in container:
      url = container['url']
      try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
          statuses[name] = "healthy"
        else:
          logger.warning("%s: URL %s responded with status %d", name, url, response.status_code)
          statuses[name] = "unhealthy"
      except requests.RequestException as err:
        logger.warning("%s: URL %s failed to reach with error %s", name, url, err)
        statuses[name] = "not-running"

    elif "tcp_port" in container:
      port = container['tcp_port']
      try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
          sock.settimeout(timeout)
          result = sock.connect_ex((hostname, port))
          if result == 0:
            statuses[name] = "healthy"
          else:
            logger.warning("%s: TCP port %s:%d is closed or unreachable", name, hostname, port)
            statuses[name] = "unhealthy"
      except Exception as err:
        logger.warning("%s: TCP port %s:%d can't be queried: {err}", name, hostname, port, err)
        statuses[name] = "not-running"

    else:
      # If no other check defined, test that host can be pinged
      try:
        cmd = ["ping", "-c1", f"-W{timeout}", hostname]
        result = subprocess.run(cmd, shell=False)
        if result.returncode == 0:
          statuses[name] = "healthy"
        else:
          logger.warning("%s: Host %s is unreachable via ping, exit code %d", name, hostname, result.returncode)
          statuses[name] = "unhealthy"
      except Exception as err:
        logger.warning("%s: Error pinging %s: %s", name, hostname, err)
        statuses[name] = "not-running"
        
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
