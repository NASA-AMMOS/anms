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

-- STORED PROCEDURE(S) for the actaul parameters specefications and actual parameter sets. has real data 


-- ==================================================================
-- SP__insert_actual_parmspec
--  inserting an actual parmspec into db
-- IN 
-- 		p_fp_spec_id integer - the id of the formal parm spec for this actual parmspec
-- 		p_tnvc_id integer - TNVC corresponding to actual parameter definition
-- 		p_use_desc varchar - human readable describtion
-- OUT 
-- 		r_ap_spec_id integer - id of the parmspec in the db 
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_actual_parmspec_tnvc(IN p_fp_spec_id integer, p_tnvc_id integer, p_use_desc varchar, INOUT r_ap_spec_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	INSERT INTO actual_parmspec(fp_spec_id, tnvc_id, use_desc) VALUES(p_fp_spec_id, p_tnvc_id, p_use_desc) RETURNING  ap_spec_id INTO r_ap_spec_id;
end$$;


-- ==================================================================
-- SP__insert_actual_parmspec
--  inserting an actual parmspec into db
-- IN 
-- 		p_fp_spec_id integer - the id of the formal parm spec for this actual parmspec
-- 		p_num_parms integer - number of parms 
-- 		p_use_desc varchar - human readable describtion
-- OUT 
-- 		r_ap_spec_id integer - id of the parmspec in the db 
-- ==================================================================
-- TODO: p_num_parms argument is deprecated and will be removed

CREATE OR REPLACE PROCEDURE SP__insert_actual_parmspec(IN p_fp_spec_id integer, p_num_parms integer, p_use_desc varchar, INOUT r_ap_spec_id integer)
LANGUAGE plpgsql
AS $$
DECLARE tnvc_id INT;
 BEGIN
    
    CALL SP__insert_tnvc_collection(p_use_desc, tnvc_id);
    CALL SP__insert_actual_parmspec_tnvc(p_fp_spec_id, tnvc_id, p_use_desc, r_ap_spec_id);
end$$;


-- ==================================================================
-- SP__insert_actual_parms_object
--  inserting an actual parm object into spec
-- IN 
-- 		p_ap_spec_id integer -  id of the spec this object is being added 
-- 		p_order_num integer -  order number
-- 		p_data_type_id integer - the id of the datatype in the data type table
-- 		p_obj_actual_definition integer - id of the object for the parm
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_actual_parms_object(IN p_ap_spec_id integer, p_order_num integer, p_data_type_id varchar , p_obj_actual_definition integer)
LANGUAGE plpgsql
AS $$
DECLARE 
ap_tnvc_id int;
r_tnvc_entry_id INT;
 BEGIN
    
    SELECT tnvc_id INTO ap_tnvc_id FROM actual_parmspec WHERE ap_spec_id = p_ap_spec_id;


    CALL SP__insert_tnvc_obj_entry(ap_tnvc_id, p_order_num, p_data_type_id, p_obj_actual_definition, r_tnvc_entry_id);



end$$;


-- ==================================================================
-- SP__insert_actual_parms_names
--  inserting an actual parm reference by name into spec. This parm gets it value from the object that defines this parm spec 
-- IN 
-- 		p_ap_spec_id integer -  id of the spec this object is being added 
-- 		p_order_num integer -  order number
-- 		p_data_type_id integer - the id of the datatype in the data type table
-- 		p_fp_id integer - id of the formal parm this parm reference
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_actual_parms_names(IN p_ap_spec_id integer, p_order_num integer, p_data_type_id varchar, p_fp_id integer)
LANGUAGE plpgsql
AS $$ DECLARE ap_tnvc_id INT;
    DECLARE dt_id INT;
    
    BEGIN 
    
    
    SELECT tnvc_id INTO ap_tnvc_id FROM actual_parmspec WHERE ap_spec_id = p_ap_spec_id;

    SELECT data_type_id INTO dt_id FROM data_type WHERE type_name = p_data_type_id;

    INSERT INTO type_name_value_entry(tnvc_id, order_num, data_type_id, data_name, fp_id) VALUES(ap_tnvc_id, p_order_num, dt_id, p_data_Type_id, p_fp_id);
    


end$$;


-- ==================================================================
-- SP__insert_actual_parms_tnvc
--  inserting an actual parm tnvc into spec.
-- IN 
-- 		p_ap_spec_id integer -  id of the spec this object is being added 
-- 		p_order_num integer -  order number
-- 		p_data_type_id integer - the id of the datatype in the data type table
-- 		p_tnvc_id integer - id of the type name value collection
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_actual_parms_tnvc(IN p_ap_spec_id integer, p_order_num integer, p_tnvc_id integer)
LANGUAGE plpgsql
AS $$
DECLARE 
ap_tnvc_id int;
r_entry_id INT;
 BEGIN
    
    SELECT tnvc_id INTO ap_tnvc_id FROM actual_parmspec WHERE ap_spec_id = p_ap_spec_id;

    CALL SP__insert_tnvc_tnvc_entry(ap_tnvc_id, p_order_num, p_tnvc_id, r_entry_id);
end$$;


-- ==================================================================
-- SP__insert_actual_parms_ac
--  inserting an actual parm ac into spec.
-- IN 
-- 		p_ap_spec_id integer -  id of the spec this object is being added 
-- 		p_order_num integer -  order number
-- 		p_data_type_id integer - the id of the datatype in the data type table
-- 		p_ac_id integer - id of the ari collection
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_actual_parms_ac(IN p_ap_spec_id integer, p_order_num integer, p_ac_id integer)
LANGUAGE plpgsql
AS $$ 
DECLARE 
ap_tnvc_id int;
 r_entry_id INT;
BEGIN 
    
    SELECT ap_tnvc_id=tnvc_id FROM actual_parmspec WHERE ap_spec_id = p_ap_spec_id;

    CALL SP__insert_tnvc_ac_entry(ap_tnvc_id, p_order_num, p_ac_id, r_entry_id);

end$$;