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

-- STORED PROCEDURE(S) for the formal parameters specefications. Stores type name information. 


-- ==================================================================
-- SP__insert_formal_parmspec
-- inserts a new formal parmspec in the db
-- IN 
-- 		p_num_parms integer - number if parms in the spec
-- 		p_use_desc varchar - human readable describtion
-- OUT 
-- 		r_fp_spec_id integer -  the id of the spec 
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_formal_parmspec(IN p_num_parms integer, p_use_desc varchar,  INOUT r_fp_spec_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	INSERT INTO formal_parmspec(num_parms, use_desc) VALUES(p_num_parms, p_use_desc) RETURNING  fp_spec_id INTO r_fp_spec_id;
end$$;




-- ==================================================================
-- SP__insert_formal_parmspec_entry
-- insert a single entry into a formal parm
-- IN 
--      p_fp_spec_id integer - id of the formal parmspec for this entry    
--      p_order_num integer - order of the entry in the parmspec
--      p_parm_name varchar - name of the parm used for parm by name 
--      p_data_type varchar - data type of the parm
--      p_obj_definition_id integer -  optional default value of this parm
-- OUT 
--      r_fp_id integer
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_formal_parmspec_entry(IN p_fp_spec_id integer,  p_order_num integer, p_parm_name varchar, p_data_type varchar, p_obj_definition_id integer, INOUT r_fp_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	INSERT INTO formal_parm
(
fp_spec_id,
order_num,
parm_name,
data_type_id,
obj_actual_definition_id)
VALUES
(p_fp_spec_id,
p_order_num,
p_parm_name,
(select data_type_id from data_type where type_name = p_data_type),
p_obj_definition_id) RETURNING fp_id INTO r_fp_id;
end$$;




-- ==================================================================
-- SP__insert_formal_parmspec
-- inserts a list of formal parms into a spec, uses three ',' delimenated lists to 
-- store type name and default value info for the formal parms
-- IN 
-- 		p_num_parms integer - number of parms in the parmspec
-- 		p_use_desc varchar - human readable description
-- 		p_data_types_list varchar(10000 ) - list of types for the parms 
-- 		p_parm_names_list varchar(10000) - list of the names for the parms
-- 		p_default_values_list varchar(10000) - list of the default values
-- OUT 
-- 		r_fp_spec_id integer - formal parmspec id
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_formal_parms_set(IN p_num_parms integer, p_use_desc varchar, p_data_types_list varchar(10000), p_parm_names_list varchar(10000),
 p_default_values_list varchar(10000), INOUT r_fp_spec_id integer)
LANGUAGE plpgsql
AS $$ 
DECLARE
fp_spec_id int;
s varchar;
loops int;
data_type varchar;
parm_name varchar;
default_value varchar;
BEGIN 
	CALL SP__insert_formal_parmspec(p_num_parms, p_use_desc, r_fp_spec_id); 
    fp_spec_id := r_fp_spec_id; 
    s := 'INSERT INTO formal_parm(fp_spec_id, order_num, parm_name, data_type_id, obj_actual_definition_id) VALUES'; 
    loops := 1; 
    WHILE loops < p_num_parms DO  LOOP 
			-- @data_type
				data_type := TRIM(SUBSTRING_INDEX(p_data_types_list, ',', 1));
			    SELECT REPLACE(p_data_types_list, CONCAT(data_type, ','), '') into p_data_types_list ;
    
 			-- parm_name
				parm_name := TRIM(SUBSTRING_INDEX(p_parm_names_list, ',', 1)); 
				SELECT REPLACE(p_parm_names_list, CONCAT(parm_name, ','), '') into p_parm_names_list;
                
            -- @default_value
				default_value := TRIM(SUBSTRING_INDEX(p_default_values_list, ',', 1));
                IF default_value = 'NULL' THEN default_value := null;
                ELSEIF default_value = 'null' THEN default_value := null;
				END IF;
                SELECT REPLACE(p_default_values_list, CONCAT(default_value, ','), '') into p_default_values_list;
            
				s = CONCAT(s, '(', fp_spec_id, ',', loops, ',', '"', parm_name, '"', ',', (SELECT data_type_id FROM data_type where type_name = data_type), ',', '"', default_value, '"', '),');
                loops := loops + 1; 
        END loop; 
 
    -- @data_type
	data_type := TRIM((SUBSTRING_INDEX(p_data_types_list, ',', 1)));
    
	-- parm_name
	parm_name := TRIM(SUBSTRING_INDEX(p_parm_names_list, ',', 1)); 
                
	-- default_value
	IF default_value = 'NULL' THEN default_value := null;
                ELSEIF default_value = 'null' THEN default_value := null;
				END IF;
                SELECT REPLACE(p_default_values_list, CONCAT(default_value, ','), '') into p_default_values_list;

	s = CONCAT(s, '(', fp_spec_id, ',', loops, ',', (SELECT data_type_id FROM data_type where type_name = data_type), ',', '"', parm_name, '"', ',', '"', default_value, '"', ')');
	-- PREPARE stmt as s; 
    EXECUTE s; 

end$$;