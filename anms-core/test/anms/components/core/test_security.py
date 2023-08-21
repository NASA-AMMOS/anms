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
from datetime import timedelta, datetime
from unittest import mock

import pytest
from authlib.jose import JWTClaims, jwt
from fastapi import HTTPException

from anms.components.core import security
from anms.components.schemas import Token, TokenPayload
from anms.models.relational.user import User
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger


class TestGenerateAndValidateCsrfToken:

    @staticmethod
    def test_round_trip():
        signed_secret, secret = security.generate_csrf_token()
        assert signed_secret is not None
        assert secret is not None
        assert security.validate_csrf_token(signed_secret, secret) == (True, None)

    def test_bad_data(self, mocker):
        # decoding should fail when given bad data
        assert security.validate_csrf_token("BAD_SECRET_DATA", "BAD_SECRET_DATA") == (False, "Invalid CSRF Token")

        # generate a token as normal
        signed_secret, secret = security.generate_csrf_token()

        # change the key
        mocker.patch.dict(config, {'APP_SECRET_KEY': "Bad_Test_Key"})

        # decoding should fail when using a different key
        assert security.validate_csrf_token(signed_secret, secret) == (False, "Invalid CSRF Token")

    def test_expired(self, mocker):
        ...  # TODO SignatureExpired "can't set attributes of built-in/extension type 'datetime.timedelta'"
        # signed_secret, secret = security.generate_csrf_token()
        # mocker.patch('test.anms.components.core.test_security.timedelta.total_seconds', return_value=-20)
        #
        # assert security.validate_csrf_token(signed_secret, secret) == (False, "Invalid CSRF Token")

    def test_fail_secret_compare(self):
        signed_secret, secret = security.generate_csrf_token()
        assert security.validate_csrf_token(signed_secret, "BAD_SECRET") == (False, "Invalid CSRF Token")
