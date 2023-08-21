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
from typing import Any
from typing import Dict

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from anms.models.relational import Model


class RegisteredAgent(Model):
    __tablename__ = 'registered_agents'

    registered_agents_id = Column(Integer, primary_key=True)
    agent_id_string = Column(
        String(128),
        default='ipn:0.0',
        unique=True,
        nullable=False)
    first_registered = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_registered = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        dict_obj["first_registered"] = str(dict_obj["first_registered"])
        dict_obj["last_registered"] = str(dict_obj["last_registered"])

        return dict_obj
