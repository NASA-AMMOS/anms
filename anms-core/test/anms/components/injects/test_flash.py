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

from anms.components.injects import FlashContainer, flash
from anms.components.schemas import SessionSchema

from fastapi.requests import Request

@pytest.fixture
def example_request():
    scope={"type":"http"}
    yield Request(scope=scope)

class TestFlashContainer:

    def test_init(self, example_request):
        session = SessionSchema()
        flash_container = FlashContainer(success_bin=[],
                                         error_bin=[],
                                         session=session,
                                         request=example_request)
        assert flash_container.session == session
        assert flash_container.request == example_request
        assert len(flash_container.success_bin) == 0
        assert len(flash_container.error_bin) == 0


class MockInstance:

    def __init__(self):
        self.flash_success = []
        self.flash_error = []


class MockSession:

    def __init__(self, instance: MockInstance = MockInstance(), request: Request = example_request):
        self.instance = instance
        self.request = request


def test_flash_pristine_inject(example_request):
    instance = MockInstance()
    session = MockSession(instance=instance, request=example_request)
    flashed_container = flash.flash_pristine_inject(session=session)
    assert flashed_container.session == instance
    assert flashed_container.request == example_request
