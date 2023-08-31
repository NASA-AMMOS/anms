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

-- STORED PROCEDURE(S) for adding updating and removing variables 

-- ==================================================================
-- SP__insert_variable_definition 
-- inserting a new variable 
-- IN 
-- 		p_obj_id integer - metadata id of the variable
-- 		p_use_desc varchar - human readable description 
-- 		p_out_type integer - out type of the variable
-- 		p_num_operators integer - number of operators 
-- 		p_operator_ids_list varchar - 
-- OUT 
-- 		r_definition_id integer - definition id of the variable
--
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_variable_definition(IN p_obj_id integer, p_use_desc varchar, 
p_out_type integer,  p_expression_id integer, INOUT r_definition_id integer)
LANGUAGE plpgsql
AS $$ 
DECLARE 
r_expr_id int;
BEGIN 
	CALL SP__insert_obj_actual_definition(p_obj_id, p_use_desc, r_definition_id);
	-- call expresion builder for var Initializer
    CALL SP__insert_expression(p_out_type, p_expression_id, r_expr_id);
	INSERT INTO variable_actual_definition(obj_actual_definition_id, data_type_id, expression_id) VALUES(r_definition_id, p_out_type, r_expr_id); 

end$$;



-- ==================================================================
-- SP__delete_var_actual_definition;
-- Parameters:
-- in 
--      p_obj_id integer - id for the var to delete 
-- 		p_obj_name varchar -  name of the var to delete --
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__delete_variable_definition(IN p_definition_id integer, p_obj_name varchar)
LANGUAGE plpgsql
AS $$
DECLARE
exp_id int;
 BEGIN
	-- delete the expresion first
    exp_id = (SELECT expression_id from variable_actual_definition where p_definition_id = obj_actual_definition);
    CALL SP__delete_expression(exp_id);
    CALL SP__delete_obj_actual_definition(p_obj_id, p_use_desc, r_definition_id);
	
end$$;