--
-- Copyright (c) 2023 The Johns Hopkins University Applied Physics
-- Laboratory LLC.
--
-- This file is part of the Asynchronous Network Managment System (ANMS).
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

-- create messages 

-- ==================================================================
-- SP__insert_outgoing_message_set
-- IN 
-- 		p_created_ts integer - created timestamp
-- 		p_modified_ts integer - modified timestamp
-- 		p_state integer - state of the message set 
-- 		p_agent_id integer - agent of this message 
-- OUT 
-- 		r_set_id integer - id of the set
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_outgoing_message_set(IN p_created_ts timestamp,
p_modified_ts timestamp, p_state integer, p_agent_id integer, INOUT r_set_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
INSERT INTO outgoing_message_set (created_ts, modified_ts, state, agent_id)
VALUES (p_created_ts, p_modified_ts, p_state, p_agent_id) RETURNING eated_ts_id INTO r_set_id;
END$$;



-- ==================================================================
-- SP__insert_outgoing_message_entry
-- IN 
-- 		p_set_id integer - id of the outgoing message set this entry belongs toß
--      p_message_order integer - order of this message in the set
--      p_start_ts integer - start time 
--      p_ac_id integer - ac of this message 
-- OUT 
--      r_message_id integer - id of this message
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_outgoing_message_entry(IN p_set_id integer, p_message_order integer, p_start_ts timestamp, p_ac_id integer, INOUT r_message_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
INSERT INTO outgoing_message_entry (set_id, message_order, start_ts, ac_id)
VALUES (p_set_id, p_message_order, p_start_ts, p_ac_id) RETURNING outgoing_message_entry_id INTO r_message_id;
END$$;



-- ==================================================================
-- SP__update_outgoing_message_set
-- IN 
-- 		p_set_id integer - id of the set to update 
-- 		p_state integer - state of the message set 
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__update_outgoing_message_set(IN p_set_id integer, p_state integer)
LANGUAGE plpgsql
AS $$ BEGIN
	
	UPDATE outgoing_message_set
	SET
	modified_ts = NOW(),
	state = p_state
	WHERE set_id = p_set_id;
END$$;



-- ==================================================================
-- SP__insert_incoming_message_set
-- IN 
-- 		p_created_ts integer - created timestamp
-- 		p_modified_ts integer - modified timestamp
-- 		p_state integer - state of the message set 
-- 		p_agent_id integer - agent of this message 
-- OUT 
-- 		r_set_id integer - id of the set
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_incoming_message_set(IN p_created_ts timestamp,
p_modified_ts timestamp, p_state integer, p_agent_id integer, INOUT r_set_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
INSERT INTO incoming_message_set (created_ts, modified_ts, state, agent_id)
VALUES (p_created_ts, p_modified_ts, p_state, p_agent_id) RETURNING eated_ts_id INTO r_set_id;
END$$;


-- ==================================================================
-- SP__insert_incoming_message_entry
-- IN 
-- 		p_set_id integer - id of the outgoing message set this entry belongs toß
--      p_message_order integer - order of this message in the set
--      p_start_ts integer - start time 
--      p_ac_id integer - ac of this message 
-- OUT 
--      r_message_id integer - id of this message
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_incoming_message_entry(IN p_set_id integer, p_message_order integer, p_start_ts timestamp, p_ac_id integer, INOUT r_message_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
INSERT INTO incoming_message_entry (set_id, message_order, start_ts, ac_id)
VALUES (p_set_id, p_message_order, p_start_ts, p_ac_id) RETURNING incoming_message_entry_id INTO r_message_id;
END$$;



-- ==================================================================
-- SP__update_incoming_message_set
-- IN 
-- 		p_set_id integer - id of the set to update 
-- 		p_state integer - state of the message set 
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__update_incoming_message_set(IN p_set_id integer, p_state integer)
LANGUAGE plpgsql
AS $$ BEGIN
	
	UPDATE incoming_message_set
	SET
	modified_ts = NOW(),
	state = p_state
	WHERE set_id = p_set_id;
END$$;



-- SP__insert_message_report_entry(message_id, order_num, ari_id, tnvc_id, ts)


CREATE OR REPLACE PROCEDURE SP__insert_message_report_entry(IN
       p_msg_id integer,
       p_order_num integer,
       p_ari_id integer,
       p_tnvc_id integer,
       p_ts integer,
       INOUT r_obj_id integer
       )
LANGUAGE plpgsql
AS $$ BEGIN

    INSERT INTO report_definition (ari_id, ts, tnvc_id) VALUES (p_ari_id, p_ts, p_tnvc_id) RETURNING report_id INTO r_obj_id;

    IF p_order_num IS NULL THEN
       SELECT order_num+1 INTO p_order_num FROM message_report_set_entry WHERE message_id=p_msg_id ORDER BY order_num DESC LIMIT 1;
    END IF;
    IF p_order_num IS NULL THEN
       p_order_num = 0;
    END IF; 

    INSERT INTO message_report_set_entry (message_id, report_id, order_num) VALUES (p_msg_id, r_obj_id, p_order_num);
    
end$$;


-- SP__insert_message_group_agent_id(group_id, agent_id )


CREATE OR REPLACE PROCEDURE SP__insert_message_group_agent_id(IN
       p_group_id integer,
       p_agent integer,
       INOUT r_obj_id integer
       )
LANGUAGE plpgsql
AS $$ BEGIN
        INSERT INTO message_group_agents (group_id, agent_id) VALUES (p_group_id, p_agent) RETURNING message_group_agents_id INTO r_obj_id;
end$$;


-- SP__insert_message_group_agent_name(group_id, agent_name)


CREATE OR REPLACE PROCEDURE SP__insert_message_group_agent_name(IN
       p_group_id integer,
       p_agent VARCHAR(128),
       INOUT r_obj_id integer
       )
LANGUAGE plpgsql
AS $$ DECLARE eid INT;   BEGIN
        
        CALL SP__insert_agent(p_agent, eid); -- Select or Insert Agent ID
        INSERT INTO message_group_agents (group_id, agent_id) VALUES (p_group_id, eid) RETURNING message_group_agents_id INTO r_obj_id;

end$$;


-- SP__insert_message_entry_agent( message_id, agent_name )


CREATE OR REPLACE PROCEDURE SP__insert_message_entry_agent(IN
       p_mid integer,
       p_agent VARCHAR(128)
       )
LANGUAGE plpgsql
AS $$ DECLARE eid INT;  BEGIN
        
        CALL SP__insert_agent(p_agent, eid); -- Select or Insert Agent ID
        INSERT INTO message_agents (message_id, agent_id) VALUES (p_mid, eid);

end$$;