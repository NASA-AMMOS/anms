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
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (Boolean, Column, DateTime, Integer, String, func,
                        inspect, select, or_, update)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Query, Session
from sqlalchemy import exc

from anms.models.relational import Model, get_async_session
from anms.shared.config_utils import ConfigBuilder

from anms.shared.opensearch_logger import OpenSearchLogger

logger = OpenSearchLogger(__name__).logger

# It's heavy to initialize this constructor, let's make it a shared instance

config = ConfigBuilder.get_config()


class User(Model):
    __tablename__="user"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String,unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


    @classmethod
    async def add_user(
            cls,  values: Dict[str, any],
            session: AsyncSession = None
    ) -> Optional["User"]:
        db_user = User()
        db_user.email = values["email"]
        db_user.username = values["username"]
        db_user.first_name = values["first_name"]
        db_user.last_name = values["last_name"]
        session.add(db_user)
        try:
            await session.commit()
            await session.refresh(db_user)
        except exc.SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {str(e.args)}")
            return None
        return db_user
    
    @classmethod
    async def get(
            cls, username: str, session: AsyncSession = None
    ) -> Optional["User"]:
        '''
        Retrieve User by username

        '''
        stmt = select(cls).where(
            func.lower(cls.username) == func.lower(username))
        if session:
            result = await session.execute(stmt)
        else:
            async with get_async_session() as session:
                result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return user
    
    @classmethod
    async def check_exist(
            cls, username: str, email: str, session: AsyncSession = None
    ) :
        '''
        Retrieve User by username, if the User does not exist, create a new user with the given username

        '''
        stmt = select(cls.username, cls.email).where(
            or_(func.lower(cls.username) == func.lower(username),
                func.lower(cls.email) == func.lower(email)
            ))
        try:
            if session:
                result = await session.execute(stmt)
            else:
                async with get_async_session() as session:
                    result = await session.execute(stmt)
            rows = result.fetchall()
            return rows 
        except exc.SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {str(e.args)}")
            return None

    @classmethod
    async def update_user(
            cls, username: str,
            new_values: Dict[str, Any],
            session: AsyncSession = None
    ) -> bool:
        '''
        Username is controlled by other system and therefore cannot be updated. 
        It is needed for querying purpose only
        '''
        stmt = update(cls).values(new_values).where(func.lower(cls.username) == func.lower(username)).execution_options(synchronize_session="fetch")
        response = 200
        try:
            if session:
                result = await session.execute(stmt)
                await session.commit()
            else:
                async with get_async_session() as session:
                    result = await session.execute(stmt)
                    await session.commit()
            if result.rowcount < 1:
                logger.info(f"No row with username {username}, is updated")
                response = 404
            elif result.rowcount > 1:
                logger.error(f"More than one rows with username {username}, are updated")
            else:
                logger.info(f"Update user {username} successfully")
        except exc.SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {str(e.args)}")
            response = 500
        return response
            
    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }
        dict_obj["created_at"] = str(dict_obj["created_at"])
        dict_obj["updated_at"] = str(dict_obj["updated_at"])

        return dict_obj

    @classmethod
    def get_user_fields(cls):
        return ['first_name', 'last_name', 'username', 'email']
    
    @classmethod
    def get_unique_fields(cls):
        return ['username', 'email']
