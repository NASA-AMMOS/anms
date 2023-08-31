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
import emails

from anms.components.schemas import SMTPOptions
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger


def send_plain_text_email(subject: str, text: str, mail_to: str) -> bool:
    email_message = emails.Message(
        subject=subject,
        text=text,
        mail_from=(config['EMAIL_FROM_NAME'], config['EMAIL_FROM_EMAIL']),
        mail_to=mail_to,
    )
    email_settings = SMTPOptions.construct().dict()
    email_response = email_message.send(smtp=email_settings)
    return email_response['status_code'] in [
        250,
    ]
