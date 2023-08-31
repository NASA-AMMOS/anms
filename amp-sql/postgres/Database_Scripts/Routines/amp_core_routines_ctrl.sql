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

-- ==================================================================
-- Author: David Linko	
-- 
-- Description:  inserting, updating and removing control formal and actual definitions
-- using the obj routines
-- 
-- ==================================================================


-- ==================================================================
-- SP__insert_control_formal_definition;
-- Parameters:
-- in 
--     p_obj_id integer - id for the object metadata
--      p_use_desc varchar - humanreadable description of the constant 
-- 		p_data_type varchar -  name of the data type for the constant 
--  	p_data_value_string varchar - blob conating the encoded value of the constant 
-- out
-- 		r_actual_definition_id integer id of the actual defintion entry 
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_control_formal_definition(IN p_obj_id integer, p_use_desc varchar, p_fp_spec_id integer, INOUT r_definition_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	CALL SP__insert_obj_formal_definition(p_obj_id, p_use_desc, r_definition_id); 
    INSERT INTO control_formal_definition(obj_formal_definition_id, fp_spec_id) VALUES(r_definition_id, p_fp_spec_id);
end$$;


-- ==================================================================
-- SP__delete_control_formal_definition;
-- Parameters:
-- in 
--     p_obj_id  - id of the control to delete
--     p_obj_name - name of the control to delete 
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__delete_control_formal_definition(IN p_obj_id integer, p_obj_name varchar)
LANGUAGE plpgsql
AS $$ BEGIN
	CALL SP__delete_obj_formal_definition(p_obj_id, p_obj_name);
end$$;



-- ==================================================================
-- SP__insert_control_actual_definition;
-- Parameters:
-- in 
--     p_obj_id integer - id for the object metadata
--      p_use_desc varchar - humanreadable description of the constant 
-- 		p_data_type varchar -  name of the data type for the constant 
--  	p_data_value_string varchar - blob conating the encoded value of the constant 
-- out
-- 		r_actual_definition_id integer id of the actual defintion entry 
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_control_actual_definition(IN p_obj_definition_id integer, p_ap_spec_id integer, p_use_desc varchar, INOUT r_instance_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	CALL SP__insert_obj_actual_definition(p_obj_definition_id, p_use_desc, r_instance_id);

    -- TODO: Skip insert if it has no parameters
    INSERT INTO control_actual_definition(obj_actual_definition_id, ap_spec_id) VALUES(r_instance_id, p_ap_spec_id);  
end$$; 
 


-- ==================================================================
-- SP__delete_control_actual_definition;
-- Parameters:
-- in 
--     p_obj_id integer - actual_definiton id of the control that is to be deleted
--     p_obj_name varchar- name of the control to delete, this allows to delete all the actual definitons 
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__delete_control_actual_definition(IN p_obj_id integer, p_obj_name varchar)
LANGUAGE plpgsql

AS $$ <<ctrl_actual_definition_del>> 
	
	DECLARE done INT DEFAULT FALSE;
    DECLARE actual_definition_id_hold integer; 
	DECLARE ap_spec_id_hold integer;
    DECLARE actual_definition_cursor CURSOR
			FOR SELECT actual_definition_id, ap_spec_id FROM vw_ctrl_actual_definition WHERE obj_name = p_obj_name;
	-- DECLARE CONTINUE HANDLER FOR NOT FOUND SET done := TRUE;	
    DECLARE ap_id integer; 
	BEGIN
	
    -- only one thing to remove 
	If( p_inst_id is not null) then 
		ap_id = (SELECT ap_spec_id from ctrl_actual_definition where actual_definition_id = p_inst_id );
		IF( ap_id is not null) THEN
			DELETE FROM actual_parmspec WHERE ap_spec_id = ap_id;
		END IF;
		DELETE FROM ctrl_actual_definition 
WHERE
    intance_id = p_actual_definition_id;
		CALL SP__delete_obj_actual_definition(p_actual_definition_id, p_obj_name);
	ELSE -- removing all instances with this name 
		IF( p_obj_name is null) then -- nothing to do 
			exit ctrl_actual_definition_del;
		END IF;
		OPEN actual_definition_cursor;
        <<read_loop>> LOOP
			FETCH NEXT FROM actual_definition_cursor INTO 
				actual_definition_id_hold, ap_spec_id_hold;
			IF done THEN
				exit read_loop;
			END IF;

			DELETE FROM actual_parmspec WHERE ap_spec_id = ap_spec_id_hold;

			DELETE FROM ctrl_actual_definition
WHERE
    ctrl_actual_definition.actual_definition_id = actual_definition_id_hold;			
		END LOOP;
        CALL SP__delete_obj_actual_definition(null, p_obj_name);
    end if;
    CLOSE actual_definition_cursor;
END$$;