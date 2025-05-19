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
from typing import Any, Optional
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from anms.models.relational import Model, get_async_session
from sqlalchemy import Column, select, exc
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import LargeBinarys
from anms.shared.opensearch_logger import OpenSearchLogger

logger = OpenSearchLogger(__name__).logger


# class for vw_ctrl_definition used for build ari
class ARI(Model):
    __tablename__ = 'vw_ari_union'
    obj_metadata_id = Column(Integer, primary_key=True)
    obj_name = Column(String)
    adm_name = Column(String)
    type_name = Column(String)
    data_model_id = Column(Integer)
    obj_id = Column(Integer, primary_key=True)
    parm_id = Column(Integer)
    actual = Column(Boolean, primary_key=True)
    display = None
    param_names = None
    param_types = None

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        return dict_obj


class ARICollection(Model):
    __tablename__ = 'ari_collection'
    ac_id = Column(Integer, primary_key=True)
    num_entries = Column(Integer)
    entries = Column(LargeBinary)
    use_desc = Column(String)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        return dict_obj


class ADM(Model):
    __tablename__ = 'adm'
    data_model_id = Column(Integer, primary_key=True)
    adm_name = Column(String)
    adm_enum = Column(Integer)
    adm_enum_label = Column(String)
    use_desc = Column(String)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        return dict_obj

    @classmethod
    async def get(
            cls, adm_enum: Integer, session: AsyncSession = None
    ) -> Optional["adm"]:
        '''
        Retrieve all adms

        '''
        stmt = select(cls).where(cls.adm_enum == adm_enum)
        try:
            if session:
                result = await session.execute(stmt)
            else:
                async with get_async_session() as session:
                    result = await session.execute(stmt)
        except exc.SQLAlchemyError as e:
            logger.error(f"ADM::get SQLAlchemyError: {str(e.args)}")
            return None

        adm_row = result.scalar_one_or_none()
        return adm_row


class ObjMetadata(Model):
    __tablename__ = 'vw_obj_metadata'
    obj_metadata_id = Column(Integer, primary_key=True)
    data_type_id = Column(Integer)
    obj_name = Column(String)
    data_model_id = Column(Integer)
    adm_name = Column(String)
    adm_enum = Column(Integer)
    adm_enum_label = Column(String)
    use_desc = Column(String)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        return dict_obj
