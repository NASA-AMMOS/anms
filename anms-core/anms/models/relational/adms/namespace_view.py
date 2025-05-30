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
from typing import Any, Dict, Optional

from sqlalchemy import (Column, Integer, String, select)
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from anms.models.relational import Model, get_async_session
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

logger = OpenSearchLogger(__name__).logger
config = ConfigBuilder.get_config()

class Namespace(Model):
    __tablename__ = 'namespace'
    data_model_id = Column(Integer, unique=True, primary_key=True)
    namespace_type = Column(String)
    issuing_org = Column(String)
    name_string = Column(String)
    version_name = Column(String)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }
        return dict_obj




class NamespaceView(Model):
    __tablename__ = 'vw_namespace'
    enumeration = Column(Integer, unique=True, primary_key=True)
    data_model_name = Column(String)
    name_string = Column(String)
    version_name = Column(String)
    use_desc = Column(String)

    @classmethod
    async def getall(
            cls, session: AsyncSession = None
    ) -> Optional["NamespaceView"]:
        '''
        Retrieve all adms

        '''        
        stmt = select(cls)
        try:
            if session:
                result = await session.execute(stmt)
            else:
                async with get_async_session() as session:
                    result = await session.execute(stmt)
        except exc.SQLAlchemyError as e:
            logger.error(f"NamespaceView::getall SQLAlchemyError: {str(e.args)}")
            return None
        
        namespace_view_rows = result.all()
        namespace_views = None
        if namespace_view_rows != None:
            namespace_views = [row['NamespaceView'] for row in namespace_view_rows]

        return namespace_views
    
    @classmethod
    async def get(
            cls, enumeration: Integer,  session: AsyncSession = None
    ) -> Optional["NamespaceView"]:
        '''
        Retrieve all adms

        '''
        stmt = select(cls).where(cls.enumeration == enumeration)
        try:
            if session:
                result = await session.execute(stmt)
            else:
                async with get_async_session() as session:
                    result = await session.execute(stmt)
        except exc.SQLAlchemyError as e:
            logger.error(f"NamespaceView::get SQLAlchemyError: {str(e.args)}")
            return None 

        namespace_view_row = result.scalar_one_or_none()
        return namespace_view_row
    
    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }
        return dict_obj