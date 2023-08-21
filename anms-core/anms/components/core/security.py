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
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional, Tuple, Union

from authlib.integrations.base_client import OAuthError
from authlib.integrations.starlette_client import OAuth, StarletteRemoteApp
from authlib.jose import JoseError, JsonWebToken
from authlib.oidc.core import UserInfo
from fastapi import HTTPException, status
from itsdangerous import BadData, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import Session

from anms.components import schemas
from anms.components.schemas import Token, TokenPayload
from anms.models.relational import get_async_session
from anms.models.relational.user import User
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger

# https://github.com/tiangolo/full-stack-fastapi-postgresql
# https://github.com/tiangolo/fastapi/issues/754


# Generate CSRF token, this needs to play together with the POST
# CSRF should be stored in a session, and validated upon "POST" (e.g. login action from the website)
# Inspired by https://github.com/wtforms/wtforms/blob/master/src/wtforms/csrf/session.py
def generate_csrf_token() -> Tuple[str, str]:
    # https://itsdangerous.palletsprojects.com/en/1.1.x/url_safe/
    # Lets make a timed-based CSRF signer
    s = URLSafeTimedSerializer(
        str(config['APP_SECRET_KEY']), salt="app_csrf"
    )  # note, this salt is not meant to be the same as a cryptographic salt
    # Generate new token (CSRF Secret)
    secret = secrets.token_hex(16)
    # Sign the Secret with our signer (to make it time-sensitive)
    signed_secret = s.dumps(secret)
    return signed_secret, secret


# Inspired by https://github.com/wtforms/wtforms/blob/master/src/wtforms/csrf/session.py
def validate_csrf_token(
    signed_secret: str, secret: str
) -> Tuple[bool, Optional[str]]:
    # Lets make a timed-based CSRF signer
    s = URLSafeTimedSerializer(
        str(config['APP_SECRET_KEY']), salt="app_csrf"
    )  # note, this salt is not meant to be the same as a cryptographic salt
    try:
        # Load CSRF Secret
        original_secret = s.loads(
            signed_secret, max_age=timedelta(days=1).total_seconds()
        )
    except (SignatureExpired, BadData):
        return False, "Invalid CSRF Token"  # TODO: prevent magic strings...
    # Perform CSRF Secret Comparison (Timing-Attack Safe)
    if not hmac.compare_digest(secret, original_secret):
        return False, "Invalid CSRF Token"  # TODO: prevent magic strings...
    return True, None
