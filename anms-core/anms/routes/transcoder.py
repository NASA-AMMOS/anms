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
import time
import asyncio

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate

from sqlalchemy import select, or_, desc
from anms.models.relational import get_session

from anms.components.schemas import TranscoderLog as TL
from anms.models.relational import get_async_session
from anms.models.relational.transcoder_log import TranscoderLog

from anms.shared.opensearch_logger import OpenSearchLogger
from anms.shared.transmogrifier import TRANSMORGIFIER
from anms.routes.network_manager import do_nm_put_hex_eid

router = APIRouter(tags=["Transcoder"])
logger = OpenSearchLogger(__name__, log_console=True)


@router.get("/db/all", status_code=status.HTTP_200_OK, response_model=Page[TL])
async def paged_transcoder_log(params: Params = Depends()):
    async with get_async_session() as session:
        return await paginate(session, select(TranscoderLog).order_by(desc(TranscoderLog.transcoder_log_id)), params)


@router.get("/db/search/{query:path}", status_code=status.HTTP_200_OK, response_model=Page[TL])
async def paged_transcoder_log(query: str, params: Params = Depends()):
    async with get_async_session() as session:
        filters = []
        filters.append(TranscoderLog.input_string.ilike(f'%{query}%'))
        filters.append(TranscoderLog.uri.ilike(f'%{query}%'))
        filters.append(TranscoderLog.cbor.ilike(f'%{query}%'))
        if query.isdigit():
            filters.append(TranscoderLog.transcoder_log_id == int(query))

        return await paginate(session, select(TranscoderLog)
                              .where(or_(*filters))
                              .order_by(desc(TranscoderLog.transcoder_log_id)), params)

@router.get("/db/id/{id}", status_code=status.HTTP_200_OK, response_model=TL)
def transcoder_log_by_id(id: str):
    return _do_transcoder_log_by_id(id)
        
def _do_transcoder_log_by_id(id: str):
    with get_session() as session:
        return TranscoderLog.query.filter_by(transcoder_log_id=id).first()

# PUT 	/ui/incoming/{cbor}/hex
@router.put("/ui/incoming/{input_cbor}/hex", status_code=status.HTTP_200_OK)
async def transcoder_put_input_cbor(input_cbor: str):
    return _transcoder_put_cbor(input_cbor)


@router.get("/ui/incoming/await/{cbor}/hex", status_code=status.HTTP_200_OK)
async def transcoder_put_cbor_await(cbor: str):
    curr_entry = _transcoder_put_cbor(cbor)
    transcoder_log_id = curr_entry["id"]
    while True:
        with get_session() as session:
            curr_uri = TranscoderLog.query.filter(TranscoderLog.transcoder_log_id==transcoder_log_id).first()
            if curr_uri.parsed_as != "pending":
                if curr_uri.parsed_as == "ERROR":
                    curr_uri = "ARI://BADARI"
                else:
                    curr_uri = curr_uri.uri
                break
        time.sleep(1)


    return  {"data": curr_uri}

def _transcoder_put_cbor(input_cbor):
    transcoder_log_id = None
    send_to_transcode = False
    with get_session() as session:
        curr_uri = TranscoderLog.query.filter(or_(TranscoderLog.input_string==input_cbor, TranscoderLog.cbor==input_cbor)).first()
        
        if curr_uri is None:
            c1 = TranscoderLog(input_string=input_cbor, parsed_as='pending')
            session.add(c1)
            session.flush()
            session.refresh(c1)
            transcoder_log_id = c1.transcoder_log_id
            session.commit()
            send_to_transcode = True
        else:
            # the input_ari has already been submitted
            status = "ARI previously submitted, check log"
            transcoder_log_id = curr_uri.transcoder_log_id
        
    if(send_to_transcode):
        status = "Submitted ARI to transcoder"
        TRANSMORGIFIER.transcode(input_cbor)

    return {"id": transcoder_log_id, "status": status}


# PUT 	/ui/incoming/str 	Body is str ARI to send to transcoder
@router.get("/ui/incoming/await/str", status_code=status.HTTP_200_OK)
async def transcoder_put_await_str(input_ari: str):
    curr_entry = _transcoder_put_str(input_ari)
    transcoder_log_id = curr_entry["id"]
    while(True):
        with get_session() as session:
            curr_uri = TranscoderLog.query.filter_by(transcoder_log_id=transcoder_log_id).first()
            if curr_uri.parsed_as != "pending":
                if curr_uri.parsed_as == "ERROR":
                    curr_uri = "ARI://BADARI"
                else:
                    curr_uri = curr_uri.uri
                break
            time.sleep(1)

    return  {"data": curr_uri}
    

# PUT 	/ui/incoming/str 	Body is str ARI to send to transcoder
@router.put("/ui/incoming/str", status_code=status.HTTP_200_OK)
def transcoder_incoming_str(input_ari: str):
    return _transcoder_put_str(input_ari)

def transcoder_put_str(input_ari: str):
    input_ari = input_ari.strip()
    transcoder_log_id = None
    send_to_transcode = False
    with get_session() as session:
        curr_uri = TranscoderLog.query.filter(or_(TranscoderLog.input_string==input_ari,TranscoderLog.ari==input_ari, TranscoderLog.cbor==input_ari)).first()
        if curr_uri is None:
            c1 = TranscoderLog(input_string=input_ari, parsed_as='pending')
            session.add(c1)
            session.flush()
            session.refresh(c1)
            transcoder_log_id = c1.transcoder_log_id
            session.commit()
            send_to_transcode = True
        else:
            # the input_ari has already been submitted
            state = "ARI previously submitted, check log"
            transcoder_log_id = curr_uri.transcoder_log_id
    
    if(send_to_transcode):
        state = "Submitted ARI to transcoder"
        TRANSMORGIFIER.transcode(input_ari)

    return {"id": transcoder_log_id, "status": state}


# PUT 	/ui/incoming_send/str 	Body is str ARI to send to transcoder
@router.put("/ui/incoming_send/str", status_code=status.HTTP_200_OK,
            responses={
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"description" : "Error response from NM"},
                status.HTTP_504_GATEWAY_TIMEOUT: {"description" : "Manager response timed out"}
                       })
async def transcoder_send_ari_str(eid: str, ari: str):
    try:
        # Perform translation (API wrapper)
        idinfo = _transcoder_put_str(ari)

        # Retrieve details and wait for completion
        retries = 10
        while True:
            # Wait for request to process before checking state
            await asyncio.sleep(1)
            
            info = _do_transcoder_log_by_id(idinfo["id"])

            if info.parsed_as != "pending":
                break
            if retries <= 0:
                raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                                    detail={ "idinfo" : idinfo, "info" : info, "status" : "transcoder timeout" })

            retries -= 1

        if info.parsed_as == "ERROR":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail={ "idinfo" : idinfo, "info" : info, "status" : 500 })

        # Publish
        state = do_nm_put_hex_eid( eid, info.cbor )
        return { "idinfo" : idinfo, "info" : info, "status" : state }
    except HTTPException as e:
        e.detail = { "idinfo" : idinfo, "info" : info, "status" : e.status_code }
        raise e
    except Exception as e:
        logger.exception(e)
        return status.HTTP_500_INTERNAL_SERVER_ERROR


