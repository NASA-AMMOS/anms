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


from threading import *
from anms.routes.network_manager import nm_get_agents
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

logger = OpenSearchLogger(__name__).logger

config = ConfigBuilder.get_config()


class ManagerChecker:
    def __init__(self, config):
        self.known_agents = {}
        self.lock = Lock()
        self.ui_url = "http://" + config['UI_HOST'] + ":" + str(config['UI_PORT']) + config['UI_API_BASE']
        self.manager_connect = True  # tracks manager connection status so doesnt repeat alerts of disconnect
        self.curr_id = 0  # tracking the alert id for acknowledging
        self.alerts = {}  # store new alerts right now alerts for added new agents or removed agents
        self.check_list()
        # TODO switch back to daemon when pushing alerts instead of waiting for request
        # checking_child = Thread(target=self._check_list)
        # checking_child.daemon = True
        # checking_child.start()

    # TODO improvements listening to database for alerts
    # # listen to the the database for new entrys in the AgentParameterReceived table
    # @event.listens_for(AgentParameterReceived, 'after_insert')
    # def _check_parameter_received(self, _, target):
    #     process_command(target.agent_parameter_id, ast.literal_eval(target.command_parameters),
    #                     AGENT_PARAMETER.get_agent())
    def clear_alerts(self):
        self.alerts = {}

    # set visibility to false so no longer displayed
    def acknowledge(self, index):
        logger.info(f"ACK {index}")
        curr_alert = self.alerts.get(index)
        if curr_alert:
            curr_alert.update({"visible": False})
            self.alerts.update({index: curr_alert})

    def check_list(self):
        logger.info('checking agents list')

        now_know = []  # for tracking new agents
        # get the current list of agents from manager
        # if new one is added or removed then send alert

        try:
            agents = nm_get_agents()
            if agents == -1:  # counlnt connect to manager
                if self.manager_connect:
                    self.alerts[self.curr_id] = {"id": self.curr_id, "name": "manager_error", "type": "danger",
                                                 "msg": f"failed to reach manager", "visible": True}
                    self.curr_id = self.curr_id + 1
                    logger.error("could not reach nm manager")
                    self.manager_connect = False
                agents = []
            else:
                if not self.manager_connect:  # if manager was disconnected alert for reconnect
                    self.alerts[self.curr_id] = {"id": self.curr_id, "name": "manager_reconnect", "type": "info",
                                                 "msg": f"reconnected to manager", "visible": True}
                    self.curr_id = self.curr_id + 1
                    self.manager_connect = True
                agents = agents["agents"]
        except Exception:
            if self.manager_connect:
                self.alerts[self.curr_id] = {"id": self.curr_id, "name": "manager_error", "type": "danger",
                                             "msg": f"failed to reach manager", "visible": True}
                self.curr_id = self.curr_id + 1
                logger.error("could not reach nm manager")
                self.manager_connect = False
            agents = []

        # process agent list from manager
        for agent in agents:
            curr_name = agent["name"]
            now_know.append(curr_name)
            if curr_name not in self.known_agents:
                self.alerts[self.curr_id] = {"id": self.curr_id, "name": "new_agent", "type": "info",
                                             "msg": f"{curr_name} added", "visible": True}
                self.known_agents[curr_name] = agent
                self.curr_id = self.curr_id + 1

        # check if any agents were removed
        missing = self.known_agents.keys() - now_know
        for miss in missing:
            self.alerts[self.curr_id] = {"id": self.curr_id, "name": "removed_agent", "type": "warning",
                                         "msg": f"{miss} removed", "visible": True}
            self.curr_id = self.curr_id + 1
            self.known_agents.pop(miss)
    # TODO Reworks so alerts are pushed to UI server and the front end instead of frontend requesting alerts
    # send alerts to UI
    # if self.alerts:
    #     logger.info(self.alerts)
    #     url = self.ui_url + "alerts/incoming"
    #     # logger.info
    #     # logger.info(requests.put(url=url, data={"data": self.alerts}))


MANAGER_CECKER = ManagerChecker(config)
