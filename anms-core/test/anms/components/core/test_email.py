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
from typing import Tuple, Dict
from unittest.mock import patch

import pytest
import mock
import emails

from anms.components.core import email
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger


class MockEmailsMessage:

    def __init__(self, subject: str = None, text: str = None, mail_from: Tuple[str, str] = (None, None),
                 mail_to: str = None):
        self.subject = subject
        self.text = text
        self.mail_from = mail_from
        self.mail_to = mail_to

    def send(self, smtp: Dict = {}) -> Dict:
        response = {}
        if self.subject and self.text and self.mail_from[0] and self.mail_from[1] and self.mail_to and \
                '@' in self.mail_from[1] and '@' in self.mail_to:
            response['status_code'] = 250
        else:
            response['status_code'] = None
        return response


class TestEmail:

    @staticmethod
    def test_send_plain_text_email(mocker):
        import emails
        emails.Message = MockEmailsMessage
        test_var = "test"
        config['EMAIL_FROM_NAME'] = test_var
        config['EMAIL_FROM_EMAIL'] = test_var
        result = email.send_plain_text_email(subject=test_var, text=test_var, mail_to=test_var)
        assert not result, ("The default response for the mocked email send function should be False because the "
                            "configuration is incorrect.")
        config['EMAIL_FROM_NAME'] = "Test"
        config['EMAIL_FROM_EMAIL'] = "test@example.com"
        result = email.send_plain_text_email(subject=test_var, text=test_var, mail_to="Chancellor.Pascale@jhuapl.edu")
        assert result, ("The default response for the mocked email send function with valid to/from emails should be "
                        "False because the configuration is incorrect.")
