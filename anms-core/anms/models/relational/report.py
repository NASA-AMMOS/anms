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

from anms.shared.transmogrifier import TRANSMORGIFIER
from anms.models.relational import Model
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import ARRAY
from sqlalchemy import LargeBinary
from sqlalchemy import orm

# class for vw_ctrl_definition used for build ari
class Report(Model):
    __tablename__ = 'vw_ari_rpt_set'
    ari_rptset_id	= Column(Integer, primary_key=True)
    mgr_time	    = Column(DateTime)
    reference_time	= Column(DateTime)
    nonce_cbor	    = Column(LargeBinary)
    agent_id	    = Column(Integer)
    ari_rptset_cbor	= Column(LargeBinary)
    ari_rptlist_id	= Column(Integer)
    time_offset	    = Column(LargeBinary)
    report_source	= Column(LargeBinary)
    report_items	= Column(ARRAY(LargeBinary) )#bytea[] NULL	

    # processing the raw cbor into an ari object
    @orm.reconstructor
    def init_on_load(self):
        self.nonce_cbor =  TRANSMORGIFIER.transcode("0x"+getattr(self, 'nonce_cbor').hex())['uri']        
        self.time_offset =  TRANSMORGIFIER.transcode("0x"+getattr(self, 'time_offset').hex())['uri']        
        self.report_source =  TRANSMORGIFIER.transcode("0x"+getattr(self, 'report_source').hex())['uri']
        self.report_items =  [TRANSMORGIFIER.transcode("0x"+x.hex())['uri'] for x in getattr(self, 'report_items')]

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
                    'ari_rptset_id': getattr(self, 'ari_rptset_id'),
                    'reference_time': getattr(self, 'reference_time'),
                    'nonce_cbor': getattr(self, 'nonce_cbor'),
                    'agent_id': getattr(self, 'agent_id'),       
                    'ari_rptlist_id': getattr(self, 'ari_rptlist_id'),
                    'report_source': getattr(self, 'report_source'),
                    'report_items': getattr(self, 'report_items')
                    }
        return dict_obj
