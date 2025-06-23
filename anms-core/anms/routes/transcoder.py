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
import json
import time

from fastapi import APIRouter, Depends
from fastapi import status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate

from sqlalchemy import select, or_, String, desc
from anms.models.relational import get_session

from anms.components.schemas import TranscoderLog as TL
from anms.models.relational import get_async_session
from anms.models.relational.transcoder_log import TranscoderLog
from anms.shared.mqtt_client import MQTT_CLIENT
from anms.shared.opensearch_logger import OpenSearchLogger

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
async def transcoder_log_by_id(id: str):
    with get_session() as session:
        return TranscoderLog.query.filter_by(transcoder_log_id=id).first()

# PUT 	/ui/incoming/{cbor}/hex
@router.put("/ui/incoming/{cbor}/hex", status_code=status.HTTP_200_OK)
async def transcoder_put_cbor(cbor: str):
    msg = json.dumps({'uri': cbor})
    transcoder_log_id = None
    with get_session() as session:
        curr_uri = TranscoderLog.query.filter_by(input_string=cbor).first()
        if curr_uri is None:
            c1 = TranscoderLog(input_string=cbor, parsed_as='pending')
            session.add(c1)
            session.flush()
            session.refresh(c1)
            transcoder_log_id = c1.transcoder_log_id
            session.commit()

    logger.info('PUBLISH to transcode/CoreFacing/Outgoing, msg = %s' % msg)
    MQTT_CLIENT.publish("transcode/CoreFacing/Outgoing", msg)

    return  {"id": transcoder_log_id}

# get 	/ui/incoming/{cbor}/hex
@router.get("/ui/incoming/await/{cbor}/hex", status_code=status.HTTP_200_OK)
async def transcoder_put_cbor_await(cbor: str):
    curr_uri = ""
    msg = json.dumps({'uri': cbor})
    transcoder_log_id = None
    with get_session() as session:
        curr_uri = TranscoderLog.query.filter_by(input_string=cbor).first()
        if curr_uri is None:
            c1 = TranscoderLog(input_string=cbor, parsed_as='pending')
            session.add(c1)
            session.flush()
            session.refresh(c1)
            transcoder_log_id = c1.transcoder_log_id
            session.commit()
            logger.info('PUBLISH to transcode/CoreFacing/Outgoing, msg = %s' % msg)
            MQTT_CLIENT.publish("transcode/CoreFacing/Outgoing", msg)
        else:
            transcoder_log_id = curr_uri.transcoder_log_id
            if curr_uri.parsed_as != "pending":
                if curr_uri.parsed_as == "ERROR":
                    curr_uri = "ARI://BADARI"
                else:
                    curr_uri = curr_uri.uri
                return  {"data": curr_uri}

    
    while True:
        with get_session() as session:
            curr_uri = TranscoderLog.query.filter_by(TranscoderLog.transcoder_log_id==transcoder_log_id).first()
        if curr_uri.parsed_as == "CBOR":
            curr_uri = curr_uri.uri
            break
        if curr_uri.parsed_as == "ERROR":
            curr_uri = "ARI://BADARI"
            break
        time.sleep(1)


    return  {"data": curr_uri}

# PUT 	/ui/incoming/str 	Body is str ARI to send to transcoder
@router.get("/ui/incomin/await/str", status_code=status.HTTP_200_OK)
def transcoder_put_await_str(ari: str):
    ari = ari.strip()
    msg = json.dumps({"uri": ari})
    transcoder_log_id = None
    with get_session() as session:
        curr_uri = TranscoderLog.query.filter_by(input_string=ari).first()
        if curr_uri is None:
            c1 = TranscoderLog(input_string=ari, parsed_as='pending')
            session.add(c1)
            session.flush()
            session.refresh(c1)
            transcoder_log_id = c1.transcoder_log_id
            session.commit()
            logger.info('PUBLISH to transcode/CoreFacing/Outgoing, msg = %s' % msg)
            MQTT_CLIENT.publish("transcode/CoreFacing/Outgoing", msg)
        else:
            transcoder_log_id = curr_uri.transcoder_log_id

    
    while(True):
        with get_session() as session:
            curr_uri = TranscoderLog.query.filter_by(transcoder_log_id=transcoder_log_id).first()
        if curr_uri.parsed_as == "URI":
            curr_uri = curr_uri.uri
            break
        if curr_uri.parsed_as == "ERROR":
            curr_uri = "ARI://BADARI"
            break
        time.sleep(1)


    return  {"data": curr_uri}
    

# PUT 	/ui/incoming/str 	Body is str ARI to send to transcoder
@router.put("/ui/incoming/str", status_code=status.HTTP_200_OK)
def transcoder_put_str(ari: str):
    ari = ari.strip()
    msg = json.dumps({"uri": ari})
    transcoder_log_id = None
    with get_session() as session:
        curr_uri = TranscoderLog.query.filter_by(input_string=ari).first()
        if curr_uri is None:
            c1 = TranscoderLog(input_string=ari, parsed_as='pending')
            session.add(c1)
            session.flush()
            session.refresh(c1)
            transcoder_log_id = c1.transcoder_log_id
            session.commit()
        else:
            transcoder_log_id = curr_uri.transcoder_log_id

    logger.info('PUBLISH to transcode/CoreFacing/Outgoing, msg = %s' % msg)
    MQTT_CLIENT.publish("transcode/CoreFacing/Outgoing", msg)

    return {"id": transcoder_log_id}



