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


-- STORED PROCEDURE(S) for creating literals 
-- need to update to allow ot be ari


-- ==================================================================
-- SP__insert_literal_actual_definition 
-- IN 
-- 		p_obj_id integer - id of the metadata info 
-- 		p_use_desc varchar - human readable describtion
-- 		p_data_type varchar - primitive data type of the literal
-- 		p_data_value_string varchar - calue of the literal encoded as a string 
-- OUT 
-- 		r_definition_id integer - id of teh literal
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_literal_actual_definition(IN p_obj_id integer, p_use_desc varchar, p_data_type varchar, p_data_value_string varchar, INOUT r_definition_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	CALL SP__insert_obj_actual_definition(p_obj_id, p_use_desc, r_definition_id); 
    INSERT INTO literal_actual_definition(obj_actual_definition_id, data_type_id, data_value) VALUES(r_definition_id, (SELECT data_type_id FROM data_type WHERE type_name  = p_data_type), p_data_value_string); 
end$$;



-- ==================================================================
-- SP__delete_literal_actual_definition 
-- IN 
-- p_obj_id integer - id of the lit to be deleted
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__delete_literal_actual_definition(IN p_obj_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	CALL SP__delete_obj_definition(p_obj_id); 
end$$;