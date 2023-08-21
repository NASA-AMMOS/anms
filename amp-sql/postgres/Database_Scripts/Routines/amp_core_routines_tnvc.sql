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

-- STORED PROCEDURE(S) for inserting type name value collections into db


-- ==================================================================
-- SP__insert_tnvc
-- inserts a new tnv collection definition into the db
-- IN
-- 		p_num_entries integer - number of entries in the collection
-- 		p_use_desc varchar -  human readble description for the collection
-- OUT 
-- 		r_tnvc_id integer - id of the collection
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_tnvc_collection(IN p_use_desc varchar, INOUT r_tnvc_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	INSERT INTO type_name_value_collection(use_desc) VALUES(p_use_desc) RETURNING tnvc_id INTO r_tnvc_id;
end$$;


-- ==================================================================
-- sp for inserting a single entry into a tnvc 
-- SP__insert_tnvc_entry
-- IN 
-- 		p_tnvc_id integer - id of tnvc this entry belongs to 
-- 		p_order_num integer - order number of this entry 
-- 		p_data_type_name varchar -  data type name 
-- 		p_data_name varchar - name of the tnvc 
-- 		p_definition_id integer - definition of the object could be literal
-- OUT 
-- 		r_tnvc_entry_id integer - id of this entrty
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_tnvc_entry(IN p_tnvc_id integer, p_order_num integer, p_data_type_name varchar, p_data_name varchar, INOUT r_tnvc_entry_id integer)
LANGUAGE plpgsql
AS $$ BEGIN

    IF p_order_num IS NULL THEN
       SELECT order_num+1 INTO p_order_num FROM type_name_value_entry WHERE tnvc_id=p_tnvc_id ORDER BY order_num DESC LIMIT 1;
    END IF;
    IF p_order_num IS NULL THEN
       p_order_num = 0;
    END IF; 


	INSERT INTO type_name_value_entry
(tnvc_id,
order_num,
data_type_id,
data_name)
VALUES
(p_tnvc_id,
p_order_num,
(SELECT data_type_id FROM data_type WHERE type_name = UPPER(p_data_type_name)),
p_data_name) RETURNING tnv_id INTO r_tnvc_entry_id;

end$$;




CREATE OR REPLACE PROCEDURE SP__insert_tnvc_entry_id(IN p_tnvc_id integer, p_order_num integer, p_data_type_id integer, p_data_name varchar, INOUT r_tnvc_entry_id integer)
LANGUAGE plpgsql
AS $$ BEGIN

    IF p_order_num IS NULL THEN
       SELECT order_num+1 INTO p_order_num FROM type_name_value_entry WHERE tnvc_id=p_tnvc_id ORDER BY order_num DESC LIMIT 1;
    END IF;
    IF p_order_num IS NULL THEN
       p_order_num = 0;
    END IF; 


INSERT INTO type_name_value_entry
(tnvc_id,
order_num,
data_type_id,
data_name)
VALUES
(p_tnvc_id,
p_order_num,
p_data_type_id,
p_data_name) RETURNING tnv_id INTO r_tnvc_entry_id;

end$$;


-- ==================================================================
--  SP__insert_tnvc_obj_entry
--  insert a new tnvc entry that is an ADM object
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   integer - id for this actual object
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_obj_entry(IN p_tnvc_id integer,
                                                  p_order_num integer,
                                                  p_data_type varchar,
                                                  p_entry_value integer,
                                                  INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry(p_tnvc_id, p_order_num, p_data_type, NULL, r_tnvc_entry_id);
    INSERT INTO type_name_value_obj_entry (tnv_id, obj_actual_definition_id) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;




CREATE OR REPLACE PROCEDURE SP__insert_tnvc_ac_entry(IN p_tnvc_id integer,
                                                  p_order_num integer,
                                                  p_data_name varchar,
                                                  p_entry_value integer,
                                                  INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN

    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 37, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_ac_entry (tnv_id, ac_id) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;



CREATE OR REPLACE PROCEDURE SP__insert_tnvc_tnvc_entry(IN p_tnvc_id integer,
                                                  p_order_num integer,
                                                  p_data_name varchar, 
                                                  p_entry_value integer,
                                                  INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 35, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_tnvc_entry (tnv_id, tnvc_id) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;



-- ==================================================================
--  SP__insert_tnvc_ari_entry
--  insert a new tnvc entry that is an ADM object
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   integer - id for this actual object
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_ari_entry(IN p_tnvc_id integer,
                                                  p_order_num integer,
                                                  p_data_name varchar,
                                                  p_entry_value integer,
                                                  INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry(p_tnvc_id, p_order_num, 'ari', p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_obj_entry (tnv_id, obj_actual_definition_id) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;


-- ==================================================================
--  SP__insert_tnvc_unk_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_unk_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry(p_tnvc_id, p_order_num, 'unk', p_data_name, r_tnvc_entry_id);
end$$;



-- ==================================================================
--  SP__insert_tnvc_int_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   int- value for this int_entry
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_int_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value int, INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 19, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_int_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;


-- ==================================================================
--  SP__insert_tnvc_uint_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   integer - value for this uint_entry
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_uint_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value integer , INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 20, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_uint_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;


-- ==================================================================
--  SP__insert_tnvc_vast_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   bigint - value for this vast_entry
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_vast_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value bigint , INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 21, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_vast_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;


-- ==================================================================
--  SP__insert_tnvc_uvast_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   bigint - value for this uvast_entry
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_uvast_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value bigint , INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 22, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_uvast_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;


-- ==================================================================
--  SP__insert_tnvc_tv_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   bigint - value for this uvast_entry
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_tv_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value bigint , INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 32, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_uvast_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;


-- ==================================================================
--  SP__insert_tnvc_uvast_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   bigint - value for this uvast_entry
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_ts_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value bigint , INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 33, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_uvast_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;


-- ==================================================================
--  SP__insert_tnvc_real32_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   float- value for this real32_entry
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_real32_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value float, INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 23, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_real32_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;


-- ==================================================================
--  SP__insert_tnvc_real64_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   double- value for this real64_entry
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_real64_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value double precision, INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 24, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_real64_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;


-- ==================================================================
--  SP__insert_tnvc_str_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   varchar- value for this string_entry
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_str_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value varchar, INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 18, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_string_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;


-- ==================================================================
--  SP__insert_tnvc_bool_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   bool- value for this bool_entry
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_bool_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value bool, INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 16, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_bool_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;


-- ==================================================================
--  SP__insert_tnvc_byte_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   smallint- value for this byte_entry
-- ================================================================== 

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_byte_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value smallint, INOUT r_tnvc_entry_id integer )
LANGUAGE plpgsql
AS $$ BEGIN
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 17, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_byte_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
end$$;



-- STORED PROCEDURE(S) for creating an ari collection and entries

-- ==================================================================
-- SP__insert_ac_id 
-- adds an ari collection to the database
-- Parameters:
-- in 
-- 		p_num_entries integer - number of entries in the ac
-- 		p_use_desc varchar - human readable description
-- OUT 
-- 		r_ac_id integer- id of the ac
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_ac_id(IN p_num_entries integer, p_use_desc varchar,  INOUT r_ac_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	INSERT INTO ari_collection(num_entries, use_desc) VALUES(p_num_entries, p_use_desc) RETURNING  ac_id INTO r_ac_id;
end$$;