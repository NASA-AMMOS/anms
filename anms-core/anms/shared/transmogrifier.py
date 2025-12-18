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


from anms.shared.config import ConfigBuilder
from anms.shared.logger import Logger
from anms.shared.mqtt_client import MQTT_CLIENT
from anms.shared.opensearch_logger import OpenSearchLogger
from anms.models.relational import get_session
from anms.models.relational.transcoder_log import TranscoderLog
import traceback
import ace
import io
import io
import json
import sqlalchemy

config = ConfigBuilder.get_config()
LOGGER = OpenSearchLogger(__name__, log_console=True)


# depending on what the config is for core will either use a MQTT server to send off commands or 
# use an internal 
class Transmorgifier:

    ''' The Transmogifier that can be configured to use an external or internal translator. '''
    def __init__(self, args):
        # if the transcoding in internal to core
        if config.Transcoder == "internal":
            LOGGER.info('Connecting to SQL DB at %s', args.db_uri)
            self._dbeng = sqlalchemy.create_engine(args.db_uri)
            self._adms = ace.AdmSet(cache_dir=False)
            self.transcode = self._transcode_internal
            self.reload = self._reload_internal
            self._adm_reload(None)
        else:
            # setting up the MQTT server instead
            self.transcode = self._transcode_mqtt
            self.reload = self._reload_mqtt 

    def _transcode_mqtt(self, input):
        msg = json.dumps({'uri': input})
        LOGGER.info('PUBLISH to transcode/CoreFacing/Outgoing, msg = %s' % msg)
        MQTT_CLIENT.publish("transcode/CoreFacing/Outgoing", msg)

    def _transcode_internal(self, input):
        # result object to fill in
        res_obj = {}
        res_obj['uri'] = ""
        res_obj['cbor'] = ""
        
        try:
            req_obj = input
            LOGGER.info('Request %s', req_obj)

            in_text = req_obj['uri'].strip()
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
                    LOGGER.debug('decoded as ARI %s', ari)
                    # ace.nickname.Converter(ace.nickname.Mode.FROM_NN, self._admsSession(self._dbeng), True)(ari)
                    ari = ace.nickname.Converter(ace.nickname.Mode.FROM_NN, self._adms.db_session(), False)(ari)
                    
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
                    LOGGER.debug('encoded as text %s', out_text)
                except Exception as err:
                    raise RuntimeError(f"Error encoding from {ari}: {err}") from err
                res_obj['uri'] = out_text

            else:
                # Text-to-binary mode
                res_obj['parsedAs'] = 'URI'
                
                try:
                    dec = ace.ari_text.Decoder()
                    ari = dec.decode(io.StringIO(in_text))
                    LOGGER.debug('decoded as ARI %s', ari)
                    ari = ace.nickname.Converter(ace.nickname.Mode.FROM_NN, self._adms.db_session(), False)(ari)
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
                    LOGGER.debug('encoded as text %s', out_text)
                except Exception as err:
                    raise RuntimeError(f"Error encoding from {ari}: {err}") from err
              
                res_obj['uri'] = out_text
                res_obj['ari'] = f"{ari}"

                try:
                    enc = ace.ari_cbor.Encoder()
                    buf = io.BytesIO()
                    enc.encode(ari, buf)

                    hex_str = ace.cborutil.to_hexstr(buf.getvalue())
                    LOGGER.info('encoded as binary %s', hex_str)
                except Exception as err:
                    raise RuntimeError(f"Error encoding from {ari}: {err}") from err
                res_obj['cbor'] = hex_str

        except Exception as err:
            res_obj['ari'] = f'Failed to process: {err}'
            res_obj['parsedAs'] = 'ERROR'
            LOGGER.error('Failed to process: %s', err)
            LOGGER.info('Traceback:\n%s', traceback.format_exc())

        LOGGER.info('Response %s', res_obj)
        
        # client.publish('transcode/CodexFacing/Outgoing', json.dumps(res_obj))
        # just  log it back into the database

        # store in transcoder database
        with get_session() as session:
            session.query(TranscoderLog).filter(TranscoderLog.input_string == res_obj['inputString']). \
                update({
                    'parsed_as': res_obj['parsedAs'],
                    'ari': json.dumps(res_obj['ari']),
                    'cbor': res_obj['cbor'],
                    'uri':  res_obj['uri']
                })
            session.commit()

    def _reload_mqtt(self,adm_name):
        return
    
    def _reload_internal(self, adm_name):
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

        LOGGER.info('ADMS present for: %s', self._adms.names())
                    
    def _handle_adm(self, adm_name, timestamp, data): 
        LOGGER.info('Handling ADM: %s', adm_name)
        LOGGER.info(type(data))
        # LOGGER.info(data.tos())

        io_buffer = io.StringIO(data.tobytes().decode('utf-8'))

        self._adms.load_from_data(io_buffer)
        LOGGER.info('Handling finished')

    
# SIGNALTON transmorgifier
TRANSMORGIFIER = Transmorgifier(config)