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

# External modules
from fastapi import APIRouter, status, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi import UploadFile
from pydantic import BaseModel
import io
import traceback
from typing import TextIO

# Internal modules
from sqlalchemy import delete, select, and_
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from anms.models.relational.adms import (adm_data, data_model_view)
from anms.models.relational.adms.data_model_view import DataModel as ADM

from anms.routes.adms.adm_compare import (AdmCompare)
from anms.shared.opensearch_logger import OpenSearchLogger
from anms.shared.mqtt_client import MQTT_CLIENT
from anms.models.relational import get_async_session, get_session
from anms.components.schemas.adm import DataModelSchema
import ace
from camp.generators import (create_sql)

# Helper function to check if a docker container image is up or not.


router = APIRouter(tags=["ADM"])
logger = OpenSearchLogger(__name__).logger

AdmData = adm_data.AdmData
DataModel = data_model_view.DataModel

ACCEPT_FILE_CONTENT_TYPE = ["application/octet-stream","application/yang" ]


class RequestError(BaseModel):
    message: str = "Method is not allowed"


class UpdateAdmError(BaseModel):
    message: str = "Method is not allowed"
    error_details: list = []


# API routes
@router.get("/", status_code=status.HTTP_200_OK, responses={200: {"model": DataModelSchema}})
async def getall():
    response = None
    # return True
    async with get_async_session() as session:
        result = await DataModel.getall(session)
        if result == None:
            message = f"DataModel view does not exist!"
            response = JSONResponse(status_code=404, content={"message": message})
        else:
            response = result
    return response


# download specific adm
@router.get("/{enumeration}/{namespace}", status_code=status.HTTP_200_OK)
async def get_adm(enumeration: int,namespace: str):
    async with get_async_session() as session:
        result_dm =  await DataModel.get(enumeration, namespace, session)
        if result_dm:
            result, _ =  await AdmData.get(result_dm.data_model_id, session)
            if result:
                return result.data
            else:
                logger.error(f"ADM ENUM:{enumeration} in NAMESPACE {namespace} not a know ADM")
                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f"ADM ENUM:{enumeration} in NAMESPACE {namespace} not a know ADM")
        else:
            logger.error(f"ADM ENUM:{enumeration} in NAMESPACE {namespace} not a know DataModel")
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f"ADM ENUM:{enumeration} in NAMESPACE {namespace} not a know DataModel")



async def remove_ace_adm(enumeration: int):
    async with get_async_session() as session:
        stmt = delete(ace.models.AdmFile).where(ace.models.AdmFile.enum == enumeration)
        await session.execute(stmt)
        session.commit()



@router.delete("/{enumeration}/{namespace}", status_code=status.HTTP_200_OK)
async def remove_adm(enumeration: int, namespace:str):
    '''
  :param data_model_id: id for the adm to delete
  :return:
  '''
    stmt_1 = delete(DataModel).where(and_(DataModel.enumeration == enumeration,DataModel.namespace == namespace ))
    async with get_async_session() as session:
        nm_row = await DataModel.get(enumeration, namespace, session)
        if nm_row:
            logger.info(f"Removing {nm_row.name} ADM")
            stmt_2 = delete(AdmData).where(AdmData.enumeration == nm_row.data_model_id)
            await session.execute(stmt_1)
            await session.execute(stmt_2)
            await session.commit()
            return status.HTTP_200_OK
        else:
            logger.debug(f"ADM ENUM:{enumeration} in NAMESPACE {namespace} not a know ADM")
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f"ADM ENUM:{enumeration} in NAMESPACE {namespace} not a know ADM")



async def handle_adm(admset: ace.AdmSet, adm_file: ace.models.AdmModule, session, replace=True):
    ''' Process a received and decoded ADM into the ANMS DB.

    :param replace: If true and the ADM exists it will be checked and replaced.
    :return: A list of issues with the ADM, which is empty if successful.
    '''
    logger.info("Adm name: %s", adm_file.norm_name)
    data_model_view = await DataModel.get(adm_file.ns_model_enum,adm_file.ns_org_name )
    if data_model_view:
        if not replace:
            logger.info('Not replacing existing ADM name %s', adm_file.norm_name)
            return []
        data_rec = None
        async with get_async_session() as session:
            data_rec,_ = await AdmData.get(data_model_view.data_model_id,session)

        if data_rec:
            # Compare old and new contents
            logger.info("Checking existing ADM name %s", adm_file.norm_name)
            old_adm = admset.load_from_data(io.BytesIO(data_rec.data), del_dupe=False)
            comp = AdmCompare(admset)
            if not comp.compare_adms(old_adm, adm_file):
                issues = comp.get_errors()
            else:
                issues = [f"Updating existing adm is not allowed yet"]
            return issues

    logger.info("Inserting ADM name %s", adm_file.norm_name)

    # Use CAmPython to generate sql
    out_path = ""  # This is empty string since we don't need to write the generated sql to a file
    sql_dialect = 'pgsql'
    writer = create_sql.Writer(admset, adm_file, out_path, sql_dialect)
    string_buffer = io.StringIO()
    writer.write(string_buffer)

    # execute generated Sql
    queries = string_buffer.getvalue()
    try:
        await session.execute(queries)
        await session.commit()
    except Exception as err:
        logger.error(f"{sql_dialect} execution error: {err.args}")
        logger.debug('%s', traceback.format_exc())
        raise

    # Save the adm file of the new adm
    

    buf = io.StringIO()
    ace.adm_yang.Encoder().encode(adm_file, buf)
    ret_dm = await DataModel.get(adm_file.ns_model_enum,  adm_file.ns_org_name, session)
    
    # Write the encoded string data to the BytesIO object
    bytes_io = io.BytesIO()
    bytes_io.write(buf.getvalue().encode('utf-8'))
    # Reset the pointer to the beginning
    bytes_io.seek(0)
    data = {"enumeration":ret_dm.data_model_id, "data": bytes_io.getvalue()}
    await AdmData.add_data(data, session)

    return []


@router.post("/", status_code=status.HTTP_201_CREATED,
             responses={400: {"model": RequestError}, 405: {"model": UpdateAdmError}, 500: {"model": RequestError}})
async def update_adm(file: UploadFile, request: Request):
    response = None
    status_code = status.HTTP_201_CREATED
    message = ""
    error_details = []  # This is used to store the comparison details between the old adm and the new adm
    # Check if not application/json
    if file.content_type not in ACCEPT_FILE_CONTENT_TYPE:
        message = f"Expect {ACCEPT_FILE_CONTENT_TYPE}. Received: {file.content_type}"
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        logger.error(message)
    else:
        # Reading json file and check if it is a validated adm description
        admset = ace.AdmSet(cache_dir=False)
        comp = AdmCompare(admset)
        try:
            adm_file_contents = await file.read()
            try:
                adm_file = admset.load_from_data(io.StringIO(adm_file_contents.decode('utf-8')), del_dupe=False)
            except Exception as err:
                adm_file = None
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
                message = f'AdmSet failed to load file {file.filename}: {err.args}'
                raise Exception(message)

            if adm_file:
                logger.info("Adm name: %s", adm_file.norm_name)
                data_rec = None
                # get data_model_id
                async with get_async_session() as session:
                    data_model_rec = await DataModel.get(adm_file.ns_model_enum, adm_file.ns_org_name, session )
                    if data_model_rec == None:
                        logger.info("new ADM dont compare" )
                    else:
                        data_rec,_ = await AdmData.get(data_model_rec.data_model_id,session )
                        if data_rec == None:
                            logger.warning("ADM not in DB can't compare")
                    
                # Compare with existing adm
                if data_rec:
                    # Compare old and new contents
                    old_adm = admset.load_from_data(io.StringIO(data_rec.data.decode('utf-8')), del_dupe=False)
                    status_code = status.HTTP_200_OK
                    if not comp.compare_adms(old_adm, adm_file):
                        message = f"Updating existing adm {adm_file.norm_name}"
                        # delete old ADM
                        await remove_adm(adm_file.enum)
                        # reload adm_set
                        admset.db_session().close()
                        admset = ace.AdmSet(cache_dir=False)
                        adm_file = admset.load_from_data(io.StringIO(adm_file_contents.decode('utf-8')), del_dupe=False)
                    else: # if its the same nothing else to be done
                        logger.warning("Duplicate ADM add attempted")
                        message = "Duplicate ADM add attempted"
                        response = JSONResponse(status_code=status_code,
                                                content={"message": message, "error_details": error_details})
                        return response

            # Update to database
            info_message = "Creating" if status_code == status.HTTP_201_CREATED else "Updating"
            logger.info(f"{info_message} adm: {adm_file.norm_name}")
            out_path = ""  # This is empty string since we don't need to write the generated sql to a file
            sql_dialect = 'pgsql'
            writer = create_sql.Writer(admset, adm_file, out_path, sql_dialect)
            string_buffer = io.StringIO()
            try: # catching error in sql creation
                writer.write(string_buffer)
            except Exception as err:
                logger.error(f"{sql_dialect} execution error: {err.args}")
                details = err.args[0].split("\n")
                specific_detail = details[-1].replace("DETAIL:", "").strip()
                status_code = status.HTTP_400_BAD_REQUEST
                message = f"{info_message} adm error:  {specific_detail}"
                raise Exception(message)

            # execute generated Sql
            queries = string_buffer.getvalue()
            try:
                async with get_async_session() as session:
                    await session.execute(queries)
                    await session.commit()
                logger.info(f"{info_message} adm to database:  {adm_file.norm_name} successfully")
            except Exception as err:
                logger.error(f"{sql_dialect} execution error: {err.args}")
                details = err.args[0].split("\n")
                specific_detail = details[-1].replace("DETAIL:", "").strip()
                status_code = status.HTTP_400_BAD_REQUEST
                message = f"{info_message} adm error:  {specific_detail}"
                raise Exception(message)

            try:
                async with get_async_session() as session:
                    # get data_model_id 
                    data_model_rec = await DataModel.get(adm_file.ns_model_enum, adm_file.ns_org_name, session )
                    # Save the adm file of the new adm
                    data = {"enumeration": data_model_rec.data_model_id, "data": adm_file_contents}
                    response, error_message = await AdmData.add_data(data, session)
                if error_message:
                    raise Exception(error_message)
                # Notify the transcoder
                MQTT_CLIENT.publish('aricodec/reload', adm_file.norm_name)
                logger.info(f"{info_message} adm file:  {file.filename} successfully")
            except Exception as err:
                logger.error(f"{sql_dialect} execution error: {err.args}")
                details = err.args[0].split("\n")
                specific_detail = details[-1].replace("DETAIL:", "").strip()
                status_code = status.HTTP_400_BAD_REQUEST
                message = f"{info_message} adm error:  {specific_detail}"
                raise Exception(message)

            message = f"{info_message} adm:  {adm_file.norm_name} successfully"
            logger.info(message)
        except Exception as err:
            if status_code <= status.HTTP_400_BAD_REQUEST:
                message = f"Failed to process file {file.filename}. Error: {err.args}"
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            error_details = comp.get_errors()
            logger.error(message)
            traceback.print_exc()
    response = JSONResponse(status_code=status_code, content={"message": message, "error_details": error_details})
    return response