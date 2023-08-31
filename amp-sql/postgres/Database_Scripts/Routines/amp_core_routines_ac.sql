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

CREATE OR REPLACE PROCEDURE SP__insert_ac_id(IN p_num_entries integer, p_use_desc varchar, OUT r_ac_id integer) LANGUAGE plpgsql AS $$ BEGIN
	INSERT INTO ari_collection(num_entries, use_desc) VALUES(p_num_entries, p_use_desc) RETURNING  ari_collection_id INTO r_ac_id;
end$$;

-- ==================================================================
-- SP__insert_ac_formal_entry
-- adds a formal ari entry into the database.
-- stops if the order_num is > the number of entries for the target ac
-- Parameters:
-- in
-- 		p_ac_id integer - id of the ari collection this entry belongs to
-- 		p_definition_id integer - id of the definition
-- 		p_order_num integer - order number
-- OUT
-- 		r_ac_entry_id integer - entry id
-- ==================================================================

CREATE OR REPLACE PROCEDURE SP__insert_ac_formal_entry(IN p_ac_id integer, p_definition_id integer, p_order_num integer, INOUT r_ac_entry_id integer) LANGUAGE plpgsql AS $$ BEGIN
	/*IF p_order_num < (select num_entries from ari_collection where ari_collection.ac_id = p_definition_id) THEN
    LANGUAGE plpgsql*/
		INSERT INTO ari_collection_entry(ac_id, order_num) VALUES(p_ac_id, p_order_num) RETURNING  ari_collection_entry_id INTO r_ac_entry_id;
		INSERT INTO ari_collection_formal_entry(ac_entry_id, obj_formal_definition_id) VALUES(r_ac_entry_id, p_definition_id);
	/*END;
    END IF;*/
end$$;

-- ==================================================================
-- SP__insert_ac_actual_entry
-- adds a actual ari entry into the database.
-- stops if the order_num is > the number of entries for the target ac
-- Parameters:
-- in
-- 		p_ac_id integer - id of the ari collection this entry belongs to
-- 		p_definition_id integer - id of the definition
-- 		p_order_num integer - order number
-- OUT
-- 		r_ac_entry_id integer - entry id
-- ==================================================================

CREATE OR REPLACE PROCEDURE SP__insert_ac_actual_entry(IN p_ac_id integer, p_definition_id integer, p_order_num integer, OUT r_ac_entry_id integer) LANGUAGE plpgsql AS $$ BEGIN
	-- IF p_order_num < (select num_entries from ari_collection where ari_collection.ac_id = p_definition_id) THEN

		INSERT INTO ari_collection_entry(ac_id, order_num) VALUES(p_ac_id, p_order_num) RETURNING ari_collection_entry_idINTO r_ac_entry_id;
		INSERT INTO ari_collection_actual_entry(ac_entry_id, obj_actual_definition_id) VALUES(r_ac_entry_id, p_definition_id);
-- END;
   -- END IF;
end$$;
