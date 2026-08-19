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
import itertools
import logging
from typing import Callable, Optional, Sequence, Union

from fastapi import FastAPI
from fastapi.exception_handlers import (http_exception_handler,
                                        request_validation_exception_handler)
from fastapi.exceptions import RequestValidationError, StarletteHTTPException
from fastapi.openapi.docs import (get_redoc_html, get_swagger_ui_html,
                                  get_swagger_ui_oauth2_redirect_html)
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination

from anms.asgi.helpers import SecretsManager
from anms.asgi.middleware import MiddlewareManager
from anms.routes.registry import RoutesRegistry
from anms.shared.config import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger


# http://stackoverflow.com/questions/25319690/how-do-i-run-a-flask-app-in-gunicorn-if-i-used-the-application-factory-pattern
class FastApiApp(object):

    def __init__(self,
                 on_startup: Optional[Sequence[Callable]] = None,
                 on_shutdown: Optional[Sequence[Callable]] = None):
        self._app = FastAPI(title=config['APP_TITLE'], version=config['APP_VERSION'], debug=['config.DEBUG'], description=f"{config['APP_TITLE']} Docs",
                            docs_url=None, redoc_url=None, on_startup=on_startup, on_shutdown=on_shutdown)
        add_pagination(self._app)
        self.register_logging()
        self.register_handlers()
        self.register_middleware()
        self.register_docs()
        self.register_mounts()

    def __new__(cls, *args, **kwargs):  # type: ignore
        cls.register_singleton_handlers()
        return super().__new__(cls)

    @property
    def app(self) -> FastAPI:
        return self._app

    def get_app(self) -> FastAPI:
        return self._app

    @classmethod
    def get_new_app(cls) -> FastAPI:
        return cls().get_app()

    def register_logging(self) -> None:
        # Todo: Move to cls init arg?
        pyppeteer_loggers = ("pyppeteer",)
        uvicorn_loggers = ("uvicorn.error",)  # "uvicorn.access", "uvicorn.asgi",)
        gunicorn_loggers = ("gunicorn.error", "gunicorn.access",)
        fastapi_loggers = ("fastapi",)
        for logger_name in itertools.chain(pyppeteer_loggers, uvicorn_loggers):
            third_party_logger = logging.getLogger(logger_name)
            third_party_logger.handlers = logger.handlers
        pass

    def register_handlers(self) -> None:

        SecretsManager()

        @self.app.on_event("startup")
        def on_startup_sync() -> None:
            pass

        @self.app.on_event("shutdown")
        def on_shutdown_sync() -> None:
            pass

        @self.app.on_event("startup")
        async def on_startup_async() -> None:
            logger.info("Started ASGI Server")
            pass

        @self.app.on_event("shutdown")
        async def on_shutdown_async() -> None:
            logger.info("Stopped ASGI Server")
            pass

        @self.app.exception_handler(StarletteHTTPException)
        async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
            logger.warning("HTTP Error Occurred: %s %s", exc.status_code, exc.detail)
            return await http_exception_handler(request, exc)

        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
            logger.warning("Invalid Data Sent")
            return await request_validation_exception_handler(request, exc)

    @classmethod
    def register_singleton_handlers(cls) -> None:
        pass

    def register_middleware(self) -> None:
        # https://fastapi.tiangolo.com/advanced/middleware/
        middleware_manager = MiddlewareManager(self._app)
        middleware_manager.init_middleware()

    def register_docs(self) -> None:

        # Allows operating application completely offline...
        # https://fastapi.tiangolo.com/advanced/extending-openapi/#serve-the-static-files

        # Points to /docs/oauth2-redirect
        # Path Order Matters
        @self.app.get(self.app.swagger_ui_oauth2_redirect_url, include_in_schema=False)  # type: ignore
        async def swagger_ui_redirect() -> HTMLResponse:
            # Returns FastAPI Hardcoded Copy of swagger-ui-dist/oauth2-redirect.html
            return get_swagger_ui_oauth2_redirect_html()

        # Swagger UI (served at /docs - no trailing-slash redirect to work under any proxy)
        @self.app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html() -> HTMLResponse:
            # Build all URLs dynamically via JS so this works at any proxy prefix (/core/docs, /docs, etc.)
            # get_swagger_ui_html hardcodes oauth2RedirectUrl as window.location.origin + '/docs/oauth2-redirect'
            # which breaks under proxy prefixes. Use dynamic JS to construct everything.
            return HTMLResponse(
                '<!DOCTYPE html>'
                '<html><head>'
                '<meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                '<title>Swagger UI</title>'
                '<style>body{margin:0}#swagger-ui .topbar{display:none}</style>'
                '<script>'
                '(function(){'
                'var b=window.location.pathname.replace(/\\/docs$/,"");'
                'var c=document.createElement("link");'
                'c.rel="stylesheet";c.href=b+"/release/assets/fastapi/swagger-ui-dist/swagger-ui.css";'
                'document.head.appendChild(c);'
                'var f=document.createElement("link");'
                'f.rel="icon";f.href=b+"/release/favicon.png";'
                'document.head.appendChild(f);'
                'var s=document.createElement("script");'
                's.src=b+"/release/assets/fastapi/swagger-ui-dist/swagger-ui-bundle.js";'
                's.onload=function(){'
                'var p=document.createElement("script");'
                'p.src=b+"/release/assets/fastapi/swagger-ui-dist/swagger-ui-standalone-preset.js";'
                'p.onload=function(){'
                'SwaggerUIBundle({url:b+"/openapi.json",dom_id:"#swagger-ui",'
                'layout:"BaseLayout",deepLinking:true,showExtensions:true,showCommonExtensions:true,'
                'oauth2RedirectUrl:window.location.pathname+"/oauth2-redirect",presets:['
                'SwaggerUIBundle.presets.apis,SwaggerUIBundle.SwaggerUIStandalonePreset]});};'
                'document.head.appendChild(p);};'
                'document.head.appendChild(s);})();'
                '</script>'
                '</head><body><div id="swagger-ui"></div></body></html>'
            )

        # ReDoc (served at /redoc - no trailing-slash redirect to work under any proxy)
        @self.app.get("/redoc", include_in_schema=False)
        async def redoc_html() -> HTMLResponse:
            # Use dynamic JS (same pattern as Swagger) so assets resolve at any proxy prefix
            return HTMLResponse(
                '<!DOCTYPE html>'
                '<html><head>'
                '<meta charset=\"utf-8\">'
                '<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">'
                '<title>AMMOS-ANMS - ReDoc</title>'
                '<style>body{margin:0;padding:0}</style>'
                '<script>'
                '(function(){'
                'var b=window.location.pathname.replace(/\\/redoc$/,"");'
                'var f=document.createElement("link");'
                'f.rel="icon";f.href=b+"/release/favicon.png";'
                'document.head.appendChild(f);'
                'var s=document.createElement("script");'
                's.src=b+"/release/assets/fastapi/redoc/bundles/redoc.standalone.js";'
                's.onload=function(){'
                'var r=document.createElement("redoc");'
                'r.setAttribute("spec-url",b+"/openapi.json");'
                'document.body.appendChild(r);};'
                'document.head.appendChild(s);})();'
                '</script>'
                '</head><body></body></html>'
            )

    def register_mounts(self) -> None:
        route_registry = RoutesRegistry()

        # Global Mounts
        # TODO: use configuration variable for /release
        self.app.mount("/release", StaticFiles(directory=config['APP_STATIC_DIR']), name="static")

        # Route Mounts
        for mapping, router in route_registry.table.items():
            self._app.include_router(router, prefix=mapping.rstrip("/"))
