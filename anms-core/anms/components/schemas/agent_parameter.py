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


from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator
import  json

class AgentParameterBase(BaseModel):
    agent_parameter_id: Optional[int] = None
    command_name: Optional[str] = None
    command_parameters: Optional[list] = None

    @validator("command_parameters", pre=True, each_item=True)
    def proccess_list(cls, input_str):
        new_list = str.split(input_str,',')
        return new_list

    class Config:
        orm_mode = True


class AgentParameterReceivedBase(BaseModel):
    ts: Optional[int] = None
    agent_parameter_received_id: Optional[int] = None
    manager_id: Optional[int] = None
    registered_agents_id: Optional[int] = None
    agent_parameter_id: Optional[int] = None
    command_parameters: Optional[dict] = None

    @validator("command_parameters", pre=True, each_item=True)
    def proccess_list(cls, input_str):
        new_list = json.loads(input_str)
        return new_list

    class Config:
        orm_mode = True
