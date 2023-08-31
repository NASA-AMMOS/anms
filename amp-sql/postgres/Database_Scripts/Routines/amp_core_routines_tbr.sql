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

-- STORED PROCEDURE(S) for adding updating and deleting time base rule defintions and instances 
-- need type checking for actions, they need to be Macros or controls


-- ===============================================================
-- SP__insert_tbr_actual_definition 
-- IN
-- 		p_obj_id integer - metadata id
-- 		p_use_desc varchar - human readable descriptionb
-- 		p_wait_per time  - how long to wait before starting 
-- 		p_run_count bigint - number of times to run 
-- 		p_start_time time - when to start 
-- 		p_ac_id integer - ac of the actions for this rules 
-- OUT 
-- 		r_definition_id integer - id of this tbr
-- ===============================================================


CREATE OR REPLACE PROCEDURE SP__insert_tbr_actual_definition(IN p_obj_id integer, p_use_desc varchar, 
p_wait_per time, p_run_count bigint, p_start_time time, p_ac_id integer, INOUT r_definition_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	CALL SP__insert_obj_actual_definition(p_obj_id, p_use_desc, r_definition_id); 
    INSERT INTO tbr_actual_definition(obj_actual_definition_id, wait_period, run_count, start_time, ac_id) VALUES(r_definition_id, p_wait_per, p_run_count, p_start_time, p_ac_id);
end$$;




-- ==================================================================
-- SP__delete_tbr_actual_definition;
-- Parameters:
-- in 
--      p_obj_id integer - id for the tbr to delete 
-- 		p_obj_name varchar -  name of the tbr to delete --
-- ==================================================================
 
CREATE OR REPLACE PROCEDURE SP__delete_tbr_actual_definition(IN p_obj_id integer, p_obj_name varchar)
LANGUAGE plpgsql
AS $$ 
<<tbr_def_del>>
DECLARE ac_id int;
BEGIN
	IF( p_obj_id is Null AND p_obj_name is not NULL) THEN
		select obj_id FROM obj_metadata WHERE obj_name = p_obj_name into p_obj_id;
    ELSE 
		EXIT tbr_def_del;
    END IF;
    
    IF(p_obj_name is NULL) THEN
		select obj_name from vw_tbr_formal where obj_id = p_obj_id into p_obj_name;
    END IF ;
    

	ac_id = (SELECT ac_id FROM vw_tbr_actual where obj_actual_definition = p_obj_id); 
	
    DELETE FROM ari_collection WHERE ac_id = ac_id;
	
    CALL SP__delete_obj_atual_defintion(p_obj_id, p_obj_name);
end$$;