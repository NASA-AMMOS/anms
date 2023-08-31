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
from typing import List

from fastapi import Depends
from fastapi.requests import Request

from anms.components.injects.session import SessionContainer
from anms.components.schemas import SessionSchema
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger


class FlashContainer(object):
    def __init__(
        self,
        success_bin: List[str],
        error_bin: List[str],
        session: SessionSchema,
        request: Request,
    ):
        self.success_bin = success_bin
        self.error_bin = error_bin
        self.session = session
        self.request = request

    def write(self):
        """
        Invoked when we'd like to update the session with flash messages added
        :return:
        """
        return self.request.session.update(self.session)


def flash_pristine_inject(
    session: SessionContainer = Depends(),
) -> FlashContainer:
    """
    Used to provided a pristine container to inject flash messages
    """
    session.instance.flash_success[:] = []
    session.instance.flash_error[:] = []
    return FlashContainer(
        session.instance.flash_success,
        session.instance.flash_error,
        session.instance,
        session.request,
    )


def flash_touched_inject(
    session: SessionContainer = Depends(),
) -> FlashContainer:
    """
    Used to provided a dirty container to inject flash messages
    """
    return FlashContainer(
        session.instance.flash_success,
        session.instance.flash_error,
        session.instance,
        session.request,
    )


def flash_messages_inject(
    session: SessionContainer = Depends(),
) -> FlashContainer:
    """
    Used to retrieve flash messages stored in session
    """
    flash_success = session.instance.flash_success.copy()
    flash_error = session.instance.flash_error.copy()
    session.instance.flash_success[:] = []
    session.instance.flash_error[:] = []
    session.write()
    return FlashContainer(
        flash_success, flash_error, session.instance, session.request
    )
