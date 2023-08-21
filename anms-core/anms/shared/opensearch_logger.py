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

import datetime
import enum
import logging
import pydash as _
from typing import Any, Dict, Optional, List

from opensearchpy import OpenSearch
import os
import uuid
from anms.components.schemas.logging import LoggingQueryResultsBase

from anms.shared.config import ConfigBuilder
from anms.shared.logger import Logger

LOGGER_INITIALIZATION_MESSAGE = "Initializing OpenSearch logger for anms-core"
LOGGER_SHUTDOWN_MESSAGE = "Shutting Down OpenSearch logger for anms-core"

MILLIS_PER_SECOND = 1000
ONE_DAY_MILLIS = MILLIS_PER_SECOND * 60 * 60 * 24


class LOG_LEVEL(enum.Enum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


class ANMS_COMPONENT(enum.Enum):
    ANMS_CORE_COMPONENT = 'anms-core'
    ANMS_UI_COMPONENT = 'anms-ui'
    GRAFANA_COMPONENT = 'grafana'
    TRANSCODER_COMPONENT = 'transcoder'
    DATABASE_COMPONENT = 'database'
    OPENSEARCH_COMPONENT = 'opensearch'


config = ConfigBuilder.get_config()
client = OpenSearch(
    hosts=[{'host': config['OPENSEARCH_HOST'], 'port': config['OPENSEARCH_PORT']}],
    http_compress=True,  # enables gzip compression for request bodies
    http_auth=(config['OPENSEARCH_AUTH_USERNAME'], config['OPENSEARCH_AUTH_PASSWORD']),
    use_ssl=config['OPENSEARCH_USE_SSL'],
    verify_certs=config['OPENSEARCH_VERIFY_CERTS'],
    ssl_assert_hostname=config['OPENSEARCH_ASSERT_HOSTNAME'],
    ssl_show_warn=config['OPENSEARCH_SHOW_WARN']
)


class OpenSearchLogger(Logger):
    """This logger is meant to be used to augment other logging capabilities.  This logger will store messages and
    related data, into OpenSearch for other processes to view and process.

    Attributes:
        config (:class:`~anms.shared.config.BaseConfig`):
            The configuration object for retrieving OpenSearch-related configuration properties
        client (:class:`opensearchpy.Opensearch`):
            This is the client used to communicate with OpenSearch clusters and nodes
        index_name (:obj:`str`): String representation of the index name used for CRUD operations with OpenSearch
        index_body (:obj:`str`): String representation of the create index body used to establish connections

    """

    def __init__(self, log_uid=None, log_console=True, client: OpenSearch = client):
        """Initializes a OpenSearchLogger instance, using anms-core server configuration."""
        super(OpenSearchLogger, self).__init__(
            log_uid=(log_uid or uuid.uuid4().hex),
            log_dir=os.path.join(config['ROOT_DIR'], config['ROOT_DIR']),
            log_file=config['LOGGER_FILE'],
            log_level=config['LOGGER_LEVEL'],
            log_console=log_console)
        self.client = client
        self.index_name = config['OPENSEARCH_INDEX_NAME']
        self.index_body = config['OPENSEARCH_INDEX_BODY']

    def debug(self, msg, *args, **kwargs):
        """Overrides the Logger debug function"""
        self.log(level=logging.DEBUG, msg=msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Overrides the Logger info function"""
        self.log(level=logging.INFO, msg=msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        """Overrides the Logger warn function"""
        self.log(level=logging.WARN, msg=msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Overrides the Logger error function"""
        self.log(level=logging.ERROR, msg=msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        """Overrides the Logger exception function"""
        self.log(level=logging.ERROR, msg=msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Overrides the Logger critical function"""
        self.log(level=logging.CRITICAL, msg=msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        """Overrides the Logger log function"""
        self._internal_logger.log(msg=msg, level=level, *args, **kwargs)
        self.log_to_opensearch(level=level, message=msg, component_name=ANMS_COMPONENT.ANMS_CORE_COMPONENT.value)

    def log_to_opensearch(self, message: str,
                          level: LOG_LEVEL = logging.DEBUG,
                          data: Optional[Dict[str, Any]] = {},
                          component_name: str = "anms-core",
                          date_time: datetime.datetime = datetime.datetime.now()) -> str:
        """This function logs a message with metadata and optionally data to OpenSearch"""
        document = {
            "level": level,
            "component": component_name,
            "message": message,
            "datetime": date_time
        }
        if data:
            document['data'] = data
        try:
            response = self.client.create(index=self.index_name, id=uuid.uuid4(), body=document)
            return response['_id']
        except Exception as e:
            self._internal_logger.log(logging.ERROR, e)
            return None

    def get_logs(self, level: LOG_LEVEL = logging.ERROR,
                 component_name: str = ANMS_COMPONENT.ANMS_CORE_COMPONENT.value,
                 start_datetime: int = None, end_datetime: int = None,
                 size: int = 10, offset: int = 0) -> List[LoggingQueryResultsBase]:
        """This function queries OpenSearch for logged a message with metadata and optionally data and returns a list
        of results
        """
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "component": component_name
                            }
                        },
                        {
                            "range": {
                                "level": {
                                    "gte": level
                                }
                            }
                        }
                    ]
                }
            }
        }
        if start_datetime or end_datetime:
            time_range = {
                "range": {
                    "datetime": {}
                }
            }
            if start_datetime:
                time_range["range"]["datetime"]["gte"] = start_datetime
            if end_datetime:
                time_range["range"]["datetime"]["lte"] = end_datetime
            body["query"]["bool"]["must"].append(time_range)
        try:
            opensearch_results = self.client.search(index=[self.index_name],
                                                    _source=['component', 'message', 'level', 'data', 'datetime'],
                                                    size=size, from_=offset, rest_total_hits_as_int=True,
                                                    track_scores=False, body=body)
            results = _.chain(_.collections.at(opensearch_results, 'hits.hits')[0]).thru(
                self.process_opensearch_results_hits).value()
            return results
        except Exception as e:
            self._internal_logger.log(logging.ERROR, e)
            return None

    def process_opensearch_results_hits(self, hits) -> List[LoggingQueryResultsBase]:
        """Simple wrapper function that maps opensearch result hits into a List"""
        return _.collections.map_(hits, self.process_opensearch_results_hit)

    def process_opensearch_results_hit(self, hit) -> LoggingQueryResultsBase:
        """This function processes a single opensearch result hit dictionary into a LoggingQueryResultsBase object."""
        source = hit['_source']
        return LoggingQueryResultsBase(id=hit['_id'],
                                       component=_.objects.get(source, 'component', ANMS_COMPONENT.ANMS_CORE_COMPONENT),
                                       message=_.objects.get(source, 'message', ""),
                                       level=_.objects.get(source, 'level', logging.DEBUG),
                                       data=_.objects.get(source, 'data', None),
                                       datetime=_.objects.get(source, 'datetime', datetime.datetime.now()))
