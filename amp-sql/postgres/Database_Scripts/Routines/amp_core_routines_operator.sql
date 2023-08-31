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

-- STORED PROCEDURE(S) for creating updating an deleting operator definitions 


-- ==================================================================
-- SP__insert_operator_actual_definition
-- IN 
-- 		p_obj_id integer - metadata id for this report
-- 		p_use_desc varchar - human readable use description
-- 		p_use_desc varchar - human readable use description
-- 		p_result_type varchar - data type of the result 
-- 		p_num_inputs integer - number of inputs for the operator 
-- 		p_tnvc_id integer -  
-- OUT 
-- 		r_definition_id integer - actual id of this operator
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_operator_actual_definition(IN p_obj_id integer, p_use_desc varchar, 
p_result_type varchar, p_num_inputs integer, p_tnvc_id integer,  INOUT r_definition_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	CALL SP__insert_obj_actual_definition(p_obj_id, p_use_desc, r_definition_id);
    INSERT INTO operator_actual_definition(obj_actual_definition_id, data_type_id, num_operands, tnvc_id)
    VALUES(r_definition_id, (SELECT data_type_id FROM data_type WHERE type_name = p_result_type), p_num_inputs, p_tnvc_id); 
end$$;


-- ==================================================================
-- SP__delete_oper_actual_defintion
-- IN 
-- 		p_obj_id integer - id of this op to delete,  
-- 		p_obj_name varchar - name of this op to delete 
-- ==================================================================
 
CREATE OR REPLACE PROCEDURE SP__delete_oper_actual_defintion(IN p_obj_id integer, p_obj_name varchar)
LANGUAGE plpgsql
AS $$ 
<<oper_def_del>>
DECLARE 
def_id int; 
fp_id int;
ac_id int;
BEGIN
	IF( p_obj_id is Null AND p_obj_name is not NULL) THEN
		select obj_id FROM obj_metadata WHERE obj_name = p_obj_name into p_obj_id;
    ELSE 
		EXIT oper_def_del;
    END IF;
    
    def_id = (select definition_id from obj_actual_definition where obj_actual_definition_id = p_obj_id);
	fp_id = (SELECT fp_spec_id from macro_actual_definition where obj_actual_definition_id = def_id );
    ac_id = (SELECT ac_id FROM macro_actual_definition where obj_actual_definition_id = def_id );
    
	DELETE FROM formal_parmspec WHERE fp_spec_id = fp_id;
	DELETE FROM ari_collection WHERE ac_id = ac_id;

	CALL SP__delete_obj_actual_defintion(p_obj_id, p_obj_name);
end$$; 
