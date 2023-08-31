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
import paho.mqtt.client as mqtt
import logging

class Messaging:
    """ This is a wrapper for the mqtt client. """
    
    def __init__(self, config, subscription = None, on_message = None, clientId = None):
        global on_connect
        self.config = config
        defaultHost = 'mqtt-broker'

        if (clientId):
            self.client = mqtt.Client(clientId)
        else:
            self.client = mqtt.Client()

        self.client.enable_logger()
        self.client.on_connect = on_connect

        if (subscription):
            self.client.user_data_set(subscription)
            self.subscribe(subscription)

        if (on_message):
            self.client.on_message = on_message

        username = config.get('username', None)
        password = config.get('password', None)

        if username is not None:
            self.client.username_pw_set(username, password)
            
        
        port = config.get('port', '1883')
        if port.isnumeric():
            port = int(port)
        else:
            port = 1883

        host = config.get('host', defaultHost)
        if host == '':
            host = defaultHost 
        
        logging.basicConfig(level=logging.INFO)
        logging.info("Host: "+ host + " port: "+ str(port))
        

        if host is None:
            raise Exception("Host must be defined in the config file or in the servers section.")
        try:
            self.client.connect(host, port)
        except Exception as err:
            logging.error(err)
            logging.error("FAILED TO Connect to MQTT host {}:{}".format(host,port))
            raise Exception("FAILED TO Connect to MQTT host {}:{}".format(host,port))
            
    def publish(self, topic, payload, qos = 0, retain = False):
        self.client.publish(topic, payload, qos, retain)

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def loop_forever(self):
        self.client.loop_forever()

    def loop_start(self):
        self.client.loop_start()

def on_connect(client, userdata, flags, rc):
    if (userdata):
        client.subscribe(userdata)

