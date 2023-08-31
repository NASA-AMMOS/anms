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
from unittest import mock

import pytest
from tenacity import stop_after_attempt, wait_none, RetryError
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from anms.components.init.db_seed import verify_connectivity, seed_data, main
from anms.models.relational import get_session
from anms.models.relational.user import User
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger


class TestVerifyConnectivity:

    @staticmethod
    @mock.patch('anms.models.relational.session_factory')
    def test_success(mocker_session_factory, mocker):
        # set up mock session
        mock_session = mocker.Mock()
        # set up mock session_factory to return mock session
        mocker_session_factory.return_value = mock_session

        # call function under test
        verify_connectivity()

        # assert that execute was called and no exceptions expected
        mock_session.execute.assert_called_once()
        # assert that the mocked session was closed when leaving scope
        mock_session.close.assert_called_once()

    @staticmethod
    @mock.patch('anms.models.relational.session_factory')
    def test_exception(mocker_session_factory, mocker):
        # set up mocks
        mock_session = mocker.Mock()
        mock_session.execute.side_effect = Exception
        mocker_session_factory.return_value = mock_session

        # call function under test expecting Exception
        with pytest.raises(RetryError):
            verify_connectivity.retry_with(stop=stop_after_attempt(1))()

        mock_session.execute.assert_called_once()
        mock_session.execute.reset_mock(side_effect=False)

        # show retries were attempted but remove the wait so it happens quickly
        with pytest.raises(RetryError):
            verify_connectivity.retry_with(wait=wait_none())()

        assert mock_session.execute.call_count == 60


class TestSeedData:
    ''' There is currently no DB seed data to test. '''
    pass


class TestMain:

    @staticmethod
    @mock.patch('anms.components.init.db_seed.seed_data')
    @mock.patch('anms.components.init.db_seed.verify_connectivity')
    @mock.patch('anms.models.relational.session_factory')
    def test_main(mocker_session_factory, mock_verify_con, mock_seed_data, mocker):
        # set up mock session
        mock_session = mocker.Mock()
        mocker_session_factory.return_value = mock_session

        # The function under test
        main()

        mock_verify_con.assert_called_once()
        mock_seed_data.assert_called_once()

        # assert that the mocked session was closed when leaving scope
        mock_session.close.assert_called_once()
