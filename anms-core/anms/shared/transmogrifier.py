#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 The Johns Hopkins University Applied Physics
# Laboratory LLC.

# This file is part of the Asynchronous Network Management System (ANMS).

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This work was performed for the Jet Propulsion Laboratory, California
# Institute of Technology, sponsored by the United States Government under
# the prime contract 80NM0018D0004 between the Caltech and NASA under
# subcontract 1658085.

from camp.generators import (create_sql)
from anms.shared.config import ConfigBuilder
import asyncio
import anms.shared.mqtt_client
from anms.shared.opensearch_logger import OpenSearchLogger
from anms.models.relational import get_session
from anms.models.relational import get_async_session
from anms.models.relational.transcoder_log import TranscoderLog
from anms.models.relational.adms import (adm_data, data_model_view)
from anms.routes.adms.adm_compare import (AdmCompare)

import traceback
import ace
import io
import io
import json
import sqlalchemy

config = ConfigBuilder.get_config()
LOGGER = OpenSearchLogger(__name__, log_console=True).logger


# depending on what the config is for core will either use a MQTT server to send off commands or 
# use an ACE internally to translate 
class Transmorgifier:

    ''' The Transmogifier that can be configured to use an external or internal translator. '''
    # args = config 
    def __init__(self, args):
        # if the transcoding in internal to core
        LOGGER.info(config.Transcoder)
        self.adm_data = adm_data.AdmData
        self.data_model = data_model_view.DataModel
        if config.Transcoder == "Internal":
            db_uri = f"postgresql://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}/{config.DB_CHROOT}"
            LOGGER.info(f'Connecting to SQL DB at {db_uri}')
            self._dbeng = sqlalchemy.create_engine(db_uri)
            self.transcode = self._transcode_internal
            self.reload = self._reload_internal
            self._adm_reload(None)
        else:
            # setting up the MQTT server instead
            self.MQTT_CLIENT = anms.shared.mqtt_client.MQTT_CLIENT
            self.transcode = self._transcode_mqtt
            self.reload = self._reload_mqtt 
    
    async def handle_adm(self, admset: ace.AdmSet, adm_file: ace.models.AdmModule, session, replace=True):
        ''' Process a received and decoded ADM into the ANMS DB.

        :param replace: If true and the ADM exists it will be checked and replaced.
        :return: A list of issues with the ADM, which is empty if successful.
        '''
        LOGGER.info("Adm name: %s", adm_file.norm_name)
        data_model_view = await self.data_model.get(adm_file.ns_model_enum,adm_file.ns_org_name )
        if data_model_view:
            if not replace:
                LOGGER.info('Not replacing existing ADM name %s', adm_file.norm_name)
                return []
            data_rec = None
            async with get_async_session() as session:
                data_rec,_ = await self.adm_data.get(data_model_view.data_model_id,session)

            if data_rec:
                # Compare old and new contents
                LOGGER.info("Checking existing ADM name %s", adm_file.norm_name)
                old_adm = admset.load_from_data(io.BytesIO(data_rec.data), del_dupe=False)
                comp = AdmCompare(admset)
                if not comp.compare_adms(old_adm, adm_file):
                    issues = comp.get_errors()
                else:
                    issues = ["Updating existing adm is not allowed yet"]
                return issues

        LOGGER.info("Inserting ADM name %s", adm_file.norm_name)

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
            LOGGER.error(f"{sql_dialect} execution error: {err.args}")
            LOGGER.debug('%s', traceback.format_exc())
            raise

        # Save the adm file of the new adm
        buf = io.StringIO()
        ace.adm_yang.Encoder().encode(adm_file, buf)
        ret_dm = await self.data_model.get(adm_file.ns_model_enum,  adm_file.ns_org_name, session)
        
        # Write the encoded string data to the BytesIO object
        bytes_io = io.BytesIO()
        bytes_io.write(buf.getvalue().encode('utf-8'))
        # Reset the pointer to the beginning
        bytes_io.seek(0)
        data = {"enumeration":ret_dm.data_model_id, "data": bytes_io.getvalue()}
        await self.adm_data.add_data(data, session)

        return []
            
    async def load_default_adms(self):
        admset = ace.AdmSet(cache_dir=False)
        admset.load_default_dirs()
        issues = ace.Checker(admset.db_session()).check()
        for iss in issues:
            LOGGER.error('ADM issue %s', iss)

        for adm_file in admset:
            try:
                LOGGER.info('ADM %s handling started', adm_file.norm_name)
                async with get_async_session() as db_sess:
                    await self.handle_adm(admset, adm_file, db_sess, replace=False)
                LOGGER.info('ADM %s handling finished', adm_file.norm_name)
            except Exception as err:
                # The function already logged any SQL issue at error severity
                LOGGER.error('ADM %s handling failed: %s', adm_file.norm_name, err)
                LOGGER.debug('%s', traceback.format_exc())

        self.reload()

    def _transcode_mqtt(self, input):
        msg = json.dumps({'uri': input})
        LOGGER.info(f'PUBLISH to transcode/CoreFacing/Outgoing, msg = {msg}')
        self.MQTT_CLIENT.publish("transcode/CoreFacing/Outgoing", msg)

    def _transcode_internal(self, input):
        self._ace_transcode(input)
        
        # picking up any stray items that didnt get translated
        pending_uris = TranscoderLog.query.filter_by(parsed_as='pending').all()
        for entrys in pending_uris:
            try:
                self._ace_transcode(entrys.input_string)
            except Exception as err:
                LOGGER.error('Failed to process pending entry: %s', err)

    def _ace_transcode(self, input):
        # result object to fill in
        res_obj = {}
        res_obj['uri'] = ""
        res_obj['cbor'] = ""
        adms = ace.AdmSet()
        try:
            LOGGER.info(f'Request {input}')
            in_text = input.strip()
            res_obj['inputString'] = in_text
            in_lower = in_text.casefold()
            if in_lower.startswith('ari:0x') or in_lower.startswith('0x'):
                # Binary-to-text mode
                res_obj['parsedAs'] = 'CBOR'
    
                if in_lower.startswith('ari:'):
                    in_text = in_text[4:]

                try:
                    in_bytes = ace.cborutil.from_hexstr(in_text)
                    dec = ace.ari_cbor.Decoder()
                    ari = dec.decode(io.BytesIO(in_bytes))
                    LOGGER.debug(f'decoded as ARI {ari}')
                    ari = ace.nickname.Converter(ace.nickname.Mode.FROM_NN, adms.db_session(), False)(ari)
                    
                except Exception as err:
                    raise RuntimeError(f"Error decoding from `{in_text}`: {err}") from err
                res_obj['cbor'] = in_text
                res_obj['ari'] = f"{ari}"

                try:
                    enc = ace.ari_text.Encoder()
                    buf = io.StringIO()
                    enc.encode(ari, buf)

                    out_text = buf.getvalue()
                    if not out_text.startswith('ari:'):
                        out_text = 'ari:' + out_text
                    LOGGER.debug(f'encoded as text {out_text}')
                except Exception as err:
                    raise RuntimeError(f"Error encoding from {ari}: {err}") from err
                res_obj['uri'] = out_text

            else:
                # Text-to-binary mode
                res_obj['parsedAs'] = 'URI'
                
                try:
                    dec = ace.ari_text.Decoder()
                    ari = dec.decode(io.StringIO(in_text))
                    LOGGER.debug(f'decoded as ARI {ari}')
                    ari = ace.nickname.Converter(ace.nickname.Mode.FROM_NN, adms.db_session(), False)(ari)
                except Exception as err:
                    raise RuntimeError(f"Error decoding from `{in_text}`: {err}") from err
                
                # rencoding ari to ensure using non nicknames
                try:
                    enc = ace.ari_text.Encoder()
                    buf = io.StringIO()
                    enc.encode(ari, buf)

                    out_text = buf.getvalue()
                    if not out_text.startswith('ari:'):
                        out_text = 'ari:' + out_text
                    LOGGER.debug(f'encoded as text {out_text}')
                except Exception as err:
                    raise RuntimeError(f"Error encoding from {ari}: {err}") from err
              
                res_obj['uri'] = out_text
                res_obj['ari'] = f"{ari}"

                try:
                    enc = ace.ari_cbor.Encoder()
                    buf = io.BytesIO()
                    enc.encode(ari, buf)

                    hex_str = ace.cborutil.to_hexstr(buf.getvalue())
                    LOGGER.info(f'encoded as binary {hex_str}')
                except Exception as err:
                    raise RuntimeError(f"Error encoding from {ari}: {err}") from err
                res_obj['cbor'] = hex_str
        except Exception as err:
            res_obj['ari'] = f'Failed to process: {err}'
            res_obj['parsedAs'] = 'ERROR'
            LOGGER.error(f'Failed to process: {err}')
            LOGGER.info(f'Traceback:\n{traceback.format_exc()}')
            
        # store in transcoder database
        with get_session() as session:
                session.query(TranscoderLog).filter(TranscoderLog.input_string == input).update({
                    'parsed_as': res_obj['parsedAs'],
                    'ari': json.dumps(res_obj['ari']),
                    'cbor': res_obj['cbor'],
                    'uri':  res_obj['uri']
                })
                session.commit()
        LOGGER.info(f'Response {res_obj}')
        
        # client.publish('transcode/CodexFacing/Outgoing', json.dumps(res_obj))
        # just  log it back into the database

       

    def _reload_mqtt(self,adm_name=None):
        config = ConfigBuilder.get_config()
        host = config.get('MQTT_HOST')
        port = config.get('MQTT_PORT')

        LOGGER.info('Connecting to MQTT broker %s to notify aricodec' % host)
        
        msg = self.MQTT_CLIENT.publish('aricodec/reload', b'')
        if adm_name:
            msg = self.MQTT_CLIENT.publish('aricodec/reload', f'{adm_name}')
        msg.wait_for_publish()
        
        return
    
    def _reload_internal(self, adm_name=None):
        try:
            self._adm_reload(adm_name)
        except Exception as err:
            LOGGER.error('Failed to process reload: %s', err)
            LOGGER.info('Traceback:\n%s', traceback.format_exc())

    def _adm_reload(self, adm_name):
        with self._dbeng.connect() as db_conn:
            if adm_name:
                LOGGER.info('Reloading one ADM: %s', adm_name)
                curs = db_conn.execute('''\
SELECT data_model.name, adm_data.updated_at, adm_data.data
FROM adm_data 
    INNER JOIN data_model ON adm_data.enumeration = data_model..data_model_id
WHERE adm_name = ?
''', [adm_name])
                for row in curs.all():
                    self._handle_adm(*row)

            else:
                LOGGER.info('Reloading all ADMS...')

                curs = db_conn.execute('''\
SELECT data_model.name, adm_data.updated_at, adm_data.data
FROM adm_data 
    INNER JOIN data_model ON adm_data.enumeration = data_model.data_model_id
''')
                for row in curs.all():
                    self._handle_adm(*row)

        
                    
    def _handle_adm(self, adm_name, timestamp, data): 
        LOGGER.info(f'Handling ADM:{adm_name}')
        LOGGER.info(type(data))
        # LOGGER.info(data.tos())

        io_buffer = io.StringIO(data.tobytes().decode('utf-8'))
        adms = ace.AdmSet()
        adms.load_from_data(io_buffer)
        LOGGER.info('Handling finished')
        LOGGER.info('ADMS present for: %s', adms.names())

    
# SIGNALTON transmorgifier
TRANSMORGIFIER = Transmorgifier(config)