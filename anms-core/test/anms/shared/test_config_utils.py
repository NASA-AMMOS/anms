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
import os
import tempfile
from unittest import mock
from unittest.mock import MagicMock

import pytest

from anms.shared.config_utils import AbstractConfig
from anms.shared.logger import LazyLogger

logger = LazyLogger(__name__).logger


class TestConfig(AbstractConfig):
    pass
TestConfig.__test__ = False

class TestAbstractConfig:

    def setup(self):
        self.root_dir = TestConfig.ROOT_DIR
        self.base_dir = TestConfig.BASE_DIR

    def teardown(self):
        TestConfig.ROOT_DIR = self.root_dir
        TestConfig.BASE_DIR = self.base_dir

    # TODO test conditional import based on setting typing.TYPE_CHECKING
    # TODO test when Non-None root_dir passed to __init__
    # TODO test log entries when DEBUG and/or TESTING are set to TRUE
    # TODO test base implementation of on_finalized called
    # TODO test get_logger with no _logger.level and no recognized handler

    # _process_paths(alt_path=None) causes error but should not occur while calls are protected by check

    @staticmethod
    def test_process_paths_nonexistent_alt_path():
        """_process_paths(alt_path=<non-existing path>) results in no changes in ROOT_DIR/BASE_DIR"""

        # store originals
        starting_root_dir: str = TestConfig.ROOT_DIR
        starting_base_dir: str = TestConfig.BASE_DIR

        TestConfig._process_paths(alt_path="/A_PATH_THAT_DOES_NOT_EXIST")

        assert TestConfig.ROOT_DIR is starting_root_dir
        assert TestConfig.BASE_DIR is starting_base_dir

    @staticmethod
    @mock.patch('test.anms.shared.test_config_utils.TestConfig.BASE_CFG_FILE',
                os.path.join(TestConfig.ROOT_DIR, "config.yaml"))
    def test_process_paths_existing_alt_path():
        """_process_paths(alt_path=<non-existing path>) results in no changes in ROOT_DIR/BASE_DIR"""
        # store originals
        starting_root_dir: str = TestConfig.ROOT_DIR
        starting_base_dir: str = TestConfig.BASE_DIR

        # get an existing temp directory
        temp_dir: str = tempfile.gettempdir()

        TestConfig._process_paths(alt_path=temp_dir)

        # show that ROOT_DIR has been updated
        assert TestConfig.ROOT_DIR is not starting_root_dir
        assert TestConfig.ROOT_DIR == temp_dir

        # show that BASE_DIR has been updated
        assert TestConfig.BASE_DIR is not starting_base_dir
        assert TestConfig.BASE_DIR == temp_dir

        # show that the variable with previous ROOT_DIR base has been updated
        assert TestConfig.BASE_CFG_FILE == os.path.join(temp_dir, "config.yaml")


class TestProcessFileCfg:

    @staticmethod
    @mock.patch('anms.shared.config_utils.Path')
    @mock.patch('test.anms.shared.test_config_utils.TestConfig._merge_config')
    def test_callable_load_func(m_mc: MagicMock, m_p: MagicMock):

        # set up mocks
        load_func: MagicMock = MagicMock()
        expected_dict = {"TEST": "TEST_VAL"}
        load_func.return_value = expected_dict
        m_p.return_value.exists.return_value = True
        m_p.return_value.is_file.return_value = True

        top_level_only: bool = False  # Default

        # Function under test
        TestConfig._process_file_cfg(load_func=load_func)

        load_func.assert_called_once()
        m_mc.assert_called_once_with(expected_dict, top_level_only=top_level_only)

        # Try setting top_level_only true
        m_mc.reset_mock()
        top_level_only: bool = True
        TestConfig._process_file_cfg(load_func=load_func, top_level_only=top_level_only)
        m_mc.assert_called_once_with(load_func.return_value, top_level_only=top_level_only)

        # Try setting top_level_only false
        m_mc.reset_mock()
        top_level_only: bool = False
        TestConfig._process_file_cfg(load_func=load_func, top_level_only=top_level_only)
        m_mc.assert_called_once_with(load_func.return_value, top_level_only=top_level_only)

    # TODO test using ruamel.yaml library (can this be done without disrupting the test using yaml library?)
    # TODO test using yaml library (can this be done without disrupting the test using ruamel.yaml library?)
    # TODO test no yaml library available (can this be done without disrupting the tests using yaml and ruamel.yaml?)


# TODO test _process_env_vars where matching_environ > 0
