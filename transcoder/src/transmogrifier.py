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


import configparser
import logging
import messaging

from time import sleep
from ampUri import AmpUri
from ampAriObj import AmpAriObj
from ariParameter import AriParameter
from ampAriObjParts import AmpAriObjParts
from datetime import datetime


class Transmogrifier():
    # Config has the connection properties.
    def getConfig(self):
        configParser = configparser.ConfigParser()
        configParser.read('./src/config.ini')
        config = configParser['DEFAULT']
        print(config.get('port'))
        return config

    def transcodeCoreFacing(self, client, userdata, msg):
        jsonString = msg.payload.decode('utf-8')
        logging.info("Received json from core: %s", jsonString)
        payload = AmpUri.from_json(jsonString)
        self.coreMsgs.append({'timeStamp': datetime.now(), 'msg': payload})
        # logging.info("Received message from core: %s", str(payload))
        # send message to codex
        client.publish('transcode/CodexFacing/Incoming', jsonString)
        
        # returning result for testing
        return jsonString

    def transcodeCodexFacing(self, client, userdata, msg):
        jsonString = msg.payload
        ampAriObj = AmpAriObj.from_json(jsonString)
        logging.info("Received json from codex: %s", ampAriObj.to_json())
        if(ampAriObj.BAD):
            logging.info("Translation Issue with %s", ampAriObj.inputString)
        self.codexMsgs.append({'timeStamp': datetime.now(), 'msg': ampAriObj})
        # logging.info("Received message from codex: %s", str(ampAriObj))
        # send message to core
        client.publish('transcode/CoreFacing/Incoming', ampAriObj.to_json())
        
        # returning result for testing
        return jsonString

    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)
        logging.info('Loaded Transmogrifier.')
        self.config = self.getConfig()

        self.coreMsgs = []
        self.codexMsgs = []
        
        # setting up two clients one to core one to codex
        try:
            self.transcodeCoreFacingMessenger = messaging.Messaging(
                self.config, 'transcode/CoreFacing/Outgoing', self.transcodeCoreFacing)
            self.transcodeCoreFacingMessenger.loop_start()
            self.transcodeCodexFacingMessengerOut = messaging.Messaging(
                self.config, 'transcode/CodexFacing/Outgoing', self.transcodeCodexFacing)
            self.transcodeCodexFacingMessengerOut.loop_start()
        except Exception as err:
            logging.error(err)

    def loop(self):
        while(True):
            sleep(1)
