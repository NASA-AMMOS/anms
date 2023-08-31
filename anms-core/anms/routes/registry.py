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
from typing import Dict

from fastapi import APIRouter

from anms.routes import hello, main, network_manager, logging, transcoder, system_status, user, agent_parameter
from anms.routes.ARIs import agents, actual_objects, formal_parameter, formal_objects, \
    ari, actual_parameter, literal_object, reports, alerts
from anms.routes.adms import adm
from anms.routes.mappings import RoutesMapper
from anms.shared.manager_checker import MANAGER_CECKER


class RoutesRegistry(object):
    def __init__(self) -> None:
        self.routing_table: Dict[RoutesMapper, APIRouter] = dict()
        self.init_routing_table()

    def init_routing_table(self) -> None:
        # Setup Routing Table here...
        # Router Path Order Matters https://fastapi.tiangolo.com/tutorial/path-params/#order-matters

        # Other API Mounts
        self.routing_table[RoutesMapper.hello_api_prefix] = hello.router
        self.routing_table[RoutesMapper.agents_api_prefix] = agents.router
        self.routing_table[RoutesMapper.parameter_api_prefix] = agent_parameter.router

        self.routing_table[RoutesMapper.logging_api_prefix] = logging.router

        self.routing_table[RoutesMapper.network_manager_api_prefix] = network_manager.router
        self.routing_table[RoutesMapper.system_status_api_prefix] = system_status.router
        self.routing_table[RoutesMapper.user_api_prefix] = user.router

        self.routing_table[RoutesMapper.ari_api_prefix] = ari.router

        self.routing_table[RoutesMapper.actual_objects_api_prefix] = actual_objects.router
        self.routing_table[RoutesMapper.formal_objects_api_prefix] = formal_objects.router

        self.routing_table[RoutesMapper.actual_parameter_api_prefix] = actual_parameter.router
        self.routing_table[RoutesMapper.formal_parameter_api_prefix] = formal_parameter.router
        self.routing_table[RoutesMapper.literal_object_api_prefix] = literal_object.router
        self.routing_table[RoutesMapper.reports_api_prefix] = reports.router

        self.routing_table[RoutesMapper.transcoder_api_prefix] = transcoder.router
        self.routing_table[RoutesMapper.adm_api_prefix] = adm.router
        self.routing_table[RoutesMapper.alerts_prefix] = alerts.router

        # Root Path Mounts (match any left for last)
        self.routing_table[RoutesMapper.base_prefix] = main.router
        # TODO https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#using-the-path-operation-function-name-as-the-operationid

        # MANAGER_CECKER.test()
    @property
    def table(self) -> Dict[RoutesMapper, APIRouter]:
        return self.routing_table
