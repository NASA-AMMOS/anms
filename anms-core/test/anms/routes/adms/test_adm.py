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
import pytest
import json

from anms.routes.adms.adm import (getall, update_adm)
from anms.routes.adms.adm_compare import (AdmCompare)

from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger
from unittest.mock import (patch, MagicMock, AsyncMock, PropertyMock)
from anms.components.schemas.adm import NamespaceViewSchema

from fastapi import File, UploadFile, Request

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger

# Enable tracemalloc when want to trace errors
#import tracemalloc
#tracemalloc.start()


class MockAdmObj:
    def __init__(self, name, value):
        self.name = name
        self.value = value
class MockAdmFile:
    def __init__(self):
        self.namespace = MockAdmObj("namespace", "adm")
        self.version = MockAdmObj("version", "v3.1")
        self.organization = MockAdmObj("organization", "JHUAPL")
        self.mdat = [self.namespace, self.version, self.organization]

class TestAdm:
    @pytest.mark.anyio
    @patch('anms.routes.adms.adm.NamespaceView', new_callable=AsyncMock)
    async def test_getall(self, mock_namespace_view):
        '''
        This only test the flow of the getall function.
        The actual execution is not tested due to no access to database
        '''
        #This mock the getall method of Adm that is used inside the getall function
        mock_result = [
            NamespaceViewSchema(enumeration=1, data_model_name="amp", 
                name_string="amp/agent", version_name="v3.1", use_des="view result")
        ]
        mock_namespace_view.getall.return_value = mock_result
        res = await getall()
        '''
            Ideally, the res is a JSONResponse object. Yet, fastapi
            parse the result into the object only when calling using HTTP request,
            we can only test the flow of execution
        '''
        assert res == mock_result

    @pytest.mark.anyio
    @patch('anms.routes.adms.adm.NamespaceView', new_callable=AsyncMock)
    async def test_getall_empty(self, mock_adm):
        '''
        This test the result when there is no data or the function is failed
        The actual execution is not tested due to no access to database
        '''
        #This mock the getall method of Adm that is used inside the getall function
        mock_adm.getall.return_value = None

        res = await getall()
        json_body = json.loads(res.body)
        assert res.status_code == 404
        assert json_body["message"] != None

    @pytest.mark.anyio
    async def test_update_adm_fail_for_incorrect_file_type(self):
        '''
        This only test the flow of the update_adm function.
        The actual execution is not tested due to no access to database
        '''
        #set up mock arguments
        uploadfile_patcher = AsyncMock('fastapi.UploadFile', **{"content_type": "not-json-type"})
        uploadfile_mock = uploadfile_patcher.return_value
        uploadfile_mock.content_type = "not-json-type"
        request_patcher = MagicMock('fastapi.Request')
        request_mock = request_patcher.return_value

        #begin test
        res = await update_adm(uploadfile_mock, request_mock)
        json_result = json.loads(res.body)
        expect_status_code = 415
        assert res.status_code == expect_status_code
        assert json_result["message"] != None
    
        
    # @pytest.mark.anyio
    # async def test_update_adm_fail_for_incorrect_type(self):
    #     '''
    #     This only test the flow of the update_adm function.
    #     The actual execution is not tested due to no access to database
    #     '''
    #     #set up mock cursor
    #     uploadfile_patcher = AsyncMock('fastapi.UploadFile', **{"content_type": "not-json-type"})
    #     request_patcher = MagicMock('fastapi.Request')
    #     request_mock = request_patcher.return_value
    #     res = await update_adm(uploadfile_patcher, request_mock)
    #     json_result = json.loads(res.body)
    #     assert res.status_code == 400
    #     assert json_result["message"] != None
    

    

