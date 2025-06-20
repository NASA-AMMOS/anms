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
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class RptEntryBase(BaseModel):
    reference_time: Optional[str] = None
    agent_id: Optional[str] = None
    correlator_nonce: Optional[str] = None
    report_list: Optional[str] = None
    ari_rptset_id: Optional[int] = None


class RptEntryBaseInDBBase(RptEntryBase):
    class Config:
        orm_mode = True


# Additional properties to return via API
class RptEntryDict(BaseModel):
    pass


class RptEntryName(RptEntryBaseInDBBase):
    report_name: Optional[str] = None
    ADM: Optional[str] = None


# Additional properties to return via API
class RptEntry(RptEntryBaseInDBBase):
    pass
