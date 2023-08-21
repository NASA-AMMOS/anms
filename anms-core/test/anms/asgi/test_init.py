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
import pytest

from anms.asgi import FastApiApp


class TestFastApiApp:

    @staticmethod
    @pytest.fixture
    def default_fast_api_app():
        return FastApiApp(on_startup=None, on_shutdown=None)

    def test_init(self, default_fast_api_app: FastApiApp):
        assert len(default_fast_api_app.app.router.routes) > 0, ("The result of initialization is that a mount to the "
                                                                 "release folder for static content is added to the "
                                                                 "routes.")
        found_release_mount = False
        scope = {'type': "http", 'path': "release"}
        for route in default_fast_api_app.app.router.routes:
            found_release_mount = found_release_mount or route.matches(scope=scope)
        assert found_release_mount, ("The result of initialization is that a mount to the release folder for static "
                                     "content is added to the routes.")

    def test_app(self, default_fast_api_app):
        assert default_fast_api_app.app == default_fast_api_app.get_app(), \
            "app property and get_app should be the same."
        assert default_fast_api_app.app == default_fast_api_app._app, \
            "app property and protected _app property should be the same."

    def test_get_app(self, default_fast_api_app):
        assert default_fast_api_app.get_app() == default_fast_api_app.app, \
            "app property and get_app should be the same."
        assert default_fast_api_app.get_app() == default_fast_api_app._app, \
            "get_app function and protected _app property should be the same."

    def test_get_new_app(self, default_fast_api_app):
        result = default_fast_api_app.get_new_app()
        assert default_fast_api_app.get_new_app().description == default_fast_api_app.app.description, \
            "app property and get_new_app should be the same."
        assert default_fast_api_app.get_new_app().openapi_url == default_fast_api_app._app.openapi_url, \
            "get_new_app function and protected _app property should be the same."


