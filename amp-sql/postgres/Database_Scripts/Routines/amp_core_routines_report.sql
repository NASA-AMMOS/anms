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


-- STORED PROCEDURE(S) for the creating updating and deleting reports and report templates


-- auto adds ac which can be troublesome 
-- user has to make ac first 
/*

CREATE OR REPLACE PROCEDURE SP__insert_report_template_metadata_format(IN p_metadata_count integer, p_metadata_types_list varchar, p_metadata_names_list varchar, p_metadata_desc varchar, INOUT r_tnvc_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	INSERT INTO type_name_value_collection(num_entries, use_desc) VALUES(p_metadata_count, p_metadata_desc) RETURNING  type_name_value_collection_id INTO r_tnvc_id;
	@s := 'INSERT INTO type_name_value(tnvc_id, data_type, data_name, order_num) VALUES'; 
    @loops := 1; 
    WHILE @loops < p_metadata_count DO 
		LANGUAGE plpgsql
AS $$ BEGIN
			-- @metadata_type
				@metadata_type := TRIM(SUBSTRING_INDEX(p_metadata_types_list, ',', 1));
				SELECT REPLACE(p_metadata_types_list, CONCAT(@metadata_type, ','), '') into p_metadata_types_list 
    
 			-- @metadata_name
				@metadata_name := TRIM(SUBSTRING_INDEX(p_metadata_names_list, ',', 1)); 
				SELECT REPLACE(p_metadata_names_list, CONCAT(@metadata_name, ','), '') into p_metadata_names_list;
                
				@s = CONCAT(@s, '(', r_tnvc_id, ',', (SELECT enum_id FROM data_type where type_name = metadata_type), ',', '\'', @metadata_name, '\'', ',', @loops, '),');
                @loops := loops + 1; 
        END; 
    END WHILE; 
 
    -- @metadata_type
	@metadata_type := TRIM((SUBSTRING_INDEX(p_metadata_types_list, ',', 1)));
    
	-- @metadata_name
	@metadata_name := TRIM(SUBSTRING_INDEX(p_metadata_names_list, ',', 1)); 

	@s = CONCAT(@s, '(', r_tnvc_id, ',', (SELECT enum_id FROM data_type where type_name = metadata_type), ',', '\'', @metadata_name, '\'', ',', @loops, ');');
	PREPARE stmt FROM @s; 
    EXECUTE stmt; 
	
end$$;
 
*/


-- ==================================================================
-- create a report template formal def
-- SP__insert_report_template_metadata_format 
-- IN 
-- 		p_obj_id integer - metadata id for this report
-- 		p_use_desc varchar - human readable use description
-- 		p_formal_parmspec_id integer - formal parameter spec id 
-- 		p_ac_id integer - ac for the report definition
-- 		 
-- OUT 
-- 		r_definition_id integer - id of this formal report 
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_report_template_formal_definition(IN p_obj_id integer, p_use_desc varchar, p_formal_parmspec_id integer, p_ac_id integer, INOUT r_definition_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	CALL SP__insert_obj_formal_definition(p_obj_id, p_use_desc, r_definition_id); 
    INSERT INTO report_template_formal_definition(obj_formal_definition_id, fp_spec_id, ac_id) VALUES(r_definition_id, p_formal_parmspec_id, p_ac_id); 
end$$;



-- ==================================================================
-- SP__insert_report_actual_definition 
-- IN 
-- 		p_obj_definition_id integer - metadata id for this report
-- 		p_ap_spec_id integer - id for the actual parmspec for this report 
-- 		p_use_desc varchar - human readable use description
-- 	OUT 
-- 		r_obj_actual_id integer - id of this actual report definition
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_report_actual_definition(IN p_obj_definition_id integer, p_ap_spec_id integer, p_ts TIMESTAMP, p_use_desc varchar, INOUT r_obj_actual_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	CALL SP__insert_obj_actual_definition(p_obj_definition_id, p_use_desc, r_obj_actual_id); 
    INSERT INTO report_template_actual_definition(obj_actual_definition_id, ap_spec_id, ts ) VALUES(r_obj_actual_id, p_ap_spec_id, p_ts);
end$$; 