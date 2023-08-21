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
import logging
import os
from datetime import datetime
from typing import Any, Optional, Collection, Union, Tuple, MutableMapping, List

import pytest
import uuid
import mock
from mock import patch

from anms.components.schemas.logging import LoggingQueryResultsBase
from anms.shared.config import ConfigBuilder

from anms.shared.opensearch_logger import OpenSearchLogger, LOG_LEVEL, ANMS_COMPONENT


@pytest.fixture
def log_uid() -> str:
    """Returns the hexadecimal value for generated UUID value
    :rtype: object
    """
    return uuid.uuid4().hex


class MockOpenSearchClient:
    """This class is used as a mock for the OpenSearch python client"""

    def __init__(self):
        """Initializes the mock for the OpenSearch python client with initial data"""
        self.data = {'took': 18, 'timed_out': False,
                     '_shards': {'total': 1, 'successful': 1, 'skipped': 0, 'failed': 0},
                     'hits': {'total': 523, 'max_score': 2.0161302,
                              'hits': [{'_index': 'anms-index', '_id': '2d21b0c7-e9d3-453b-a419-1cbf17a585e0',
                                        '_score': 2.0161302,
                                        '_source': {
                                            'component': 'anms-core',
                                            'datetime': 1655839446706, 'data': {},
                                            'level': 20,
                                            'message': 'Initializing OpenSearch logger for anms-core'}}
                                       ]}}

    def get_log_results(self) -> List[LoggingQueryResultsBase]:
        """Process data attribute into a list of LoggingQueryResultsBase objects"""
        results = []
        # Note that the opensearchpy client search function returns an object that when you index to ['hits']['hits']
        #  strangely looks like a list but need to index 0 to get all results, below returns results similarly but
        #  not in the exact same process.
        hits = self.data['hits']['hits']
        for hit in hits:
            source = hit['_source']
            result = LoggingQueryResultsBase(id=hit['_id'],
                                             component=source['component'],
                                             message=source['message'],
                                             level=source['level'],
                                             data=source['data'],
                                             datetime=source['datetime'])
            results.append(result)
        return results

    def search(
            self,
            *,
            body: Optional[Any] = ...,
            index: Optional[Any] = ...,
            _source: Optional[Any] = ...,
            _source_excludes: Optional[Any] = ...,
            _source_includes: Optional[Any] = ...,
            allow_no_indices: Optional[Any] = ...,
            allow_partial_search_results: Optional[Any] = ...,
            analyze_wildcard: Optional[Any] = ...,
            analyzer: Optional[Any] = ...,
            batched_reduce_size: Optional[Any] = ...,
            ccs_minimize_roundtrips: Optional[Any] = ...,
            default_operator: Optional[Any] = ...,
            df: Optional[Any] = ...,
            docvalue_fields: Optional[Any] = ...,
            expand_wildcards: Optional[Any] = ...,
            explain: Optional[Any] = ...,
            from_: Optional[Any] = ...,
            ignore_throttled: Optional[Any] = ...,
            ignore_unavailable: Optional[Any] = ...,
            lenient: Optional[Any] = ...,
            max_concurrent_shard_requests: Optional[Any] = ...,
            min_compatible_shard_node: Optional[Any] = ...,
            pre_filter_shard_size: Optional[Any] = ...,
            preference: Optional[Any] = ...,
            q: Optional[Any] = ...,
            request_cache: Optional[Any] = ...,
            rest_total_hits_as_int: Optional[Any] = ...,
            routing: Optional[Any] = ...,
            scroll: Optional[Any] = ...,
            search_type: Optional[Any] = ...,
            seq_no_primary_term: Optional[Any] = ...,
            size: Optional[Any] = ...,
            sort: Optional[Any] = ...,
            stats: Optional[Any] = ...,
            stored_fields: Optional[Any] = ...,
            suggest_field: Optional[Any] = ...,
            suggest_mode: Optional[Any] = ...,
            suggest_size: Optional[Any] = ...,
            suggest_text: Optional[Any] = ...,
            terminate_after: Optional[Any] = ...,
            timeout: Optional[Any] = ...,
            track_scores: Optional[Any] = ...,
            track_total_hits: Optional[Any] = ...,
            typed_keys: Optional[Any] = ...,
            version: Optional[Any] = ...,
            pretty: Optional[bool] = ...,
            human: Optional[bool] = ...,
            error_trace: Optional[bool] = ...,
            format: Optional[str] = ...,
            filter_path: Optional[Union[str, Collection[str]]] = ...,
            request_timeout: Optional[Union[int, float]] = ...,
            ignore: Optional[Union[int, Collection[int]]] = ...,
            opaque_id: Optional[str] = ...,
            http_auth: Optional[Union[str, Tuple[str, str]]] = ...,
            api_key: Optional[Union[str, Tuple[str, str]]] = ...,
            params: Optional[MutableMapping[str, Any]] = ...,
            headers: Optional[MutableMapping[str, str]] = ...,
    ) -> Any:
        return self.data

    def create(
            self,
            index: Any,
            id: Any,
            body: Any,
            pipeline: Optional[Any] = ...,
            refresh: Optional[Any] = ...,
            routing: Optional[Any] = ...,
            timeout: Optional[Any] = ...,
            version: Optional[Any] = ...,
            version_type: Optional[Any] = ...,
            wait_for_active_shards: Optional[Any] = ...,
            pretty: Optional[bool] = ...,
            human: Optional[bool] = ...,
            error_trace: Optional[bool] = ...,
            format: Optional[str] = ...,
            filter_path: Optional[Union[str, Collection[str]]] = ...,
            request_timeout: Optional[Union[int, float]] = ...,
            ignore: Optional[Union[int, Collection[int]]] = ...,
            opaque_id: Optional[str] = ...,
            http_auth: Optional[Union[str, Tuple[str, str]]] = ...,
            api_key: Optional[Union[str, Tuple[str, str]]] = ...,
            params: Optional[MutableMapping[str, Any]] = ...,
            headers: Optional[MutableMapping[str, str]] = ...,
    ) -> Any:
        return {"_id": log_uid}


class TestOpenSearchLogger:

    @staticmethod
    @pytest.fixture
    def mock_client() -> MockOpenSearchClient:
        return MockOpenSearchClient()

    @staticmethod
    @pytest.fixture
    def config() -> dict:
        """Returns the configuration object for the application"""
        return ConfigBuilder.get_config()

    @staticmethod
    @pytest.fixture
    def log_dir(config: dict) -> str:
        return os.path.join(config['ROOT_DIR'], config['ROOT_DIR'])

    @staticmethod
    @pytest.fixture
    def log_file(config: dict, log_dir: str) -> str:
        return os.path.join(log_dir, config['LOGGER_FILE'])

    @staticmethod
    @pytest.fixture
    def log_msg() -> str:
        return "test message"

    @staticmethod
    @pytest.fixture
    def opensearch_logger(log_uid: str, mock_client: MockOpenSearchClient):
        return OpenSearchLogger(log_uid=log_uid, log_console=False, client=mock_client)

    def test_init(self,
                  config: dict,
                  opensearch_logger: OpenSearchLogger,
                  mock_client: MockOpenSearchClient,
                  log_dir: str,
                  log_file: str,
                  log_uid: str):
        assert opensearch_logger.log_uid == log_uid, \
            "The uuid passed to the OpenSearchLogger as this clase' log_uid"
        assert opensearch_logger.log_dir == log_dir, \
            ("The log_dir variable should be the same in both OpensearchLogger and as a fixture, since they are based "
             "on the same configuration")
        assert opensearch_logger.log_file == log_file, \
            ("The log_file variable should be the same in both OpensearchLogger and the config object as they are based"
             " on the same information")
        assert opensearch_logger.log_level == config["LOGGER_LEVEL"], \
            ("The log_level variable should be the same in both OpensearchLogger and the config object as they are "
             "based on the same information")
        assert opensearch_logger.client == mock_client, \
            ("The client variable should be the same in OpensearchLogger and the mock_client fixture, as it is what is "
             "passed to the logger.")
        assert opensearch_logger.index_name == config["OPENSEARCH_INDEX_NAME"], \
            ("The index_name variable should be the same in both OpensearchLogger and the config object as they are "
             "based on the same information")
        assert opensearch_logger.index_body == config["OPENSEARCH_INDEX_BODY"], \
            ("The index_body variable should be the same in both OpensearchLogger and the config object as they are "
             "based on the same information")

    @patch('logging.Logger')
    def test_debug(self, internal_logger: logging.Logger, opensearch_logger: OpenSearchLogger, log_msg: str):
        opensearch_logger.debug(msg=log_msg)
        assert internal_logger.called_with(msg=log_msg, level=logging.DEBUG)

    @patch('logging.Logger')
    def test_info(self, internal_logger: logging.Logger, opensearch_logger: OpenSearchLogger, log_msg: str):
        opensearch_logger.info(msg=log_msg)
        assert internal_logger.called_with(msg=log_msg, level=logging.INFO)

    @patch('logging.Logger')
    def test_warn(self, internal_logger: logging.Logger, opensearch_logger: OpenSearchLogger, log_msg: str):
        opensearch_logger.warn(msg=log_msg)
        assert internal_logger.called_with(msg=log_msg, level=logging.WARN)

    @patch('logging.Logger')
    def test_error(self, internal_logger: logging.Logger, opensearch_logger: OpenSearchLogger, log_msg: str):
        opensearch_logger.error(msg=log_msg)
        assert internal_logger.called_with(msg=log_msg, level=logging.ERROR)

    @patch('logging.Logger')
    def test_exception(self, internal_logger: logging.Logger, opensearch_logger: OpenSearchLogger, log_msg: str):
        opensearch_logger.exception(msg=log_msg)
        assert internal_logger.called_with(msg=log_msg, level=logging.ERROR)

    @patch('logging.Logger')
    def test_critical(self, internal_logger: logging.Logger, opensearch_logger: OpenSearchLogger, log_msg: str):
        opensearch_logger.critical(msg=log_msg)
        assert internal_logger.called_with(msg=log_msg, level=logging.CRITICAL)

    @patch('logging.Logger')
    def test_log(self, internal_logger: logging.Logger, opensearch_logger: OpenSearchLogger, log_msg: str):
        opensearch_logger.log(level=logging.DEBUG, msg=log_msg)
        assert internal_logger.called_with(msg=log_msg, level=logging.DEBUG)
        opensearch_logger.log(level=logging.INFO, msg=log_msg)
        assert internal_logger.called_with(msg=log_msg, level=logging.INFO)
        opensearch_logger.log(level=logging.WARN, msg=log_msg)
        assert internal_logger.called_with(msg=log_msg, level=logging.WARN)
        opensearch_logger.log(level=logging.ERROR, msg=log_msg)
        assert internal_logger.called_with(msg=log_msg, level=logging.ERROR)
        opensearch_logger.log(level=logging.CRITICAL, msg=log_msg)
        assert internal_logger.called_with(msg=log_msg, level=logging.CRITICAL)

    @staticmethod
    def perform_log_to_opensearch_test(level: LOG_LEVEL,
                                       msg: str,
                                       internal_logger: logging.Logger,
                                       logger: OpenSearchLogger,
                                       component: ANMS_COMPONENT = None):
        if level is None:
            result = logger.log_to_opensearch(message=msg, component_name=component)
            level = LOG_LEVEL.DEBUG
        else:
            result = logger.log_to_opensearch(level=logging.INFO, message=msg, component_name=component)
        assert internal_logger.called_with(msg=msg, level=level)
        assert result == log_uid, "The mock should return the log_uid fixture."

    @patch('logging.Logger')
    def test_log_to_opensearch(self,
                               internal_logger: logging.Logger,
                               opensearch_logger: OpenSearchLogger,
                               log_uid: str,
                               log_msg: str):
        self.perform_log_to_opensearch_test(level=None, msg=log_msg, internal_logger=internal_logger,
                                            logger=opensearch_logger, component=ANMS_COMPONENT.ANMS_CORE_COMPONENT)
        self.perform_log_to_opensearch_test(level=LOG_LEVEL.DEBUG, msg=log_msg, internal_logger=internal_logger,
                                            logger=opensearch_logger, component=ANMS_COMPONENT.ANMS_CORE_COMPONENT)
        self.perform_log_to_opensearch_test(level=LOG_LEVEL.INFO, msg=log_msg, internal_logger=internal_logger,
                                            logger=opensearch_logger, component=ANMS_COMPONENT.ANMS_CORE_COMPONENT)
        self.perform_log_to_opensearch_test(level=LOG_LEVEL.WARN, msg=log_msg, internal_logger=internal_logger,
                                            logger=opensearch_logger, component=ANMS_COMPONENT.ANMS_CORE_COMPONENT)
        self.perform_log_to_opensearch_test(level=LOG_LEVEL.ERROR, msg=log_msg, internal_logger=internal_logger,
                                            logger=opensearch_logger, component=ANMS_COMPONENT.ANMS_CORE_COMPONENT)
        self.perform_log_to_opensearch_test(level=logging.CRITICAL, msg=log_msg, internal_logger=internal_logger,
                                            logger=opensearch_logger, component=ANMS_COMPONENT.ANMS_CORE_COMPONENT)
        self.perform_log_to_opensearch_test(level=logging.CRITICAL, msg=log_msg, internal_logger=internal_logger,
                                            logger=opensearch_logger, component=ANMS_COMPONENT.ANMS_CORE_COMPONENT)
        self.perform_log_to_opensearch_test(level=logging.CRITICAL, msg=log_msg, internal_logger=internal_logger,
                                            logger=opensearch_logger,
                                            component=ANMS_COMPONENT.ANMS_CORE_COMPONENT)

    @staticmethod
    def perform_equality_test_log_query_result(actual_result: LoggingQueryResultsBase,
                                               expected_result: LoggingQueryResultsBase):
        assert actual_result.data == expected_result.data, \
            "The data in the result should be the same as the mock get_log_results returns for the same index."
        assert actual_result.message == expected_result.message, \
            "The message in the result should be the same as the mock get_log_results returns for the same index."
        assert actual_result.level == expected_result.level, \
            "The level in the result should be the same as the mock get_log_results returns for the same index."
        assert actual_result.component == expected_result.component, \
            "The component in the result should be the same as the mock get_log_results returns for the same index."
        assert actual_result.datetime == expected_result.datetime, \
            "The datetime in the result should be the same as the mock get_log_results returns for the same index."
        assert actual_result.id == expected_result.id, \
            "The id in the result should be the same as the mock get_log_results returns for the same index."

    def perform_test_get_logs(self,
                              opensearch_logger: OpenSearchLogger,
                              mock_client: MockOpenSearchClient,
                              component: ANMS_COMPONENT = ANMS_COMPONENT.ANMS_CORE_COMPONENT,
                              start_datetime: datetime = None,
                              end_datetime: datetime = None):
        actual_results = opensearch_logger.get_logs(component_name=component,
                                                    start_datetime=start_datetime, end_datetime=end_datetime)
        expected_results = mock_client.get_log_results()
        assert len(actual_results) == len(expected_results), ("The size of the actual and expected results"
                                                              " should be the same since the mock client "
                                                              "always returns the same results.")
        # Order of results should match because the result processing should maintain order
        for actual_result in actual_results:
            self.perform_equality_test_log_query_result(actual_result=actual_result,
                                                        expected_result=expected_results.pop())

    def test_get_logs(self,
                      opensearch_logger: OpenSearchLogger,
                      mock_client: MockOpenSearchClient):
        self.perform_test_get_logs(opensearch_logger=opensearch_logger, mock_client=mock_client)
        self.perform_test_get_logs(opensearch_logger=opensearch_logger,
                                   mock_client=mock_client, start_datetime=datetime.now())
        self.perform_test_get_logs(opensearch_logger=opensearch_logger, mock_client=mock_client,
                                   end_datetime=datetime.now())
        self.perform_test_get_logs(opensearch_logger=opensearch_logger, mock_client=mock_client,
                                   start_datetime=datetime.now(), end_datetime=datetime.now())
        self.perform_test_get_logs(opensearch_logger=opensearch_logger, mock_client=mock_client,
                                   component=None,
                                   start_datetime=datetime.now(), end_datetime=datetime.now())
