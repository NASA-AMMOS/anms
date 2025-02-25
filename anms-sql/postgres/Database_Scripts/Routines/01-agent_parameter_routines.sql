--
-- Copyright (c) 2023 The Johns Hopkins University Applied Physics
-- Laboratory LLC.
--
-- This file is part of the Asynchronous Network Management System (ANMS).
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--     http://www.apache.org/licenses/LICENSE-2.0
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.
--
-- This work was performed for the Jet Propulsion Laboratory, California
-- Institute of Technology, sponsored by the United States Government under
-- the prime contract 80NM0018D0004 between the Caltech and NASA under
-- subcontract 1658085.
--


CREATE OR REPLACE PROCEDURE SP__add_agent_parameter_received(IN p_manager_id INTEGER, p_registered_agents_id INTEGER, p_agent_parameter_id int, p_command_parameters VARCHAR )
LANGUAGE plpgsql
as $$ BEGIN
    INSERT INTO agent_parameter_received(manager_id, registered_agents_id, agent_parameter_id, command_parameters) VALUES(p_manager_id, p_registered_agents_id, p_agent_parameter_id, p_command_parameters);
END$$;


CREATE OR REPLACE PROCEDURE SP__add_agent_parameter(IN  p_command_name VARCHAR, p_command_parameters VARCHAR )
LANGUAGE plpgsql
as $$ BEGIN
    INSERT INTO agent_parameter(command_name, command_parameters) VALUES(p_command_name, p_command_parameters);
END$$;

