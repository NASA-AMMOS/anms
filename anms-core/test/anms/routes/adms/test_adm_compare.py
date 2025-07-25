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

import os
import ace
from anms.routes.adms.adm_compare import (AdmCompare)
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger

# Enable tracemalloc when want to trace errors
#import tracemalloc
#tracemalloc.start()

#: Directory containing this file
SELFDIR = os.path.dirname(__file__)
TESTDIR = os.path.join(SELFDIR, "test_data")

class TestAdmCompare:

    def setup_method(self, method):
        self._admset = ace.AdmSet(cache_dir=False)

    def _load_adm(self, filename):
        file_path = os.path.join(TESTDIR, filename)
        adm_new = self._admset.load_from_file(file_path, del_dupe=False)
        assert adm_new.id
        return adm_new

    def test_equal(self):
        comp = AdmCompare(self._admset)
        self._load_adm('ietf-amm.yang')
        adm1 = self._load_adm('example-adm-minimal.yang')
        adm2 = self._load_adm('example-adm-minimal.yang')
        assert comp.compare_adms(adm1, adm2)
        assert [] == comp.get_errors()

    def compare_error(self, errorA, errorB):
        keys = ['obj_type', 'name', 'issue']
        equivalent = True
        for key in keys:
            equivalent = equivalent and (errorA.get(key,None) == errorB.get(key,None))
        return equivalent

    def test_different(self):
        comp = AdmCompare(self._admset)
        self._load_adm('ietf-amm.yang')
        adm1 = self._load_adm('example-adm-minimal.yang')
        adm2 = self._load_adm('example-adm-minimal-modified.yang')
        assert not comp.compare_adms(adm1, adm2)
        expect_errors = [
            {'obj_type': 'Edd',
            'name': 'edd1',
            'issue': "changed typeobj value from TypeUse(type_text='/ARITYPE/int', type_ari=LiteralARI(value=<StructType.INT: 4>, type_id=<StructType.ARITYPE: 16>), base=None, units=None, constraints=[]) to TypeUse(type_text='/ARITYPE/real32', type_ari=LiteralARI(value=<StructType.REAL32: 8>, type_id=<StructType.ARITYPE: 16>), base=None, units=None, constraints=[])"
            }
        ]
        
        for actual_error in comp.get_errors():
            has_equivalent_error = False
            for expect_error in expect_errors:
                if self.compare_error(actual_error, expect_error):
                    has_equivalent_error = True
                    break
            assert has_equivalent_error
            assert actual_error['issue'] == expect_error['issue']

    

