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
from typing import Any
from typing import Dict

from anms.models.relational import Model
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import LargeBinary


# class for vw_ctrl_definition used for build ari
class ExecutionSet(Model):
    __tablename__ = 'vw_execution_set'
    execution_set_id = Column(Integer, primary_key=True)
    correlator_nonce = Column(Integer)
    use_desc = Column(String)
    agent_id = Column(String)
    num_entries = Column(Integer)
    entries	 = Column(LargeBinary)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
                    'execution_set_id': getattr(self, 'execution_set_id'),
                    'correlator_nonce': getattr(self, 'correlator_nonce'),        
                    'use_desc': getattr(self, 'use_desc'),
                    'agent_id': getattr(self, 'agent_id'),
                    'num_entries': getattr(self, 'num_entries'),
                    'entries': getattr(self, 'entries')       
                    }

        return dict_obj
