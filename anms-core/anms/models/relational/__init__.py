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

import atexit
import importlib
import json
import os
import pkgutil
import sys
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Any, AsyncGenerator, Generator, Optional, Type

import pydash
from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (Query, Session, as_declarative, declared_attr,
                            scoped_session, sessionmaker)
from sqlalchemy.pool import QueuePool

import paho.mqtt.client as mqtt

from anms.shared.config import ConfigBuilder

from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger


# https://docs.sqlalchemy.org/en/13/orm/query.html
# https://docs.sqlalchemy.org/en/13/orm/mapped_attributes.html
# https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/api.html
# https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html
# https://docs.sqlalchemy.org/en/14/changelog/migration_14.html
# https://docs.sqlalchemy.org/en/14/changelog/migration_20.html

# Pattern: http://flask.pocoo.org/docs/latest/patterns/sqlalchemy/
# Reason: We control SQLAlchemy instead of Flask-SLQAlchemy only, this means we can use this outside of flask's context as well.


# Create NM URI
nm_url = "http://" + config['NM_HOST'] + ":" + str(config['NM_PORT']) + config['NM_API_BASE']

# Parse Engine URI
engine_url = URL.create(
    config['DB_SCHEME'],
    username=config['DB_USER'],
    password=config['DB_PASS'],
    host=config['DB_HOST'],
    port=config['DB_PORT'],
    database=config['DB_CHROOT'],
    query=config['DB_PARAMS'],
)

# Parse Async Engine URI
async_engine_url = URL.create(
    config['DB_ASYNC_SCHEME'],
    username=config['DB_USER'],
    password=config['DB_PASS'],
    host=config['DB_HOST'],
    port=config['DB_PORT'],
    database=config['DB_CHROOT'],
    query=config['DB_PARAMS'],
)

# Instantiate SqlAlchemy Engine
engine = create_engine(
    engine_url,
    poolclass=QueuePool,
    pool_size=config['DB_POOL_SIZE'],
    pool_recycle=config['DB_POOL_RECYCLE'],
    pool_timeout=config['DB_POOL_TIMEOUT'],
    max_overflow=config['DB_MAX_OVERFLOW'],
    echo=config['DB_ECHO'],
    encoding=config['DB_ENCODING'],
    pool_pre_ping=True,
    future=True,
)

# Instantiate Async SqlAlchemy Engine
async_engine = create_async_engine(
    async_engine_url,
    poolclass=QueuePool,
    pool_size=config['DB_POOL_SIZE'],
    pool_recycle=config['DB_POOL_RECYCLE'],
    pool_timeout=config['DB_POOL_TIMEOUT'],
    max_overflow=config['DB_MAX_OVERFLOW'],
    echo=config['DB_ECHO'],
    encoding=config['DB_ENCODING'],
    pool_pre_ping=True,
    future=True,
)

# Default Session Maker
# Import this to manage connections yourself
session_factory = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, future=True
)

# Default Async Session Maker
# Import this to manage connections yourself
if config['TESTING']:
    async_session_factory = sessionmaker(
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        future=True,
        expire_on_commit=False,  # if testing, state of instances are present after the commit
    )
else:
    async_session_factory = sessionmaker(
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        future=True,
    )

# Import this to commit, etc. (thread-safe)
# With coroutines (asyncio), this is dangerous as it uses thread local instead of contextvars...
# Different coroutines share the same thread.. so thread local is not safe anymore which is what scoped_session uses
db_session = scoped_session(session_factory)


# Declarative Mapping
@as_declarative(name="Model")
class Model(object):
    id: Any
    query: Query
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return pydash.snake_case(cls.__name__)


# Create/Retrive Metadata
metadata = Model.metadata  # type: MetaData

# Setup so you can type Model.query.xyz
Model.query = db_session.query_property()


# Makes sure session is cleaned at program exit
@atexit.register
def _remove_session():
    print("Cleaning DB Connections... %s" % engine, file=sys.stderr)
    db_session.remove()
    engine.dispose()


# Allows retrieving a temporary session to the DB
@contextmanager
def get_session() -> Generator[Session, None, None]:
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


# Allows retrieving a temporary async session to the DB
@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    db = async_session_factory()
    try:
        yield db
    finally:
        await db.close()


def init_base(models_path=config['DB_MODELS_DIR']) -> Optional[Type[Model]]:
    # Actually perform declarative Mapping
    try:
        if metadata.is_bound():
            return Model
        # Import Models To Map to base
        logger.info(f"Looking for models in: {models_path}")
        base_pkg_dir = Path(config['DB_MODELS_DIR']).relative_to(
            config['BASE_DIR']
        )  # get relative path to base directory
        base_pkg_normalized = str(base_pkg_dir).replace(
            os.sep, os.curdir
        )  # change path from / or \ to . notation
        for _, module_name, is_pkg in pkgutil.iter_modules(
                [models_path]
        ):  # type: pkgutil.ModuleInfo
            # skip packages
            if is_pkg:
                continue
            full_pkg_path = f"{base_pkg_normalized}.{module_name}"
            logger.info(f"Importing Model: {full_pkg_path}")
            # skip if already imported
            if full_pkg_path in sys.modules:
                continue
            # import module properly
            importlib.import_module(full_pkg_path)
        # Bind Engine (after loading models)
        metadata.bind = engine
        return Model
    except SQLAlchemyError as e:
        logger.error("SQLAlchemy Error", exc_info=e)
        raise e
    except (TypeError, ValueError, ModuleNotFoundError) as e:
        logger.error("Invalid Path", exc_info=e)
        raise e


def init_orm():
    # Actually perform/bind declarative Mapping
    try:
        init_base()
        logger.info("Initializing DB... %s", engine)
        metadata.create_all()
    except SQLAlchemyError as e:
        logger.error("SQLAlchemy Error", exc_info=e)


def drop_orm():
    try:
        init_base()
        logger.info("Clearing DB... %s", engine)
        metadata.drop_all()
    except SQLAlchemyError as e:
        logger.error("SQLAlchemy Error", exc_info=e)
