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
''' Main entrypoint
'''
import argparse
import logging
import io
import json
import sys
import sqlalchemy
from sqlalchemy.orm import Session
import traceback
import paho.mqtt.client as mqtt
import ace
from ace import cborutil


LOGGER = logging.getLogger(__name__)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', choices=('debug', 'info', 'warning', 'error'),
                        default='info',
                        help='The minimum log severity.')
    parser.add_argument('--mqtt-host', required=True)
    parser.add_argument('--db-uri', required=True)
    return parser


class Executive:
    ''' The executive containing the main event loop and DB connections. '''
    def __init__(self, args):
        client = mqtt.Client()
        client.on_connect = self._on_connect
        self._client = client
        LOGGER.info('Connecting to MQTT broker at %s', args.mqtt_host)
        self._client.connect_async(args.mqtt_host, port=1883, keepalive=60)

        LOGGER.info('Connecting to SQL DB at %s', args.db_uri)
        self._dbeng = sqlalchemy.create_engine(args.db_uri)

        self._adms = ace.AdmSet(cache_dir=False)

    def run(self):
        ''' Run the event loop. '''
        self._client.loop_forever()

    def _on_connect(self, client, userdata, flags, rc):
        LOGGER.info('MQTT connected')
        # Subscribe to topics
        topic = 'aricodec/reload'
        client.message_callback_add(topic, self._on_msg_reload)
        client.subscribe(topic)
        topic = 'transcode/CodexFacing/Incoming'
        client.message_callback_add(topic, self._on_ari_in)
        client.subscribe(topic)
        # Initial state load
        self._adm_reload(None)

    def _on_msg_reload(self, client, userdata, msg):
        adm_name = msg.payload
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
    INNER JOIN data_model ON adm_data.enumeration = data_model.enumeration
WHERE adm_name = ?
''', [adm_name])
                for row in curs.all():
                    self._handle_adm(*row)

            else:
                LOGGER.info('Reloading all ADMS...')

                curs = db_conn.execute('''\
SELECT data_model.name, adm_data.updated_at, adm_data.data
FROM adm_data 
    INNER JOIN data_model ON adm_data.enumeration = data_model.enumeration
''')
                for row in curs.all():
                    self._handle_adm(*row)

        LOGGER.info('ADMS present for: %s', self._adms.names())
                    
    def _handle_adm(self, adm_name, timestamp, data):
        LOGGER.info('Handling ADM: %s', adm_name)
        self._adms.load_from_data(io.BytesIO(data))
        LOGGER.info('Handling finished')

    def _on_ari_in(self, client, userdata, msg):
        # result object to fill in
        res_obj = {}
        res_obj['uri'] = ""
        res_obj['cbor'] = ""
        
        try:
            req_obj = json.loads(msg.payload)
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
                    in_bytes = cborutil.from_hexstr(in_text)

                    dec = ace.ari_cbor.Decoder()
                    ari = dec.decode(io.BytesIO(in_bytes))
                    LOGGER.debug('as ARI %s', ari)
                    ace.nickname.Converter(ace.nickname.Mode.FROM_NN, self._adms, True)(ari)
                except Exception as err:
                    raise RuntimeError(f"Error decoding from `{in_text}`: {err}") from err
                res_obj['cbor'] = in_text
                res_obj['ari'] = {}

                try:
                    enc = ace.ari_text.Encoder()
                    buf = io.StringIO()
                    enc.encode(ari, buf)

                    out_text = buf.getvalue()
                    if not out_text.startswith('ari:'):
                        out_text = 'ari:' + out_text
                    LOGGER.debug('as text %s', out_text)
                except Exception as err:
                    raise RuntimeError(f"Error encoding from {ari}: {err}") from err
                res_obj['uri'] = out_text

            else:
                # Text-to-binary mode
                res_obj['parsedAs'] = 'URI'
                
                try:
                    dec = ace.ari_text.Decoder()
                    ari = dec.decode(io.StringIO(in_text))
                    LOGGER.debug('as ARI %s', ari)
                    ace.nickname.Converter(ace.nickname.Mode.TO_NN, self._adms, True)(ari)
                except Exception as err:
                    raise RuntimeError(f"Error decoding from `{in_text}`: {err}") from err
                res_obj['uri'] = in_text
                res_obj['ari'] = {}

                try:
                    enc = ace.ari_cbor.Encoder()
                    buf = io.BytesIO()
                    enc.encode(ari, buf)

                    hex_str = cborutil.to_hexstr(buf.getvalue())
                    LOGGER.debug('as binary %s', hex_str)
                except Exception as err:
                    raise RuntimeError(f"Error encoding from {ari}: {err}") from err
                res_obj['cbor'] = hex_str

        except Exception as err:
            res_obj['ari'] = f'Failed to process: {err}'
            LOGGER.error('Failed to process: %s', err)
            LOGGER.info('Traceback:\n%s', traceback.format_exc())

        LOGGER.info('Response %s', res_obj)
        client.publish('transcode/CodexFacing/Outgoing', json.dumps(res_obj))


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())
    sys.exit(Executive(args).run())
