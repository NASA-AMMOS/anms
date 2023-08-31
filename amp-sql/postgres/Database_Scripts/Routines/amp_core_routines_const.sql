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
-- Description:  inserting, updating and removing constant formal and actual definitions
-- using the obj routines
-- 
-- ==================================================================

-- ==================================================================
-- SP__insert_const_actual_definition;
-- Parameters:
-- in 
--     p_obj_id integer - id for the object metadata
--      p_use_desc varchar - humanreadable description of the constant 
-- 		p_data_type varchar -  name of the data type for the constant 
--  	p_data_value_string varchar - blob conating the encoded value of the constant 
-- out
-- 		r_actual_definition_id integer id of the actual defintion entry 
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_const_actual_definition(IN p_obj_id integer, p_use_desc varchar, p_data_type varchar, p_data_value_string varchar, INOUT r_actual_definition_id integer)
LANGUAGE plpgsql

AS $$
DECLARE data_id integer;
 BEGIN
	CALL SP__insert_obj_actual_definition(p_obj_id, p_use_desc, r_actual_definition_id); 
    SELECT data_type_id FROM data_type WHERE type_name  = p_data_type into data_id;
    INSERT INTO const_actual_definition(obj_actual_definition_id, data_type_id, data_value) VALUES(r_actual_definition_id, data_id, p_data_value_string); 
end$$;



-- ==================================================================
-- SP__delete_const_actual_definition
-- cna us either hte name or the id of the constant to delete 
-- Parameters:
-- in 
--  	p_obj_id integer -  id of the constan to delete 
-- 		p_obj_name varchar -   name of the constant to delete
-- ==================================================================

CREATE OR REPLACE PROCEDURE SP__delete_const_actual_definition(IN p_obj_id integer, p_obj_name varchar)
LANGUAGE plpgsql

AS $$ 
DECLARE
metadata_id INTEGER;
BEGIN
	IF (p_obj_id != null) THEN
		metadata_id = (SELECT obj_metadata_id FROM obj_actual_definition where obj_actual_definition_id = p_obj_id );
	ELSE
		IF (p_obj_name != NULL) THEN 
			metadata_id = (SELECT obj_metadata_id FROM obj_metadata where obj_name = p_obj_name); 
        END IF;
	END IF;
    CALL SP__delete_obj_metadata(metadata_id);
    
END$$;