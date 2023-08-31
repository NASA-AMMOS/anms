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
import json
import posixpath
from typing import Optional, Tuple

from fastapi import Depends, Form, HTTPException, status
from fastapi.openapi.models import OAuthFlowPassword, OAuthFlows
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.ext.asyncio import AsyncSession
from pydash import arrays

from anms.components.core.security import (generate_csrf_token,
                                           validate_csrf_token)
from anms.components.injects.relational import get_async_session_inject
from anms.components.injects.session import SessionContainer
from anms.components.schemas import Token
from anms.models.relational.user import User
from anms.routes.mappings import RoutesMapper
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger


# CSRF is stored in session, and validated upon "POST" (e.g. login action from the website)
def generate_csrf_token_inject(session: SessionContainer = Depends()) -> str:
    # Get Signed-Token and Backing Secret
    token, secret = generate_csrf_token()
    # Update the session... Store CSRF in session
    session.instance.csrf_token = secret
    session.write()
    # Return time-signed token cached via Depends (stored per request context), otherwise we would have to use request.state...
    return token


# Inspired by https://github.com/wtforms/wtforms/blob/master/src/wtforms/csrf/session.py
def validate_csrf_token_form_inject(
        session: SessionContainer = Depends(),
        csrf_token: Optional[str] = Form(None, format="password"),
) -> Tuple[bool, Optional[str]]:
    # Get Session Data
    if not (csrf_token and session.instance.csrf_token):
        return False, "Invalid CSRF Token"  # TODO: prevent magic strings...
    is_success, message = validate_csrf_token(
        signed_secret=csrf_token, secret=session.instance.csrf_token
    )
    # Return something to the Depends inject function...
    # https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/#add-dependencies-to-the-path-operation-decorator
    return is_success, message


# Todo move to utils?
def identity_message_handler(
        error: Optional[str] = None, message: Optional[str] = None
) -> Optional[Tuple[Optional[str], Optional[str]]]:
    return error, message
