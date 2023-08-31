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
from typing import Any, Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request
from fastapi.responses import Response
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import ASGIApp
from starlette_early_data import EarlyDataMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from anms.asgi.helpers import SecretsManager
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(log_console=True)


class MiddlewareManager(object):

    def __init__(self, app: FastAPI):
        self.app = app

    def init_middleware(self) -> None:
        for key, val in self.__class__.__dict__.items():  # type: (str, Any)
            if not key.startswith("middleware"):
                continue
            fun = getattr(self, key, None)  # type: Callable
            if not callable(fun):
                continue
            fun()

    def middleware_session(self) -> bool:
        logger.debug("Enabling Session Middleware")
        self.app.add_middleware(SessionMiddleware,
                                secret_key=SecretsManager.app_secret_key,
                                session_cookie=config['APP_SESSION_COOKIE_NAME'],
                                max_age=config['APP_SESSION_COOKIE_LIFETIME'],
                                same_site=config['APP_SESSION_COOKIE_SAMESITE'],
                                https_only=config['APP_SESSION_COOKIE_SECURE']
                                )
        return True

    def middleware_https_redirect(self) -> bool:
        if not config['SERVER_SSL']:
            return False
        logger.debug("Enabling HTTPS Redirect Middleware")
        self.app.add_middleware(HTTPSRedirectMiddleware)
        return True

    def middleware_trusted_host(self) -> bool:
        logger.debug("Enabling Trust Host Middleware")
        self.app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"], www_redirect=False)
        return True

    def middleware_trust_proxy(self) -> bool:
        if not config['SERVER_BEHIND_PROXY']:
            return False
        logger.debug("Enabling Trust Proxy Middleware")
        self.app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")  # trust upstream server (e.g. nginx)
        return True

    def middleware_cors(self) -> bool:
        logger.debug("Enabling CORS Middleware")
        self.app.add_middleware(CORSMiddleware, allow_origins="*", allow_methods="*")
        return True

    def middleware_conditional_http_cache(self) -> bool:
        logger.debug("Enabling HTTP Cache Middleware")
        self.app.add_middleware(HttpCacheMiddlewareFix, enable=not config['DEBUG'])
        return True

    def middleware_deny_early_data(self) -> bool:
        if not config['SERVER_SSL']:
            return False
        # See: https://blog.trailofbits.com/2019/03/25/what-application-developers-need-to-know-about-tls-early-data-0rtt/
        logger.debug("Enabling Early Deny (0-RTT) Middleware")
        self.app.add_middleware(EarlyDataMiddleware, deny_all=True)
        return True


class HttpCacheMiddlewareFix(BaseHTTPMiddleware):

    def __init__(self, app: ASGIApp, enable: bool = True):
        super().__init__(app)
        self.should_cache = enable

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        if self.should_cache:
            response.headers["Cache-Control"] = "public, max-age=0"
        else:
            # No Cache during Development
            response.headers["Expires"] = "0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
