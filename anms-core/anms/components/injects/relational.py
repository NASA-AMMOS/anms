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
from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from anms.models.relational import async_session_factory, session_factory


# https://fastapi.tiangolo.com/tutorial/sql-databases/
# https://fastapi.tiangolo.com/advanced/async-sql-databases/

# Allows retrieving a temporary session to the DB
# https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
# FastAPI Doesn't like if you have your functions annotated with context managers... hence re-defining
def get_session_inject() -> Generator[Session, None, None]:
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


# Allows retrieving a temporary async session to the DB
# https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
# FastAPI Doesn't like if you have your functions annotated with context managers... hence re-defining
async def get_async_session_inject() -> AsyncGenerator[AsyncSession, None]:
    db = async_session_factory()
    try:
        yield db
    finally:
        await db.close()
