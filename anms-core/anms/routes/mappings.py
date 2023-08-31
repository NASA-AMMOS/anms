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
import posixpath
from enum import Enum

from anms.shared.config_utils import ConfigBuilder

config = ConfigBuilder.get_config()


class RoutesMapper(str, Enum):
    # Base
    base_prefix = posixpath.join("/", config['SERVER_CHROOT']).rstrip("/") + "/"

    # Route Paths
    hello_api_prefix = posixpath.join(base_prefix, "hello") + "/"
    agents_api_prefix = posixpath.join(base_prefix, "agents") + "/"
    parameter_api_prefix = posixpath.join(base_prefix, "agents", "parameter") +"/"


    ari_api_prefix = posixpath.join(base_prefix, "ari") + "/"

    actual_objects_api_prefix = posixpath.join(base_prefix, "actual_objects") + "/"
    actual_parameter_api_prefix = posixpath.join(base_prefix, "actual_parameter") + "/"
    formal_objects_api_prefix = posixpath.join(base_prefix, "formal_objects") + "/"
    formal_parameter_api_prefix = posixpath.join(base_prefix, "formal_parameter") + "/"
    literal_object_api_prefix = posixpath.join(base_prefix, "literal_object") + "/"
    reports_api_prefix = posixpath.join(base_prefix, "report") + "/"

    logging_api_prefix = posixpath.join(base_prefix, "logging") + "/"

    network_manager_api_prefix = posixpath.join(base_prefix, "nm") + "/"

    transcoder_api_prefix = posixpath.join(base_prefix, "transcoder") + "/"

    system_status_api_prefix = posixpath.join(base_prefix, "sys_status") + "/"
    user_api_prefix = posixpath.join(base_prefix, "users") + "/"
    adm_api_prefix = posixpath.join(base_prefix, "adms") + "/"

    alerts_prefix = posixpath.join(base_prefix, "alerts") + "/"

    @classmethod
    def as_dict(cls):
        return dict(
            (name, member.value) for name, member in cls.__members__.items()
        )
