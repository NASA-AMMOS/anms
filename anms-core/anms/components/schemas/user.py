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
from typing import Dict, Optional

from pydantic import BaseModel, EmailStr, Field


class UserUpdatePassword(BaseModel):
    password: Optional[str] = None


class MinUserBase(BaseModel):
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    email: Optional[EmailStr] = Field(None, example="john.doe@example.com")


class UserUpdateBase(BaseModel):
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    email: Optional[EmailStr] = Field(None, example="john.doe@example.com")


class UserBase(MinUserBase):
    username: Optional[str] =  Field(None, example="johndoe")


# Properties to receive via API on creation
class UserInternalCreate(MinUserBase):
    username: Optional[str] = None
    details: Optional[Dict] = None
    roles: Optional[list] = None
    permissions: Optional[list] = None


class UserExternCreate(MinUserBase):
    is_extern_provider: Optional[bool] = True


class UserInDBBase(UserBase):
    id: Optional[int] = None
    details: Optional[Dict]

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    password: str


class UserPasswordReset(BaseModel):
    csrf_token: Optional[str] = Field(None, alias="csrfToken")
    new_password: Optional[str] = Field(None, alias="newPassword")

    class Config:
        allow_population_by_field_name = True
