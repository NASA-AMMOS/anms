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
from paho import mqtt
from anms.models.relational import get_session
from anms.models.relational.transcoder_log import TranscoderLog
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger
import json
from threading import *
import time

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger


class MQTTClient:
    def __init__(self, config):
        host = config.get('MQTT_HOST')
        port = config.get('MQTT_PORT')
        if not host:
            self.client = None
            return

        # Create MQTT Client
        client = mqtt.client.Client("Core_MQTT_Client", clean_session=False)
        client.on_connect = self._on_connect
        client.on_message = self._on_message
        logger.info('Connecting to MQTT broker at %s:%s', host, port)
        client.connect_async(host, port, keepalive=60)
        self.client = client
        checking_child = Thread(target=self._check_pending)
        checking_child.daemon = True
        checking_child.start()
        client.loop_start()

    def publish(self, *args, **kwargs):
        ''' If connected, pass through a publish request. '''
        if not self.client:
            logger.waring('MQTT client is not connected, skipping publish')
            return
        return self.client.publish(*args, **kwargs)

    def _on_message(self, client, userdata, msg):
        ''' when core gets update its entry in the transcoder table '''
        json_string = msg.payload.decode('utf-8')
        logger.info("Received json from Transcoder: %s", json_string)
        jsonified = json.loads(json_string)

        # store in transcoder database
        with get_session() as session:
            session.query(TranscoderLog).filter(TranscoderLog.input_string == jsonified['inputString']). \
                update({
                    'parsed_as': jsonified['parsedAs'],
                    'ari': json.dumps(jsonified['ari']),
                    'cbor': jsonified['cbor'],
                    'uri':  jsonified['uri']
                })
            session.commit()

    def _on_connect(self, client, userdata, flags, rc):
        ''' The callback for when the client connects to the broker '''
        if rc != 0:
            logger.info(
                "Failed to connected with result code %s", rc
            )  # Print result of connection attempt
        self.client.subscribe("transcode/CoreFacing/Incoming")

    def _check_pending(self):
        ''' Within a work thread, every minute check the transcoder
        table for ari labeled as pending and resend.
        '''
        while True:
            logger.info('Checking transcoder table')
            pending_uris = TranscoderLog.query.filter_by(parsed_as='pending').all()

            for entrys in pending_uris:
                try:
                    self._send_pending(entrys)
                except Exception as err:
                    logger.error('Failed to process pending entry: %s', err)
            time.sleep(90)

    def _send_pending(self, entrys):
        msg = {"uri": entrys.input_string}
        logger.info('REPUBLISH to transcode/CoreFacing/Outgoing, msg = %s' % msg)
        self.publish("transcode/CoreFacing/Outgoing", json.dumps(msg))


# Singleton global instance
MQTT_CLIENT = MQTTClient(config)
