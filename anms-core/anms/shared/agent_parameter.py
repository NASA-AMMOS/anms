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
import io
import json
import re
# from threading import *
from threading import Lock

from pydantic.main import BaseModel
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError, OperationalError

# from anms.routes import transcoder
import ace
from anms.models.relational import get_session
from anms.models.relational.agent_parameter import AgentParameter
from anms.routes.network_manager import nm_put_hex_eid, Data
from anms.shared.ace_runner import get_adms
from anms.shared.config_utils import ConfigBuilder
from anms.shared.opensearch_logger import OpenSearchLogger

config = ConfigBuilder.get_config()
logger = OpenSearchLogger(__name__).logger
lock = Lock()


def process_command(parameter_id, command_parameters, agent_EID, self_EID):
    if parameter_id in AGENT_PARAMETER.agent_parameters and self_EID:
        AGENT_PARAMETER.agent_parameters[parameter_id].run_action(command_parameters, agent_EID, self_EID)
        return True
    else:
        logger.error(f"Agent Parameter with id {parameter_id} not know to Handler")
        return False


class Command(BaseModel):
    command_name: str
    command_parameter: list
    command: list


class AgentParameterHandler:
    """
    Class for upadating agent_parameter table and track the commands need to preform parameter updates
        watches the database for new reqeuest and sends them to manager
        uses a JSON file to configure parameter options
        example:
    [
        {
        "name": "upd cL",
        "parameter": ["hostname", "port"],
        "command": [
          "ari:/IANA:ion_bp_admin/CTRL.outduct_add('udp','<hostname>:<port>','udpclo',UINT.0)",
          "ari:/IANA:ion_bp_admin/CTRL.outduct_start('udp','<hostname>:<port>')",
          "ari:/IANA:ion_bp_admin/CTRL.egress_plan_add('<eid>', 'udp', '<hostname>:<port>')",
          "ari:/IANA:ion_bp_admin/CTRL.egress_plan_start('<eid>')]"
        ]}
    ]
    """

    def __init__(self, config_):
        # dict that stores AgentParam for each agent_parameter_id
        self.agent_parameters = {}
        self.agent_eid = config_.get("AGENT_EID")
        self.initiated = False
        self.json_file = config_.get("AGENT_PARAMETER")
        try:
            with get_session() as db_sess:
                db_sess.execute("SELECT 1")
        except (ConnectionError, OperationalError):
            logger.error('DB not available')
            return

        try:
            self.init_json()
            self.initiated = True
        except ValueError as e:
            logger.error(f"{self.json_file} not valid json file: {e}")
        except FileNotFoundError:
            logger.error(f"{self.json_file} file not found")
        except NotADirectoryError:
            logger.error(f"{self.json_file} file not found")

    def init_json(self):
        with open(self.json_file, "r") as read_file:
            parameters = json.load(read_file)
            for parm in parameters:
                self.add_new_parameter(Command(
                    command_name=parm["name"],
                    command_parameter=parm["parameter"],
                    command=parm["command"]))

    def add_new_parameter(self, command):
        prim_id = None
        if len(command.command_parameter) > len(set(command.command_parameter)):
            logger.error(f"{command.command_name} has non unique parameter {command.command_parameter}")
            return prim_id

        parameters_list_str = ','.join(command.command_parameter)
        stmt = insert(AgentParameter).values(command_name=command.command_name,
                                             command_parameters=parameters_list_str)
        stmt2 = select(AgentParameter.agent_parameter_id).where(
            AgentParameter.command_name == command.command_name).where(
            AgentParameter.command_parameters == parameters_list_str)
        with get_session() as db_see:
            try:
                # get agent_parameter_id to use as key for agent_parameters dict
                prim_id = db_see.execute(stmt2).first()
                if prim_id:
                    logger.info(f"Agent parameter entry {command.command_name}({command.command_parameter})" +
                                " already added updating command list")
                    prim_id = prim_id[0]
                    logger.info(prim_id)
                else:
                    result = db_see.execute(stmt)
                    db_see.commit()
                    prim_id = result.inserted_primary_key[0]
                    logger.info(prim_id)
                lock.acquire()
                try:
                    self.agent_parameters[prim_id] = AgentParam(prim_id, command.command_name,
                                                                command.command_parameter,
                                                                command.command)
                finally:
                    lock.release()
            # try to insert new command and replace command list if exits
            except IntegrityError:
                db_see.rollback()
        return prim_id

    def get_agent(self):
        return self.agent_eid

    # # listen to the the database for new entrys in the AgentParameterReceived table
    # @event.listens_for(AgentParameterReceived, 'after_insert')
    # def _check_parameter_received(self, _, target):
    #     process_command(target.agent_parameter_id, ast.literal_eval(target.command_parameters),
    #                     AGENT_PARAMETER.get_agent())


class AgentParam:
    """
    class for processing individual agent parameters
    """

    def __init__(self, prim_id, name, parameters, command):
        self.id = prim_id
        self.name = name
        self.parameters = parameters
        self.command = command
        # key parameter value action translated [0x,0x ]
        self.know_parms = []
        self.know_cbor = []

    def translate(self, parameter_values):
        """
        loop through command array, formats, and tranlsates with ace
        :param parameter_values: dict of parameter name and parameter values
        :return: list of cbor encoded ari
        """
        cbors = []
        # translate each command with ACE
        for act in self.command:
            # uses < > to notate that this string is a parameter
            formatted_act = act.strip().replace("<", "{").replace(">", "}").format(**parameter_values)
            ari = ""
            try:
                dec = ace.ari_text.Decoder()
                ari = dec.decode(io.StringIO(formatted_act))
                ace.nickname.Converter(ace.nickname.Mode.TO_NN, get_adms(), True)(ari)
                enc = ace.ari_cbor.Encoder()
                buf = io.BytesIO()
                enc.encode(ari, buf)
                ari = ace.cborutil.to_hexstr(buf.getvalue())
                cbors.append(ari)
            except Exception as err:
                logger.error(f"Error encoding from {ari}: {err}")
                return [], ari, err

        # save known parameters and corresponding cbor
        lock.acquire()
        try:
            self.know_parms.append(parameter_values)
            self.know_cbor.append(cbors)
        finally:
            lock.release()
        return cbors, None, None

    def run_action(self, parameter_values, agent_EID, self_EID):
        """
        sends formatted command to agent. checks if the command was sent before if not creates a new entry for the set
        of parameter
        :param parameter_values: dict of parameter name and parameter values
        :param agent_EID: the agent to send commands to
        :param self_EID: the agent sending the command
        """
        good = True
        cbors = []
        # verify inputs are usable
        if set(parameter_values.keys()) != set(self.parameters):
            logger.error(
                f"Bad parameters for \"{self.name}\" with {parameter_values.keys()} expecting {self.parameters}")
            return

        # appending self_eid to paramteres issued may or may not actually be needed to perform command
        parameter_values_plus_self = parameter_values
        if self_EID.startswith("ipn:"):
            self_EID = re.sub(r'ipn:(.+)\..+', r'ipn:\g<1>.0', self_EID)

        parameter_values_plus_self["eid"] = self_EID
        logger.info(f"Processing parameters for \"{self.name}\" with values {parameter_values}")
        # recall if already been processed
        if parameter_values_plus_self in self.know_parms:
            cbors = self.know_cbor[self.know_parms.index(parameter_values_plus_self)]

        if not cbors:
            cbors, ari, err = self.translate(parameter_values_plus_self)

        # send hex to manager
        if cbors:
            for cbor in cbors:
                nm_put_hex_eid(agent_EID, Data(data=cbor))
            return None, None
        else:
            return ari, err


AGENT_PARAMETER = AgentParameterHandler(config)
