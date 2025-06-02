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
import logging
import os
import secrets
from datetime import timedelta
from pathlib import Path
from urllib.parse import urljoin

from .config_utils import AbstractConfig, ConfigBuilder

__all__ = ["ConfigBuilder", "AbstractConfig", "BaseConfig", "LocalConfig"]


class BaseConfig(AbstractConfig):
    # # # # GLOBAL PARAMETERS - ONLY EXTEND - # # # #

    ROOT_DIR = AbstractConfig.ROOT_DIR  # root of python project
    BASE_DIR = (
        AbstractConfig.BASE_DIR
    )  # root of module (may be the same as root of project)
    BASE_DATA_DIR = (
        AbstractConfig.BASE_DATA_DIR
    )
    BASE_CFG_FILE = (
        AbstractConfig.BASE_CFG_FILE
    )  # file to look for at BASE_DIR location to load from
    BASE_ENV_PREFIX = (
        AbstractConfig.BASE_ENV_PREFIX
    )  # environment variable prefix (used to match dynamic env vars)

    # # # # GLOBAL PARAMETERS - ONLY EXTEND - # # # #

    # # # ENVIRONMENT PARAMS # # #
    DEBUG = False
    TESTING = False
    LOGGER_NAME = BASE_ENV_PREFIX + "LOGGER"
    LOGGER_DIR = "logs"
    LOGGER_FILE = "/dev/null"
    LOGGER_LEVEL = logging.DEBUG

    # Directory Configs
    # DATA_DIR = os.path.join(ROOT_DIR, "data")

    # Web Networking
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5555
    SERVER_CHROOT = "/"
    SERVER_API_CHROOT = "/api/"
    SERVER_BIND = "0.0.0.0"
    SERVER_BEHIND_PROXY = False

    # SSL
    SERVER_SSL = False
    SERVER_SSL_CRT = None
    SERVER_SSL_KEY = None
    SERVER_SSL_PWD = None
    SERVER_PROXY_SSL = False

    # Gunicorn
    SERVER_WORKERS = 4
    SERVER_TIMEOUT = 60

    # Scheduler
    APSCHEDULER_MAX_THREAD_WORKERS = 20
    APSCHEDULER_MAX_PROCESS_WORKERS = 4

    # ASGI App Settings
    APP_TITLE = "AMMOS-ANMS"
    APP_VERSION = "0.1.0"
    APP_STATIC_DIR = os.path.join(Path(BASE_DIR), "static")
    APP_TEMPLATES_DIR = os.path.join(Path(BASE_DIR), "static")
    APP_SECRET_KEY = "fkxb7xMK3dSQt89Lo-klJMGuiM3Ro0chiDcHR6E6Ejc"
    APP_CSRF_ENABLED = True

    # ASGI App Cookie Settings
    APP_SESSION_COOKIE_NAME = "anms"
    APP_SESSION_COOKIE_LIFETIME = int(
        timedelta(hours=12).total_seconds()
    )  # 12 hours
    APP_SESSION_COOKIE_SECURE = SERVER_SSL or (
        SERVER_BEHIND_PROXY and SERVER_PROXY_SSL
    )
    APP_SESSION_COOKIE_HTTPONLY = True
    APP_SESSION_REFRESH_EACH_REQUEST = True
    APP_SESSION_COOKIE_SAMESITE = "Lax"
    APP_SESSION_TOKEN_LIFETIME = int(timedelta(days=1).total_seconds() /
                                     timedelta(minutes=1).total_seconds())  # minutes 1 day

    # Relation DB Settings
    DB_SCHEME = "postgresql+psycopg2"
    DB_ASYNC_SCHEME = "postgresql+asyncpg"
    DB_HOST = os.environ.get('DB_HOST', 'postgres')
    DB_PORT = 5432
    DB_USER = os.environ.get('DB_USER', "root")
    DB_PASS = os.environ.get('DB_PASSWORD', "root")
    DB_CHROOT = os.environ.get('DB_NAME', 'amp_core')


    # mqtt Settings
    # Let the name resolver determine the host to use at runtime
    MQTT_HOST = "mqtt-broker"
    MQTT_PORT = 1883
    MQTT_PASS = None
    MQTT_USER = None

    # nm Settings
    NM_HOST = "ion-manager"
    NM_PORT = 8089
    NM_API_BASE ="/nm/api"

    # Relation DB Settings (MySQL)
    # DB_SCHEME = "mysql+pymysql"
    # DB_ASYNC_SCHEME = "mysql+asyncmy"
    # DB_HOST = "db_container"
    # DB_PORT = 3306
    # DB_USER = "amp"
    # DB_PASS = "amp"
    # DB_CHROOT = "amp_core"

    DB_PARAMS = (
        dict()
    )  # https://www.post:wqgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS
    DB_MODELS_DIR = os.path.join(BASE_DIR, "models", "relational")
    # https://docs.sqlalchemy.org/en/latest/core/engines.html
    DB_POOL_SIZE = 50  # sqlalchemy.create_engine.params.pool_size
    DB_POOL_TIMEOUT = 30  # sqlalchemy.create_engine.params.pool_timeout
    DB_POOL_RECYCLE = 3600  # sqlalchemy.create_engine.params.pool_recycle
    DB_MAX_OVERFLOW = 10  # sqlalchemy.create_engine.params.max_overflow
    DB_ECHO = False  # sqlalchemy.create_engine.params.echo
    DB_ENCODING = "utf-8"

    OPENSEARCH_HOST = 'opensearch'
    OPENSEARCH_PORT = 9200
    OPENSEARCH_AUTH_USERNAME = 'admin'
    OPENSEARCH_AUTH_PASSWORD = 'admin'
    # OPENSEARCH_CA_CERTS = '/full/path/to/root-ca.pem' Provide a CA bundle if you use intermediate CAs with root CA.
    # Optional client certificates if you don't want to use HTTP basic authentication.
    # OPENSEARCH_CLIENT_CERT_PATH = '/full/path/to/client.pem'
    # OPENSEARCH_CLIENT_KEY_PATH = '/full/path/to/client-key.pem'
    OPENSEARCH_USE_SSL = True
    OPENSEARCH_VERIFY_CERTS = False
    OPENSEARCH_ASSERT_HOSTNAME = False
    OPENSEARCH_SHOW_WARN = False
    OPENSEARCH_INDEX_NAME = 'anms-index'
    OPENSEARCH_INDEX_BODY = {
        'settings': {
            'index': {
                'number_of_shards': 4
            }
        }
    }

    # Email Settings
    SMTP_TLS = True
    SMTP_PORT = 25
    SMTP_HOST = "localhost"
    SMTP_USER = None
    SMTP_PASS = None
    EMAIL_ENABLED = True
    EMAIL_FROM_NAME = "ANMS No-Reply"
    EMAIL_FROM_EMAIL = "no-reply@anms.jhuapl.edu"
    EMAIL_TEMPLATES_DIR = None
    EMAIL_RESET_TOKEN_EXPIRE_LIFETIME = int(
        timedelta(days=1).total_seconds()
    )  # 1 days

    # JSON for agent parameters
    AGENT_PARAMETER = os.environ.get('AGENT_PARAMETER', '/usr/local/share/anms/agent_parameter.json')
    AGENT_EID = os.environ.get('MANAGER_EID', 'ipn:1.6')

    # UI parameters
    UI_HOST = "anms-ui"
    UI_PORT = 9030
    UI_API_BASE = "/api/"

    def on_finalized(self):
        pass


class TestConfig(BaseConfig):
    TESTING = True

    DB_CHROOT = "anms_test"

class LocalConfig(BaseConfig):

    DB_HOST = "localhost"
    MQTT_HOST = "localhost"
    NM_HOST = "localhost"
    OPENSEARCH_HOST = "localhost"
    AGENT_PARAMETER = "anms/agent_parameter.json"
