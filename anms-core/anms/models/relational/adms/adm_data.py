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
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (LargeBinary, DateTime, Integer, Column, select, update)
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from anms.models.relational import Model, get_async_session
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

logger = OpenSearchLogger(__name__).logger

# It's heavy to initialize this constructor, let's make it a shared instance

config = ConfigBuilder.get_config()


# TODO: maybe add adm_enum, adm_name to the table
class AdmData(Model):
    __tablename__ = 'adm_data'
    adm_enum = Column(Integer, primary_key=True)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    @classmethod
    async def add_data(
            cls, values: Dict[str, any],
            session: AsyncSession = None
    ) -> Optional["AdmData"]:

        created_session = False
        if session is None:
            session = get_async_session()
            created_session = True

        try:
            admdata = AdmData()
            admdata.adm_enum = values["adm_enum"]
            admdata.data = values["data"]
        except Exception as e:
            error_message = f"AdmData add_data: Extracting value errors: {str(e.args)}"
            logger.error(error_message)
            return None, error_message
        try:
            session.add(admdata)
            await session.commit()
            await session.refresh(admdata)
        except exc.SQLAlchemyError as e:
            error_message = f"AdmData add_data SQLAlchemyError: {str(e.args)}"
            logger.error(error_message)
            return None, error_message
        return admdata, None

    @classmethod
    async def get(
            cls, adm_enum: int, session: AsyncSession = None
    ) -> Optional["AdmData"]:
        '''
        Retrieve data by adm_enum
        '''
        stmt = select(cls).where(
            cls.adm_enum == adm_enum)
        try:
            if session:
                result = await session.execute(stmt)
            else:
                async with get_async_session() as session:
                    result = await session.execute(stmt)
        except exc.SQLAlchemyError as e:
            error_message = f"AdmData get SQLAlchemyError: {str(e.args)}"
            logger.error(error_message)
            return None, error_message
        adm_data = result.scalar_one_or_none()
        return adm_data, None

    @classmethod
    async def update_data(
            cls, adm_enum: int,
            new_values: Dict[str, Any],
            session: AsyncSession = None
    ) -> bool:
        '''
        Update stored data based on adm_enum
        '''
        stmt = update(cls).values(new_values).where(cls.adm_enum == adm_enum).execution_options(
            synchronize_session="fetch")
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
                raise Exception(f"No row with adm_enum {adm_enum}, is updated")
            elif result.rowcount > 1:
                raise Exception(f"More than one rows with adm_enum {adm_enum}, are updated")
            else:
                logger.info(f"Update AdmData {adm_enum} successfully")
        except exc.SQLAlchemyError as e:
            error_message = f"AdmData update_data SQLAlchemyError: {str(e.args)}"
            logger.error(error_message)
            response = 500
        return response, error_message

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }
        dict_obj["created_at"] = str(dict_obj["created_at"])
        dict_obj["updated_at"] = str(dict_obj["updated_at"])

        return dict_obj
