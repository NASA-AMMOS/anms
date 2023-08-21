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

from io import StringIO
import io
import json
import logging
from pickle import TRUE
import time
from ampAriObj import AmpAriObj
from ampUri import AmpUri
import transmogrifier

import pytest



def load_json():
    f = open('./inputs.JSON')
    data = json.load(f)
    return data


def test_transcoder_from_cbor(caplog):
    caplog.set_level('INFO')
    data = load_json()
    results = []
    logging.basicConfig(level=logging.INFO)
    logging.info("%s",'Start of Test!')
    tm = transmogrifier.Transmogrifier()

    #  send and collect messages
    for d in data:
        if "comment" in d:# skipping commented test
            continue
        payload = AmpUri(d['cbor'])
        payloadJson = payload.to_json()
        tm.transcodeCoreFacingMessenger.publish(
            'transcode/CoreFacing/Outgoing', payloadJson)
        # while(not tm.codexMsgs):
        #     time.sleep(1)
        time.sleep(1)

    while(caplog.records != []):
        time.sleep(1)
        currLog = caplog.records.pop()
        
        if "json from codex" in currLog.msg:
            codexJson = json.loads(currLog.args[0])
            print(codexJson)
            for d in data:
                if "comment" in d : # skipping commented test
                    continue
                if d['cbor'] == codexJson['inputString']:
                    assert d['uri'] == codexJson['uri']

def test_transcoder_from_uri(caplog):
    caplog.set_level('INFO')
    data = load_json()
    results = []
    logging.basicConfig(level=logging.INFO)
    logging.info("%s",'Start of Test!')
    tm = transmogrifier.Transmogrifier()

    #  send and collect messages
    for d in data:
        if "comment" in d or d['skipUri']: # skipping commented test
            continue
        payload = AmpUri(d['uri'])
        payloadJson = payload.to_json()
        tm.transcodeCoreFacingMessenger.publish(
            'transcode/CoreFacing/Outgoing', payloadJson)
        # while(not tm.codexMsgs):
        #     time.sleep(1)
        time.sleep(1)

    while(caplog.records != []):
        time.sleep(1)
        currLog = caplog.records.pop()
        
        if "json from codex" in currLog.msg:
            codexJson = json.loads(currLog.args[0])
           
            for d in data:
                if "comment" in d: # skipping commented test
                    continue
                if d['uri'] == codexJson['inputString']:
                    print(codexJson['cbor'] + " " + d['cbor'])
                    assert d['cbor'] == "ari:"+codexJson['cbor']
