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
from typing import Any
from typing import Dict

from anms.models.relational import Model
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


# class for vw_ctrl_definition used for build ari
class Report(Model):
    __tablename__ = 'vw_rpt_entries'
    time = Column(Integer, nullable=False)
    agent_id = Column("Agent ID", String)
    report_name = Column("Report Name", String, nullable=False)
    ADM = Column(String, nullable=False)
    report_id = Column("Report ID", Integer, primary_key=True)
    string_values = Column("String Values", String)
    uint_values = Column("UINT Values", String)
    int_values = Column("INT Values", String)
    real32_values = Column("REAL32 Values", String)
    real64_values = Column("REAL64 Values", String)
    uvast_values = Column("UVAST Values", String)
    vast_values = Column("VAST Values", String)
    object_id_values = Column("Object ID Values", String)
    AC_id_values = Column("AC ID Values", String)
    TNVC_id_values = Column("TNVC ID Values", String)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {'vw_rpt_entries.time': getattr(self, 'time'),
                    'vw_rpt_entries.Agent ID': getattr(self, 'agent_id'),
                    'vw_rpt_entries.Report Name': getattr(self, 'report_name'),
                    'vw_rpt_entries.ADM': getattr(self, 'ADM'),
                    'vw_rpt_entries.Report ID': getattr(self, 'report_id'),
                    'vw_rpt_entries.String Values': getattr(self, 'string_values'),
                    'vw_rpt_entries.UINT Values': getattr(self, 'uint_values'),
                    'vw_rpt_entries.INT Values': getattr(self, 'int_values'),
                    'vw_rpt_entries.REAL32 Values': getattr(self, 'real32_values'),
                    'vw_rpt_entries.REAL64 Values': getattr(self, 'real64_values'),
                    'vw_rpt_entries.UVAST Values': getattr(self, 'uvast_values'),
                    'vw_rpt_entries.VAST Values': getattr(self, 'vast_values'),
                    'vw_rpt_entries.Object ID Values': getattr(self, 'object_id_values'),
                    'vw_rpt_entries.AC ID Values': getattr(self, 'AC_id_values'),
                    'vw_rpt_entries.TNVC ID Values': getattr(self, 'TNVC_id_values'),
                    }

        return dict_obj
