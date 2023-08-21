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

import collections
import logging
import os
import sys
import uuid
import weakref
from logging.handlers import TimedRotatingFileHandler

# NOTE: THIS FILE SHOULD BE ALWAYS LOCATED AT THE ROOT OF THE PYTHON PROJECT
BASE_DIR = os.path.normpath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)
)


class Logger(object):
    def __init__(
            self,
            log_uid=None,
            log_dir=None,
            log_file=None,
            log_level=None,
            log_console=True,
    ):
        self._internal_logger = None
        self.log_uid = log_uid if log_uid is not None else uuid.uuid4().hex
        self.log_dir = (
            os.path.join(BASE_DIR, log_dir)
            if log_dir is not None
            else os.path.join(BASE_DIR, "logs")
        )
        self.log_file = (
            os.path.join(self.log_dir, log_file)
            if log_file is not None
            else os.path.join(self.log_dir, "debug.log")
        )
        self.log_level = log_level if log_level is not None else logging.DEBUG
        self.enable_console = log_console
        self._configure_logger()

    @property
    def logger(self):
        """
        :rtype: logging.Logger
        """
        return self._internal_logger

    @property
    def handlers(self):
        """
        :rtype: List[logging.handlers.Handler]
        """
        return self._internal_logger.handlers

    def get_logger(self):
        """
        :rtype: logging.Logger
        """
        return self._internal_logger

    def _configure_logger(self):

        # Attempt some imports to enable/disable functionality
        try:
            import multiprocessing_logging
        except ImportError:
            multiprocessing_logging = None

        try:
            import colorlog
        except ImportError:
            colorlog = None

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self._internal_logger = logging.getLogger(self.log_uid)

        # check if it already was initialized
        if self._internal_logger.handlers:
            return

        self._internal_logger.propagate = False
        self._internal_logger.setLevel(self.log_level)

        console_handler_id = "stream.sys.stdout"
        rotating_file_handler_id = "rotating.%s" % self.log_file

        if rotating_file_handler_id not in HandlerStorage.handlers:
            internal_file_handler = TimedRotatingFileHandler(
                self.log_file, when="midnight", encoding="UTF-8", backupCount=30
            )
            internal_file_handler.name = rotating_file_handler_id
            internal_file_handler.setLevel(self.log_level)
            internal_file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                )
            )
            HandlerStorage.handlers[
                rotating_file_handler_id
            ] = internal_file_handler

        if (
                self.enable_console is True
                and console_handler_id not in HandlerStorage.handlers
        ):
            internal_console_handler = logging.StreamHandler(stream=sys.stdout)
            internal_console_handler.name = console_handler_id
            internal_console_handler.setLevel(self.log_level)
            if colorlog is None:
                stream_formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                )
            else:
                stream_formatter = colorlog.ColoredFormatter(
                    "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                )
            internal_console_handler.setFormatter(stream_formatter)
            HandlerStorage.handlers[
                console_handler_id
            ] = internal_console_handler

        # Configure Loggers to Send their Logs to the Main Process
        if multiprocessing_logging is not None:
            _ct = HandlerStorage.counter
            _m_wrapper = multiprocessing_logging.MultiProcessingHandler
            for handler_id, internal_handler in HandlerStorage.handlers.items():
                # Ignore if this handler is already wrapped...
                if isinstance(internal_handler, _m_wrapper):
                    continue
                # using OS get pid in case this is a child process...
                thread_name = "mp-handler-%s-%s" % (
                    os.getpid(),
                    _ct["id"],
                )
                _ct.update(
                    id=1
                )  # increment counter by 1, should be the same ref across threads...
                m_handler = _m_wrapper(
                    thread_name, sub_handler=internal_handler
                )
                HandlerStorage.handlers[
                    handler_id
                ] = m_handler  # substitute reference w/ multiprocess one

        # Attach Final Handlers
        self._internal_logger.addHandler(
            HandlerStorage.handlers[rotating_file_handler_id]
        )
        self._internal_logger.addHandler(
            HandlerStorage.handlers[console_handler_id]
        )


# Keeps around references to re-use handlers
class HandlerStorage(object):
    handlers = weakref.WeakValueDictionary()
    counter = collections.Counter(id=0)


class LazyLogger(Logger):
    def __init__(self, log_uid=None, log_console=True):
        from .config import ConfigBuilder

        self.config = ConfigBuilder.get_config()
        super(LazyLogger, self).__init__(
            log_uid=(log_uid or uuid.uuid4().hex),
            log_dir=os.path.join(self.config['ROOT_DIR'], self.config['ROOT_DIR']),
            log_file=self.config['LOGGER_FILE'],
            log_level=self.config['LOGGER_LEVEL'],
            log_console=log_console,
        )