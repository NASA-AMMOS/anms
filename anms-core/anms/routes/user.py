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
from fastapi import APIRouter, status, Response, Request
from fastapi.responses import JSONResponse
import json

from anms.models.relational import user
from anms.shared.opensearch_logger import OpenSearchLogger
from anms.models.relational import get_async_session
from anms.components.schemas.user import UserUpdateBase
from anms.components.schemas.user import UserBase
from pydantic import BaseModel, Field


# Helper function to check if a docker container image is up or not. 


router = APIRouter(tags=["USER"])
logger = OpenSearchLogger(__name__).logger

User = user.User

class Conflict(BaseModel):
  field: dict = Field(..., example= {"email": "abcd@example.com"})

class UserReturn(UserBase):
  id: int = Field(..., example = 1)
  created_at: str = Field(..., example = "2022-11-18T15:29:37.226127")
  updated_at: str = Field(..., example = "2022-11-18T15:29:37.226127")

#The below fields are used to store unique fields from ther user table

def is_authorized(request: Request, username: str):
  x_remote_user = request.headers.get("x-remote-user") 
  return x_remote_user== username

@router.get("/{username}", status_code=status.HTTP_200_OK, responses={200: {"model": UserReturn}})
async def get_user(username: str):
  response = None
  async with get_async_session() as session:
      result = await User.get(username, session)
      if result == None:
        message = f"{username} does not exist!"
        response = JSONResponse(status_code=404, content={"message": message})
      else:
        response = result
  return response

#create new user  
@router.post("", status_code=status.HTTP_201_CREATED, responses={409: {"model": Conflict}, 201: {"model": UserReturn}})
async def create_user(data: UserBase, request: Request):
  data_dict = data.dict()
  response = None
  existing_values = dict()
  #Check for authorization
  # print("Request headers:", request.headers)
  # if not is_authorized(request, data_dict["username"]):
  #   response = JSONResponse(status_code=401, content={"message": "Unauthorized"})
  #   return response
  #Check if username exist or email exist
  rows = await User.check_exist(data_dict["username"], data_dict["email"])
  if rows == None:
    response = JSONResponse(status_code=500, content={"message": "Internal Server Error"})
    return response
  elif len(rows) > 0:
    for row in rows:
      username, email = row
      if username == data_dict["username"]:
        existing_values["username"] = username
      if email == data_dict["email"]:
        existing_values["email"] = email
    response = JSONResponse(status_code=409, content={"field": existing_values})
    return response
  
  
  #Creating new user
  create_values = dict()
  for field in data_dict.keys():
    value = data_dict.get(field, "")
    if value != "":
      create_values[field] = value
  
  async with get_async_session() as session:
    result = await User.add_user(create_values, session)
    
    if result == None:
      response = JSONResponse(status_code=500, content={"message": "Internal Server Error"})
    else:
      username = data_dict.get("username", None)
      profile = result.as_dict()
      msg = f"User {username} is created"
      logger.info(msg)
      response = JSONResponse(status_code=201, content=profile)
  return response

#update user
@router.put("/{username}", status_code=status.HTTP_200_OK, responses={409: {"model": Conflict}})
async def update_user(username: str, data: UserUpdateBase):
  data_dict = data.dict()
  response = None
  existing_values = dict()

  #Check if updating unique fields are used by other users
  rows = await User.check_exist(username, data_dict["email"])
  if rows == None:
    response = JSONResponse(status_code=500, content={"message": "Internal Server Error"})
    return response
  elif len(rows) > 0:
    for row in rows:
      row_username, row_email = row
      #email does not belong to the updating username
      if row_username != username and row_email == data_dict["email"]:
        existing_values["email"] = row_email
        break
  
  if len(existing_values.keys()) > 0:
    response = JSONResponse(status_code=409, content={"field": existing_values})
    return response

  #Updating user data
  update_values = dict()
  for field in data_dict.keys():
    value = data_dict.get(field, "")
    if value != "":
      update_values[field] = value
  
  logger.info(f"Update values: {update_values} ")
  async with get_async_session() as session:
    result = await User.update_user(username,update_values, session)
    if result == 404:
      response = JSONResponse(status_code=404, content={"message": "User {username} does not exist"})
    elif result == 500:
      response = JSONResponse(status_code=500, content={"message": "Internal Server Error"})
    else:
      logger.info("Updated successfully")
      response = JSONResponse(status_code=200, content="") #204 is more approriate, but raising raise RuntimeError("Response content longer than Content-Length")
      #del response.body
  return response

'''
TODO
1. Create unit test for these api

'''