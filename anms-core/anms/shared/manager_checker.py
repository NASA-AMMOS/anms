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

import io
import json
import requests
from threading import Lock

from anms.models.relational import nm_url
from anms.shared import alerts
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

logger = OpenSearchLogger(__name__).logger

config = ConfigBuilder.get_config()


class ManagerChecker:
    def __init__(self, config):
        self.known_agents = {}
        self.lock = Lock()
        self.alert_file = io.StringIO()
        self.ui_url = "http://" + config['UI_HOST'] + ":" + str(config['UI_PORT']) + config['UI_API_BASE']
        self.manager_connect = True  # tracks manager connection status so doesnt repeat alerts of disconnect
        self.curr_id = 0  # tracking the alert id for acknowledging
        self.alerts = {}  # store new alerts right now alerts for added new agents or removed agents
    
    # TODO improvements listening to database for alerts
    def clear_alerts(self):
        self.alerts = {}

    # set visibility to false so no longer displayed
    def acknowledge(self, index):
        with self.lock:
            try:
                curr_alert = None
                with open(self.alert_file, 'r') as f:
                    alerts = json.load(f)
                curr_alert = alerts.get(str(index))
                if curr_alert:
                    logger.info(f"ACK {index}")
                    curr_alert["visible"]= False
                    alerts[str(index)] = curr_alert
                with open(self.alert_file, 'w') as f:
                    json.dump(alerts, f)
            except (FileNotFoundError, json.JSONDecodeError):
                logger.error("ERROR reading alert.json")
                
    def get_alerts(self):
        data = {}
        with self.lock:
            try:
                with open(self.alert_file, 'r') as f:
                    data = json.load(f)
                return data 
            except Exception as e:
                logger.error(e)
        return data

    async def check_list(self):
        now_know = []  # for tracking new agents
        # get the current list of agents from manager
        # if new one is added or removed then send alert
        curr_alerts = self.get_alerts()
        with self.lock:
            try:
                # TODO enhancement compare manager known agents vs database known agents 
                logger.info('checking agents list')
                url = nm_url + "/agents"
                response = requests.get(url)
                if not response.ok:
                    raise RuntimeError('no valid resonse')

                if not self.manager_connect:  # if manager was disconnected alert for reconnect
                    curr_alerts[self.curr_id] = {"id": self.curr_id, "name": "manager_reconnect", "type": "info",
                                                "msg": "reconnected to manager", "visible": True}
                    await alerts.store_alert("manager_reconnect", "20", "reconnected to manager")
                    self.curr_id = self.curr_id + 1
                    self.manager_connect = True
                agents = agents["agents"]

            except Exception as e:
                if self.manager_connect:
                    curr_alerts[self.curr_id] = {"id": self.curr_id, "name": "manager_error", "type": "danger",
                                                "msg": "failed to reach manager", "visible": True}
                    await alerts.store_alert("manager_error", "40", "failed to reach manager")
                    self.curr_id = self.curr_id + 1
                    logger.error("could not reach nm manager")
                    self.manager_connect = False
                logger.error(f"{e} while getting agents")
                agents = []

            # process agent list from manager
            for agent in agents:
                curr_name = agent["name"]
                now_know.append(curr_name)
                if curr_name not in self.known_agents:
                    curr_alerts[self.curr_id] = {"id": self.curr_id, "name": "new_agent", "type": "info",
                                                "msg": f"{curr_name} added", "visible": True}
                    await alerts.store_alert("new_agent", "20", f"{curr_name} added")
                    self.known_agents[curr_name] = agent
                    self.curr_id = self.curr_id + 1

            # check if any agents were removed
            missing = self.known_agents.keys() - now_know
            for miss in missing:
                # write new entry into DB
                curr_alerts[self.curr_id] = {"id": self.curr_id, "name": "removed_agent", "type": "warning",
                                            "msg": f"{miss} removed", "visible": True}
                await alerts.store_alert("removed_agent", "30", f"{miss} removed")
                self.curr_id = self.curr_id + 1
                self.known_agents.pop(miss)


MANAGER_CHECKER = ManagerChecker(config)
