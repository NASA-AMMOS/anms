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
from typing import Any
from typing import Dict

from anms.models.relational import Model
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


# class for vw_ctrl_definition used for build ari
class FormalObject(Model):
    __tablename__ = 'vw_obj_formal_def'
    obj_metadata_id = Column(Integer, primary_key=True)
    type_name = Column(String, nullable=False)
    obj_name = Column(String, nullable=False)
    namespace_id = Column(Integer, nullable=False)
    adm_name = Column(String)
    adm_enum = Column(Integer)
    adm_enum_label = Column(String)
    use_desc = Column(String)
    obj_formal_definition_id = Column(Integer, nullable=False)
    formal_desc = Column(String)
    is_formal = True

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        return dict_obj

# class for vw_ctrl_definition used for build ari
class Control(Model):
    __tablename__ = 'vw_ctrl_definition'

    obj_metadata_id = Column(Integer, primary_key=True)
    obj_name = Column(String, nullable=False)
    namespace_id = Column(Integer, nullable=False)
    adm_name = Column(String)
    obj_formal_definition_id = Column(Integer, nullable=False)
    fp_spec_id = Column(Integer)
    num_parms = Column(Integer)
    parm_types = Column(String)
    parm_names = Column(String)
    parm_defaults = Column(String)
    use_desc = Column(String, nullable=False)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        return dict_obj

# class for vw_ctrl_definition used for build ari
class EddFormal(Model):
    __tablename__ = 'vw_edd_formal'
    obj_metadata_id = Column(Integer, primary_key=True)
    obj_name = Column(String)
    namespace_id = Column(Integer)
    obj_formal_definition_id = Column(Integer)
    fp_spec_id = Column(Integer)
    use_desc = Column(String, nullable=False)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        return dict_obj

# class for vw_ctrl_definition used for build ari
class EddFormalDef(Model):
    __tablename__ = 'edd_formal_definition'
    obj_formal_definition_id = Column(Integer, primary_key=True)
    fp_spec_id = Column(Integer)
    data_type_id = Column(Integer)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        return dict_obj

# class for vw_ctrl_definition used for build ari
class MacFormal(Model):
    __tablename__ = 'vw_mac_formal'
    obj_metadata_id = Column(Integer, primary_key=True)
    obj_name = Column(String)
    namespace_id = Column(Integer)
    obj_formal_definition_id = Column(Integer)
    fp_spec_id = Column(Integer)
    use_desc = Column(String, nullable=False)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        return dict_obj


# class for vw_ctrl_definition used for build ari
class RptFormal(Model):
    __tablename__ = 'vw_rptt_formal'
    obj_metadata_id = Column(Integer, primary_key=True)
    obj_name = Column(String)
    namespace_id = Column(Integer)
    obj_formal_definition_id = Column(Integer)
    fp_spec_id = Column(Integer)
    use_desc = Column(String, nullable=False)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        return dict_obj


class RptFormalDef(Model):
    __tablename__ = 'report_template_formal_definition'
    obj_formal_definition_id = Column(Integer, primary_key=True)
    fp_spec_id = Column(Integer)
    ac_id = Column(Integer)

    def __repr__(self) -> str:
        return self.as_dict().__repr__()

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

        return dict_obj