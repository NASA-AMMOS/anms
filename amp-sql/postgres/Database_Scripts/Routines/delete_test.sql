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


CREATE OR REPLACE PROCEDURE SP__insert_ac_id(IN p_num_entries integer, p_use_desc varchar,  OUT r_ac_id integer)
LANGUAGE SQL
AS $$
	INSERT INTO amp_core.ari_collection(num_entries, use_desc) VALUES(p_num_entries, p_use_desc); 
    SET r_ac_id = LAST_INSERT_ID();
$$;



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


CREATE OR REPLACE PROCEDURE SP__insert_ac_formal_entry(IN p_ac_id integer, p_definition_id integer,  p_order_num integer, OUT r_ac_entry_id integer)
LANGUAGE SQL
AS $$ 
	/*IF p_order_num < (select num_entries from ari_collection where ari_collection.ac_id = p_definition_id) THEN 
    LANGUAGE SQL
AS $$*/
		INSERT INTO amp_core.ari_collection_entry(ac_id, order_num) VALUES(p_ac_id, p_order_num);
		SET r_ac_entry_id = LAST_INSERT_ID();
		INSERT INTO amp_core.ari_collection_formal_entry(ac_entry_id, obj_formal_definition_id) VALUES(r_ac_entry_id, p_definition_id); 
	/*END;
    END IF;*/
$$;



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


CREATE OR REPLACE PROCEDURE SP__insert_ac_actual_entry(IN p_ac_id integer, p_definition_id integer, p_order_num integer, 
OUT r_ac_entry_id integer)
LANGUAGE SQL
AS $$ 
	-- IF p_order_num < (select num_entries from ari_collection where ari_collection.ac_id = p_definition_id) THEN 
    -- LANGUAGE SQL
AS $$
		INSERT INTO amp_core.ari_collection_entry(ac_id, order_num) VALUES(p_ac_id, p_order_num);
		SET r_ac_entry_id = LAST_INSERT_ID();
		INSERT INTO amp_core.ari_collection_actual_entry(ac_entry_id, obj_actual_definition_id) VALUES(r_ac_entry_id, p_definition_id); 
-- END;
   -- END IF;
$$;


-- DROP PROCEDURE IF EXISTS SP__insert_ari_collection;
-- 
-- CREATE OR REPLACE PROCEDURE SP__insert_ari_collection(IN p_num_entries integer, p_definition_ids_list varchar(10000), p_instance_ids_list varchar(10000), p_use_desc varchar, OUT r_ac_id integer) 
-- LANGUAGE SQL
AS $$ 
-- 	CALL SP__insert_ac_id(p_num_entries, p_use_desc, r_ac_id); 
--     -- TODO -- verify that lists are same size or NULL prior to processing, backout transaction on failure  and return NULL
--     SET @ac_id  = r_ac_id; 
--     SET @s = 'INSERT INTO amp_core.ari_collection_entry(ac_id, definition_id, instance_id, order_num) VALUES'; 
-- 	
-- 	SET @loops = 1; 
-- --     -- SET @def_id = NULL; 
-- --     -- SET @inst_id = NULL; 
--     WHILE @loops < p_num_entries DO
-- 		LANGUAGE SQL
AS $$
-- 			-- @def_id
--             IF p_definition_ids_list IS NOT NULL THEN
-- 				LANGUAGE SQL
AS $$
-- 				SET @def_id = TRIM(SUBSTRING_INDEX(p_definition_ids_list, ',', 1)); 
-- 				SET p_definition_ids_list = REPLACE(p_definition_ids_list, CONCAT(@def_id, ','), '');
-- 				-- IF strcmp(@def_id, 'NULL') THEN
-- 					-- SET @def_id = NULL; 
-- 				-- ELSE
-- 					SET @def_id = CAST(@def_id AS UNSIGNED); 
-- 				-- END IF;
--                 END; 
-- 			ELSE 
-- 				LANGUAGE SQL
AS $$
-- 				 SET @def_id = 'NULL';
-- 				END; 
--             END IF; 
--             
--             -- @inst_id
--             IF p_instance_ids_list IS NOT NULL THEN 
-- 				LANGUAGE SQL
AS $$
-- 				SET @inst_id = TRIM(SUBSTRING_INDEX(p_instance_ids_list, ',', 1)); 
-- 				SET p_instance_ids_list = REPLACE(p_instance_ids_list, CONCAT(@inst_id, ','), '');
-- 				-- IF strcmp(@inst_id, 'NULL') THEN 
-- 					-- SET @inst_id = NULL; 
-- 				-- ELSE
-- 					SET @inst_id = CAST(@inst_id AS UNSIGNED); 
-- 				-- END IF;
--                 END;
-- 			ELSE 
-- 				LANGUAGE SQL
AS $$
-- 				SET @inst_id = 'NULL'; 
--                 END; 
-- 			END IF; 
-- 			
--             SET @s = CONCAT(@s, '(', @ac_id, ',', @def_id , ',', @inst_id, ',', @loops, '),');
--            -- SELECT @s; 
--  			SET @loops = @loops + 1; 
--          END; 
--     END WHILE; 
--     
--     -- @def_id
--             IF p_definition_ids_list IS NOT NULL THEN
-- 				LANGUAGE SQL
AS $$
-- 				SET @def_id = TRIM(SUBSTRING_INDEX(p_definition_ids_list, ',', 1)); 
-- 				SET p_definition_ids_list = REPLACE(p_definition_ids_list, CONCAT(@def_id, ','), '');
-- 			-- 	IF strcmp(@def_id, 'NULL') THEN
-- 				-- 	SET @def_id = NULL; 
-- 			--	ELSE
-- 					SET @def_id = CAST(@def_id AS UNSIGNED); 
-- 				-- END IF;
--                 END; 
-- 			ELSE 
-- 				LANGUAGE SQL
AS $$
-- 				 SET @def_id = 'NULL'; 
-- 				END; 
--             END IF; 
--             
--             -- @inst_id
--             IF p_instance_ids_list IS NOT NULL THEN 
-- 				LANGUAGE SQL
AS $$
-- 				SET @inst_id = TRIM(SUBSTRING_INDEX(p_instance_ids_list, ',', 1)); 
-- 				SET p_instance_ids_list = REPLACE(p_instance_ids_list, CONCAT(@inst_id, ','), '');
-- 				-- IF strcmp(@inst_id, 'NULL') THEN 
-- 				--	SET @inst_id = NULL; 
-- 				-- ELSE
-- 					SET @inst_id = CAST(@inst_id AS UNSIGNED); 
-- 				-- END IF;
--                 END; 
-- 			 ELSE 
-- 				LANGUAGE SQL
AS $$
-- 			 	SET @inst_id = 'NULL'; 
--                 END;
-- 			END IF; 
-- 			
--             SET @s = CONCAT(@s, '(', @ac_id, ',', @def_id, ',', @inst_id, ',', @loops, ')');
--           -- SELECT @s; 
-- 	PREPARE stmt FROM @s; 
-- 	EXECUTE stmt; 
-- $$;



USE amp_core;

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


CREATE OR REPLACE PROCEDURE SP__insert_actual_parmspec_tnvc(IN p_fp_spec_id integer, p_tnvc_id integer, p_use_desc varchar, OUT r_ap_spec_id integer)
LANGUAGE SQL
AS $$
	INSERT INTO amp_core.actual_parmspec(fp_spec_id, tnvc_id, use_desc) VALUES(p_fp_spec_id, p_tnvc_id, p_use_desc); 
    SET r_ap_spec_id = LAST_INSERT_ID();
$$;


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


CREATE OR REPLACE PROCEDURE SP__insert_actual_parmspec(IN p_fp_spec_id integer, p_num_parms integer, p_use_desc varchar, OUT r_ap_spec_id integer)
LANGUAGE SQL
AS $$
    DECLARE tnvc_id INT;
    CALL SP__insert_tnvc_collection(p_use_desc, tnvc_id);
    CALL SP__insert_actual_parmspec_tnvc(p_fp_spec_id, tnvc_id, p_use_desc, r_ap_spec_id);
$$;


-- ==================================================================
-- SP__insert_actual_parms_object
--  inserting an actual parm object into spec
-- IN 
-- 		p_ap_spec_id integer -  id of the spec this object is being added 
-- 		p_order_num integer -  order number
-- 		p_data_type_id integer - the id of the datatype in the data type table
-- 		p_obj_actual_definition integer - id of the object for the parm
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_actual_parms_object(IN p_ap_spec_id INT unsigned, p_order_num integer, p_data_type_id varchar , p_obj_actual_definition INT UNSIGNED)
LANGUAGE SQL
AS $$
    DECLARE ap_tnvc_id, r_tnvc_entry_id INT;
    SELECT tnvc_id INTO ap_tnvc_id FROM amp_core.actual_parmspec WHERE ap_spec_id = p_ap_spec_id;


    CALL SP__insert_tnvc_obj_entry(ap_tnvc_id, p_order_num, p_data_type_id, p_obj_actual_definition, r_tnvc_entry_id);



$$;


-- ==================================================================
-- SP__insert_actual_parms_names
--  inserting an actual parm reference by name into spec. This parm gets it value from the object that defines this parm spec 
-- IN 
-- 		p_ap_spec_id integer -  id of the spec this object is being added 
-- 		p_order_num integer -  order number
-- 		p_data_type_id integer - the id of the datatype in the data type table
-- 		p_fp_id integer - id of the formal parm this parm reference
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_actual_parms_names(IN p_ap_spec_id INT(10) unsigned, p_order_num integer, p_data_type_id varchar, p_fp_id INT(10) UNSIGNED)
LANGUAGE SQL
AS $$ 
    DECLARE ap_tnvc_id INT;
    DECLARE dt_id INT;
    
    SELECT tnvc_id INTO ap_tnvc_id FROM amp_core.actual_parmspec WHERE ap_spec_id = p_ap_spec_id;

    SELECT data_type_id INTO dt_id FROM data_type WHERE type_name = p_data_type_id;

    INSERT INTO type_name_value_entry(tnvc_id, order_num, data_type_id, data_name, fp_id) VALUES(ap_tnvc_id, p_order_num, dt_id, p_data_Type_id, p_fp_id);
    


$$;


-- ==================================================================
-- SP__insert_actual_parms_tnvc
--  inserting an actual parm tnvc into spec.
-- IN 
-- 		p_ap_spec_id integer -  id of the spec this object is being added 
-- 		p_order_num integer -  order number
-- 		p_data_type_id integer - the id of the datatype in the data type table
-- 		p_tnvc_id integer - id of the type name value collection
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_actual_parms_tnvc(IN p_ap_spec_id INT(10) unsigned, p_order_num integer, p_tnvc_id INT(10) UNSIGNED)
LANGUAGE SQL
AS $$
    DECLARE ap_tnvc_id, r_entry_id INT;
    SELECT tnvc_id INTO ap_tnvc_id FROM amp_core.actual_parmspec WHERE ap_spec_id = p_ap_spec_id;

    CALL SP__insert_tnvc_tnvc_entry(ap_tnvc_id, p_order_num, p_tnvc_id, r_entry_id);
$$;


-- ==================================================================
-- SP__insert_actual_parms_ac
--  inserting an actual parm ac into spec.
-- IN 
-- 		p_ap_spec_id integer -  id of the spec this object is being added 
-- 		p_order_num integer -  order number
-- 		p_data_type_id integer - the id of the datatype in the data type table
-- 		p_ac_id integer - id of the ari collection
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_actual_parms_ac(IN p_ap_spec_id INT(10) unsigned, p_order_num integer, p_ac_id INT(10) UNSIGNED)
LANGUAGE SQL
AS $$ 
    DECLARE ap_tnvc_id, r_entry_id INT;
    SELECT ap_tnvc_id=tnvc_id FROM amp_core.actual_parmspec WHERE ap_spec_id = p_ap_spec_id;

    CALL SP__insert_tnvc_ac_entry(ap_tnvc_id, p_order_num, p_ac_id, r_entry_id);

$$;




-- was used before one there wasnt two types of actual_parms so it was easy to parse a 
-- a list of parms 
--
-- 
-- 
-- CREATE OR REPLACE PROCEDURE SP__insert_actual_parms_set(IN p_num_parms integer, p_fp_spec_id integer, p_data_types_list varchar(10000), p_data_values_list varchar(10000), OUT r_ap_spec_id integer)
-- LANGUAGE SQL
AS $$ 
-- 	CALL SP__insert_actual_parmspec(p_fp_spec_id, r_ap_spec_id); 
--     SET @ap_spec_id = r_ap_spec_id; 
--     SET @s = 'INSERT INTO amp_core.actual_parm(order_num, ap_type, data_value, ap_spec_id) VALUES'; 
--     SET @loops = 1; 
--     WHILE @loops < p_num_parms DO 
-- 		LANGUAGE SQL
AS $$
-- 			-- @data_type
-- 				SET @data_type = TRIM(SUBSTRING_INDEX(p_data_types_list, ',', 1));
-- 				SET p_data_types_list = REPLACE(p_data_types_list, CONCAT(@data_type, ','), ''); 
--     
--             -- @data_value
-- 				SET @data_value = TRIM(SUBSTRING_INDEX(p_data_values_list, ',', 1));
--                 SET p_data_values_list = REPLACE(p_data_values_list, CONCAT(@data_value, ','), '');
--             
-- 				SET @s = CONCAT(@s, '(', @loops, ',', (SELECT data_type_id FROM amp_core.data_type WHERE type_name = @data_type), ',', '"', @data_value, '"', ',', @ap_spec_id, '),');
--                 SET @loops = @loops + 1; 
--         END; 
--     END WHILE; 
--  
--     -- @data_type
-- 	SET @data_type = TRIM((SUBSTRING_INDEX(p_data_types_list, ',', 1)));
--     
-- 	
-- 	-- @data_value
-- 	SET @data_value = TRIM(SUBSTRING_INDEX(p_data_values_list, ',', 1));

-- 	SET @s = CONCAT(@s, '(', @loops, ',', (SELECT data_type_id FROM amp_core.data_type WHERE type_name = @data_type), ',', '"', @data_value, '"', ',', @ap_spec_id, ')');
-- 	PREPARE stmt FROM @s; 
--     EXECUTE stmt; 

-- $$;
-- 

use amp_core;

-- inserting reg agents into the db

-- ==================================================================
-- SP__insert_agent
--  inserting a new agent into the systemß
-- IN 
-- 		p_agent_id_string- name of the agent to insert 
-- OUT
-- 		r_registered_agents_id - teh id of the agent in the db
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_agent(IN p_agent_id_string varchar, OUT r_registered_agents_id INT unsigned)
LANGUAGE SQL
AS $$ 
	SET @cur_time = NOW(); 
    SET @lower_name = LOWER(p_agent_id_string);
    SET @eid = NULL;
    SELECT registered_agents_id INTO @eid FROM registered_agents WHERE @lower_name = agent_id_string;
    
	IF (@eid IS NOT NULL) THEN 
	LANGUAGE SQL
AS $$ 
		UPDATE registered_agents SET last_registered = @cur_time WHERE registered_agents_id=@eid;
        SET r_registered_agents_id = @eid;
    END;
    ELSE LANGUAGE SQL
AS $$
    INSERT INTO registered_agents (agent_id_string,first_registered, last_registered)
		VALUES (@lower_name, @cur_time, @cur_time);
		SET r_registered_agents_id = LAST_INSERT_ID();
    END;
    END IF;
$$;



-- ==================================================================
-- Author: David Linko	
-- 
-- Description:  inserting, updating and removing constant formal and actual definitions
-- using the obj routines
-- 
-- ==================================================================

USE amp_core;


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


CREATE OR REPLACE PROCEDURE SP__insert_const_actual_definition(IN p_obj_id integer, p_use_desc varchar, p_data_type varchar, p_data_value_string varchar, OUT r_actual_definition_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_actual_definition(p_obj_id, p_use_desc, r_actual_definition_id); 
    Set @data_id  = (SELECT data_type_id FROM amp_core.data_type WHERE type_name  = p_data_type);
    INSERT INTO amp_core.const_actual_definition(obj_actual_definition_id, data_type_id, data_value) VALUES(r_actual_definition_id, @data_id, p_data_value_string); 
$$;



-- ==================================================================
-- SP__delete_const_actual_definition
-- cna us either hte name or the id of the constant to delete 
-- Parameters:
-- in 
--  	p_obj_id integer -  id of the constan to delete 
-- 		p_obj_name varchar -   name of the constant to delete
-- ==================================================================
DROP PROCEDURE IF EXiSTS SP__delete_const_actual_definition;

CREATE OR REPLACE PROCEDURE SP__delete_const_actual_definition(IN p_obj_id integer, p_obj_name varchar)
LANGUAGE SQL
AS $$
	IF (p_obj_id != null) THEN
		SET @metadata_id = (SELECT obj_metadata_id FROM obj_actual_definition WHERE obj_actual_definition_id = p_obj_id );
	ELSE
		IF (p_obj_name != NULL) THEN 
			SET @metadata_id = (SELECT obj_metadata_id FROM obj_metadata WHERE obj_name = p_obj_name); 
        END IF;
	END IF;
    CALL SP__delete_obj_metadata(@metadata_id);
    
END//


-- ==================================================================
-- Author: David Linko	
-- 
-- Description:  inserting, updating and removing control formal and actual definitions
-- using the obj routines
-- 
-- ==================================================================

USE amp_core;



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


CREATE OR REPLACE PROCEDURE SP__insert_control_formal_definition(IN p_obj_id integer, p_use_desc varchar, p_fp_spec_id integer, OUT r_definition_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_formal_definition(p_obj_id, p_use_desc, r_definition_id); 
    INSERT INTO amp_core.control_formal_definition(obj_formal_definition_id, fp_spec_id) VALUES(r_definition_id, p_fp_spec_id);
$$;


-- ==================================================================
-- SP__delete_control_formal_definition;
-- Parameters:
-- in 
--     p_obj_id  - id of the control to delete
--     p_obj_name - name of the control to delete 
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__delete_control_formal_definition(IN p_obj_id integer, p_obj_name varchar)
LANGUAGE SQL
AS $$
	CALL SP__delete_obj_formal_definition(p_obj_id, p_obj_name);
$$;



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


CREATE OR REPLACE PROCEDURE SP__insert_control_actual_definition(IN p_obj_definition_id integer, p_ap_spec_id integer, p_use_desc varchar, OUT r_instance_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_actual_definition(p_obj_definition_id, p_use_desc, r_instance_id);

    -- TODO: Skip insert if it has no parameters
    INSERT INTO amp_core.control_actual_definition(obj_actual_definition_id, ap_spec_id) VALUES(r_instance_id, p_ap_spec_id);  
$$; 
 


-- ==================================================================
-- SP__delete_control_actual_definition;
-- Parameters:
-- in 
--     p_obj_id integer - actual_definiton id of the control that is to be deleted
--     p_obj_name varchar- name of the control to delete, this allows to delete all the actual definitons 
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__delete_control_actual_definition(IN p_obj_id integer, p_obj_name varchar)
ctrl_actual_definition_del:LANGUAGE SQL
AS $$
	
	DECLARE done INT DEFAULT FALSE;
    DECLARE actual_definition_id_hold, ap_spec_id_hold integer;
    DECLARE actual_definition_cursor CURSOR
			FOR SELECT actual_definition_id, ap_spec_id FROM vw_ctrl_actual_definition WHERE obj_name = p_obj_name;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;	
    
    -- only one thing to remove 
	If( p_inst_id is not null) then 
		SET @ap_id = (SELECT ap_spec_id from ctrl_actual_definition where actual_definition_id = p_inst_id );
		IF( @ap_id is not null) THEN
			DELETE FROM actual_parmspec WHERE ap_spec_id = @ap_id;
		END IF;
		DELETE FROM ctrl_actual_definition 
WHERE
    intance_id = p_actual_definition_id;
		CALL SP__delete_obj_actual_definition(p_actual_definition_id, p_obj_name);
	ELSE -- removing all instances with this name 
		IF( p_obj_name is null) then -- nothing to do 
			leave ctrl_actual_definition_del;
		END IF;
		OPEN actual_definition_cursor;
        read_loop: LOOP
			FETCH NEXT FROM actual_definition_cursor INTO 
				actual_definition_id_hold, ap_spec_id_hold;
			IF done THEN
				LEAVE read_loop;
			END IF;

			DELETE FROM actual_parmspec WHERE ap_spec_id = ap_spec_id_hold;

			DELETE FROM ctrl_actual_definition
WHERE
    amp_core.ctrl_actual_definition.actual_definition_id = actual_definition_id_hold;			
		END LOOP;
        CALL SP__delete_obj_actual_definition(null, p_obj_name);
    end if;
    CLOSE actual_definition_cursor;
END  //


USE amp_core;

-- STORED PROCEDURE(S)

-- 
-- 
-- CREATE OR REPLACE PROCEDURE SP__insert_data_value(IN p_value_converted varchar, p_value_string varchar, OUT r_value_id integer)
-- LANGUAGE SQL
AS $$
-- 	INSERT INTO amp_core.data_value(value_converted, value_string) VALUES(p_value_converted, p_value_string); 
--     SET r_value_id =  LAST_INSERT_ID();
-- $$;
-- 

-- ==================================================================
-- Author: David Linko	
-- 
-- Description:  inserting, updating and removing EDD formal and actual definitions
-- using the obj routines
-- 
-- ==================================================================

USE amp_core;


-- ==================================================================
-- SP__insert_edd_formal_definition;
-- Parameters:
-- in 
--     p_obj_id integer - id for the object metadata
--      p_use_desc varchar - humanreadable description of the edd 
-- 		p_data_type varchar -  name of the data type for the edd 
--  	p_data_value_string varchar - blob conating the encoded value of the edd
-- out
-- 		r_actual_definition_id integer id of the actual defintion entry 
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_edd_formal_definition(IN p_obj_id integer, p_use_desc varchar, p_fp_spec_id integer, p_external_data_type varchar, OUT r_formal_definition_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_formal_definition(p_obj_id, p_use_desc, r_formal_definition_id); 
    INSERT INTO amp_core.edd_formal_definition(obj_formal_definition_id, fp_spec_id, data_type_id) VALUES(r_formal_definition_id, p_fp_spec_id, (SELECT data_type_id FROM amp_core.data_type WHERE type_name  = p_external_data_type)); 
$$;




-- ==================================================================
-- SP__delete_edd_actual_definition;
-- Parameters:
-- in 
--      p_obj_id integer - id for the edd to delete 
-- 		p_obj_name varchar -  name of the edd  to delete 
--
-- ==================================================================
DROP PROCEDURE IF EXISTS SP__delete_edd_formal_defintion;
 
CREATE OR REPLACE PROCEDURE SP__delete_edd_formal_defintion(IN p_obj_id integer, p_obj_name varchar)
edd_def_del:LANGUAGE SQL
AS $$
	IF( p_obj_id is Null AND p_obj_name is not NULL) THEN
		SET p_obj_id =  (select obj_id FROM amp_core.obj_metadata WHERE obj_name = p_obj_name);
    ELSE 
		LEAVE edd_def_del;
    END IF;
    
    IF(p_obj_name is NULL) THEN
		SET p_obj_name = (select obj_name from vw_edd_formal where obj_id = p_obj_id);
    END IF ;
    
	-- deleting all instances 
	CALL SP__delete_edd_actual_definition(null, p_obj_name);
    
	SET @def_id = (select obj_formal_definition_id from obj_formal_definition where obj_metadata_id = p_obj_id);
	SET @fp_id = (SELECT fp_spec_id from edd_formal_definition where obj_formal_definition_id = @def_id );
	DELETE FROM formal_parmspec WHERE fp_spec_id = @fp_id;
    
	CALL SP__delete_obj_formal_defintion(p_obj_id, p_obj_name);
$$; 



-- ==================================================================
-- SP__insert_edd_actual_definition;
-- Parameters:
-- in 
--     p_obj_id integer - id for the object metadata
--      p_use_desc varchar - humanreadable description of the constant 
-- 		p_data_type varchar -  name of the data type for the constant 
--  	p_data_value_string varchar - blob conating the encoded value of the constant 
-- out
-- 		r_actual_definition_id integer id of the actual defintion entry 
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_edd_actual_definition(IN p_obj_definition_id integer, p_use_desc varchar, p_ap_spec_id integer,  OUT r_actual_definition_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_actual_definition(p_obj_definition_id, p_use_desc, r_actual_definition_id); 
    INSERT INTO amp_core.edd_actual_definition(obj_actual_definition_id, ap_spec_id) VALUES(r_actual_definition_id, p_ap_spec_id);  
$$; 
 


-- ==================================================================
-- SP__delete_edd_actual_definition;
-- Parameters:
-- in 
--     p_obj_id integer - id for the object metadata
--      p_use_desc varchar - humanreadable description of the constant 
-- 		p_data_type varchar -  name of the data type for the constant 
--  	p_data_value_string varchar - blob conating the encoded value of the constant 
-- out
-- 		r_actual_definition_id integer id of the actual defintion entry 
-- ==================================================================
-- for instance can supply the definiton name to remove all the instances of that definition or can remove 
DROP PROCEDURE IF EXISTS SP__delete_edd_actual_definition;

CREATE OR REPLACE PROCEDURE SP__delete_edd_actual_definition(IN p_actual_definition_id integer, p_obj_name varchar)
edd_actual_definition_del:LANGUAGE SQL
AS $$
	
	DECLARE done INT DEFAULT FALSE;
    DECLARE actual_definition_id_hold, ap_spec_id_hold integer;
    DECLARE actual_definition_cursor CURSOR
			FOR SELECT actual_definition_id, ap_spec_id FROM vw_edd_actual WHERE obj_name = p_obj_name;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;	
    
    -- only one thing to remove 
	If( p_inst_id is not null) then 
		SET @ap_id = (SELECT ap_spec_id from edd_actual_definition where actual_definition_id = p_inst_id );
		IF( @ap_id is not null) THEN
			DELETE FROM actual_parmspec WHERE ap_spec_id = @ap_id;
		END IF;
		DELETE FROM edd_actual_definition 
WHERE
    intance_id = p_actual_definition_id;
		CALL SP__delete_obj_actual_definition(p_actual_definition_id, p_obj_name);
	ELSE -- removing all instances with this name 
		IF( p_obj_name is null) then -- nothing to do 
			leave edd_actual_definition_del;
		END IF;
		OPEN actual_definition_cursor;
        read_loop: LOOP
			FETCH NEXT FROM actual_definition_cursor INTO 
				actual_definition_id_hold, ap_spec_id_hold;
			IF done THEN
				LEAVE read_loop;
			END IF;

			DELETE FROM actual_parmspec WHERE ap_spec_id = ap_spec_id_hold;

			DELETE FROM edd_actual_definition
WHERE
    amp_core.edd_actual_definition.actual_definition_id = actual_definition_id_hold;			
		END LOOP;
        CALL SP__delete_obj_actual_definition(null, p_obj_name);
    end if;
    CLOSE actual_definition_cursor;
$$; 

USE amp_core;

-- STORED PROCEDURE(S) for creating expresions that are used in rules and variables 

-- DROP PROCEDURE IF EXISTS sp_insert_postfix_operations; 
-- 
-- CREATE OR REPLACE PROCEDURE sp_insert_postfix_operations(IN p_num_operators integer, p_operator_ids_list varchar(1000), p_operands_values_list varchar(10000), OUT r_postfix_operations integer)
-- LANGUAGE SQL
AS $$ -- we get a list of operators and a list of operands need to create an ari collection for both 
--    -- need to finish
--    -- generate an ari collection
--    -- add in the airs
--    -- call sp_insert_ari_collection(IN p_num_entries integer, p_definition_ids_list varchar(10000), p_instance_ids_list varchar(10000), p_use_desc varchar, OUT r_ac_id integer)
--    
-- $$;
-- 


-- ==================================================================
-- SP__insert_expression 
-- adds an expression to the database
-- Parameters:
-- in 
-- 		p_out_type integer - data type id for the return type of the expression  
-- 		p_num_operators integer - number of operators   
-- 		p_postfix_ids_list varchar(1000) - id of the ac that lists the equation in postfix notation
-- OUT 
-- 		r_expr_id integer - id of the expr in the database
-- =================================================================


CREATE OR REPLACE PROCEDURE SP__insert_expression(IN p_out_type INT(10) UNSIGNED,   
p_postfix_operations INT(10) UNSIGNED, OUT r_expr_id INT(10) UNSIGNED)
LANGUAGE SQL
AS $$ 
	-- SELECT p_out_type;
	-- IF p_out_type = 2 or p_out_type = 12 or p_out_type = 3 or p_out_type = 0 THEN
	-- 	LANGUAGE SQL
AS $$
			INSERT INTO amp_core.expression(data_type_id, ac_id) VALUES(p_out_type, p_postfix_operations); 
			SET r_expr_id = LAST_INSERT_ID();
	-- END;
    -- END IF;
$$;



-- ==================================================================
-- SP__delete_expression 
-- Delete an expression from the database
-- Parameters:
-- in 
-- 		p_expr_id integer - id of the expr in the database to delete
-- ==================================================================



CREATE OR REPLACE PROCEDURE SP__delete_expression(IN p_expr_id INT(10) UNSIGNED)
LANGUAGE SQL
AS $$ 
	DELETE from  amp_core.expression WHERE (expression_id = p_expr_id);
$$;

USE amp_core;

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


CREATE OR REPLACE PROCEDURE SP__insert_formal_parmspec(IN p_num_parms integer, p_use_desc varchar,  OUT r_fp_spec_id integer)
LANGUAGE SQL
AS $$
	INSERT INTO amp_core.formal_parmspec(num_parms, use_desc) VALUES(p_num_parms, p_use_desc); 
    SET r_fp_spec_id = LAST_INSERT_ID();
$$;




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


CREATE OR REPLACE PROCEDURE SP__insert_formal_parmspec_entry(IN p_fp_spec_id integer,  p_order_num integer, p_parm_name varchar, p_data_type varchar, p_obj_definition_id integer, OUT r_fp_id integer)
LANGUAGE SQL
AS $$
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
p_obj_definition_id);

SET r_fp_id = LAST_INSERT_ID();
$$;




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
 p_default_values_list varchar(10000), OUT r_fp_spec_id integer)
LANGUAGE SQL
AS $$ 
	CALL SP__insert_formal_parmspec(p_num_parms, p_use_desc, r_fp_spec_id); 
    SET @fp_spec_id = r_fp_spec_id; 
    SET @s = 'INSERT INTO amp_core.formal_parm(fp_spec_id, order_num, parm_name, data_type_id, obj_actual_definition_id) VALUES'; 
    SET @loops = 1; 
    WHILE @loops < p_num_parms DO 
		LANGUAGE SQL
AS $$
			-- @data_type
				SET @data_type = TRIM(SUBSTRING_INDEX(p_data_types_list, ',', 1));
				SET p_data_types_list = REPLACE(p_data_types_list, CONCAT(@data_type, ','), ''); 
    
 			-- @parm_name
				SET @parm_name = TRIM(SUBSTRING_INDEX(p_parm_names_list, ',', 1)); 
				SET p_parm_names_list = REPLACE(p_parm_names_list, CONCAT(@parm_name, ','), '');
                
            -- @default_value
				SET @default_value = TRIM(SUBSTRING_INDEX(p_default_values_list, ',', 1));
                IF @default_value = 'NULL' THEN SET @default_value = null;
                ELSEIF @default_value = 'null' THEN SET @default_value = null;
				END IF;
                SET p_default_values_list = REPLACE(p_default_values_list, CONCAT(@default_value, ','), '');
            
				SET @s = CONCAT(@s, '(', @fp_spec_id, ',', @loops, ',', '"', @parm_name, '"', ',', (SELECT data_type_id FROM amp_core.data_type WHERE type_name = @data_type), ',', '"', @default_value, '"', '),');
                SET @loops = @loops + 1; 
        END; 
    END WHILE; 
 
    -- @data_type
	SET @data_type = TRIM((SUBSTRING_INDEX(p_data_types_list, ',', 1)));
    
	-- @parm_name
	SET @parm_name = TRIM(SUBSTRING_INDEX(p_parm_names_list, ',', 1)); 
                
	-- @default_value
	IF @default_value = 'NULL' THEN SET @default_value = null;
                ELSEIF @default_value = 'null' THEN SET @default_value = null;
				END IF;
                SET p_default_values_list = REPLACE(p_default_values_list, CONCAT(@default_value, ','), '');

	SET @s = CONCAT(@s, '(', @fp_spec_id, ',', @loops, ',', (SELECT data_type_id FROM amp_core.data_type WHERE type_name = @data_type), ',', '"', @parm_name, '"', ',', '"', @default_value, '"', ')');
	PREPARE stmt FROM @s; 
    EXECUTE stmt; 

$$;


USE amp_core;

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


CREATE OR REPLACE PROCEDURE SP__insert_literal_actual_definition(IN p_obj_id integer, p_use_desc varchar, p_data_type varchar, p_data_value_string varchar, OUT r_definition_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_actual_definition(p_obj_id, p_use_desc, r_definition_id); 
    INSERT INTO amp_core.literal_actual_definition(obj_actual_definition_id, data_type_id, data_value) VALUES(r_definition_id, (SELECT data_type_id FROM amp_core.data_type WHERE type_name  = p_data_type), p_data_value_string); 
$$;



-- ==================================================================
-- SP__delete_literal_actual_definition 
-- IN 
-- p_obj_id integer - id of the lit to be deleted
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__delete_literal_actual_definition(IN p_obj_id integer)
LANGUAGE SQL
AS $$
	CALL SP__delete_obj_definition(p_obj_id); 
$$;
USE amp_core;

-- STORED PROCEDURE(S) for creating updating and deleting macro definitions and actuals

-- ==================================================================
-- SP__insert_macro_formal_definition
-- IN
-- 		p_obj_id integer - id of the metadata info 
-- 		p_use_desc varchar - human readable describtion
--      p_fp_spec_id integer - formal parmspec of the macro
--      p_max_call_depth integer - max call depth of the macro
--      p_definition_ac integer - ari collection definining the macro
-- OUT
-- 		r_definition_id integer - id of the new formal definition	 
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_macro_formal_definition(IN p_obj_id integer, p_use_desc varchar, p_fp_spec_id integer, p_max_call_depth integer, p_definition_ac integer, OUT r_definition_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_formal_definition(p_obj_id, p_use_desc, r_definition_id); 
    INSERT INTO amp_core.macro_formal_definition(obj_formal_definition_id, fp_spec_id, ac_id, max_call_depth) VALUES(r_definition_id, p_fp_spec_id, p_definition_ac, p_max_call_depth); 
$$;



-- ==================================================================
-- SP__delete_mac_formal_defintion
-- IN 
--      p_obj_id integer - id of the macro to be deleted
-- 	 	p_obj_name varchar - name of the macro to delete
-- ==================================================================
DROP PROCEDURE IF EXISTS SP__delete_mac_formal_defintion;
 
CREATE OR REPLACE PROCEDURE SP__delete_mac_formal_defintion(IN p_obj_id integer, p_obj_name varchar)
mac_def_del:LANGUAGE SQL
AS $$
	IF( p_obj_id is Null AND p_obj_name is not NULL) THEN
		SET p_obj_id =  (select obj_id FROM amp_core.obj_metadata WHERE obj_name = p_obj_name);
    ELSE 
		LEAVE mac_def_del;
    END IF;
    
    IF(p_obj_name is NULL) THEN
		SET p_obj_name = (select obj_name from vw_mac_formal where obj_id = p_obj_id);
    END IF ;
    
	-- deleting all actuals 
	CALL SP__delete_macro_actual(null, p_obj_name);
	
	SET @def_id = (select definition_id from obj_formal_definition where obj_id = p_obj_id);
	SET @fp_id = (SELECT fp_spec_id from macro_formal_definition where definition_id = @def_id );
    SET @ac_id = (SELECT ac_id FROM macro_formal_definition where definition_id = @def_id );
    
	DELETE FROM formal_parmspec WHERE fp_spec_id = @fp_id;
	DELETE FROM ari_collection WHERE ac_id = @ac_id;

	CALL SP__delete_obj_formal_defintion(p_obj_id, p_obj_name);
$$; 



-- ==================================================================
-- SP__insert_macro_actual_definition
-- -- IN
-- 		p_obj_id integer - id of the metadata info 
--      p_ap_spec_id integer - actual parmspec id
--      p_actual_ac integer - ari collection containg all actual ARI for this macro
--      p_use_desc varchar - human readable description
-- OUT
-- 		r_actual_id integer - id of the new actual definition	
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_macro_actual_definition(IN p_obj_definition_id integer, p_ap_spec_id integer, p_actual_ac integer, p_use_desc varchar, OUT r_actual_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_actual_definition(p_obj_definition_id, p_use_desc, r_actual_id); 
    INSERT INTO amp_core.macro_actual(obj_actual_definition_id, ap_spec_id, ac_id) VALUES(r_actual_id, p_ap_spec_id, p_actual_ac);  
$$; 
 
 
-- ==================================================================
-- SP__delete_mac_actual_definition
-- IN 
--      p_obj_id integer - id of the macro to be deleted
-- 	 	p_obj_name varchar - name of the macro to delete
-- ==================================================================
-- for actual can supply the definiton name to remove all the actuals of that definition or can remove 
DROP PROCEDURE IF EXISTS SP__delete_mac_actual_definition;

CREATE OR REPLACE PROCEDURE SP__delete_mac_actual_definition(IN p_inst_id integer, p_obj_name varchar)
mac_inst_del:LANGUAGE SQL
AS $$
	
	DECLARE done INT DEFAULT FALSE;
    DECLARE actual_id_hold, ap_spec_id_hold, ac_id_hold integer;
    DECLARE actual_cursor CURSOR
			FOR SELECT actual_id, ap_spec_id, ac_id  WHERE obj_name = p_obj_name;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;	
    
    -- only one thing to remove 
	If( p_inst_id is not null) then 
		SET @ap_id = (SELECT ap_spec_id from macro_actual_definition where actual_id = p_inst_id );
		IF( @ap_id is not null) THEN
			DELETE FROM actual_parmspec WHERE ap_spec_id = @ap_id;
		END IF;
		DELETE FROM macro_actual 
WHERE
    intance_id = p_inst_id;
		CALL SP__delete_obj_actual(p_inst_id, p_obj_name);
	ELSE -- removing all actuals with this name 
		IF( p_obj_name is null) then -- nothing to do 
			leave mac_inst_del;
		END IF;
		OPEN actual_cursor;
        read_loop: LOOP
			FETCH NEXT FROM actual_cursor INTO 
				actual_id_hold, ap_spec_id_hold, ac_id_hold;
			IF done THEN
				LEAVE read_loop;
			END IF;

			DELETE FROM actual_parmspec WHERE ap_spec_id = ap_spec_id_hold;
			DELETE FROM ari_collection WHERE ac_id = ac_id_hold;

			DELETE FROM macro_actual_definition
WHERE
    amp_core.macro_actual.actual_id = actual_id_hold;			
		END LOOP;
        CALL SP__delete_obj_actual_definition(null, p_obj_name);
    end if;
    CLOSE actual_cursor;
$$; 

-- create messages 
use amp_core;

-- ==================================================================
-- SP__insert_outgoing_message_set
-- IN 
-- 		p_created_ts integer - created timestamp
-- 		p_modified_ts integer - modified timestamp
-- 		p_state integer - state of the message set 
-- 		p_agent_id integer - agent of this message 
-- OUT 
-- 		r_set_id integer - id of the set
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_outgoing_message_set(IN p_created_ts DATETIME,
p_modified_ts DATETIME, p_state integer, p_agent_id integer, OUT r_set_id integer )
LANGUAGE SQL
AS $$
INSERT INTO amp_core.outgoing_message_set (created_ts, modified_ts, state, agent_id)
VALUES (p_created_ts, p_modified_ts, p_state, p_agent_id);

SET r_set_id = LAST_INSERT_ID();
END//



-- ==================================================================
-- SP__insert_outgoing_message_entry
-- IN 
-- 		p_set_id integer - id of the outgoing message set this entry belongs toß
--      p_message_order integer - order of this message in the set
--      p_start_ts integer - start time 
--      p_ac_id integer - ac of this message 
-- OUT 
--      r_message_id integer - id of this message
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_outgoing_message_entry(IN p_set_id integer, p_message_order integer, p_start_ts datetime, p_ac_id integer, OUT r_message_id integer)
LANGUAGE SQL
AS $$
INSERT INTO amp_core.outgoing_message_entry (set_id, message_order, start_ts, ac_id)
VALUES (p_set_id, p_message_order, p_start_ts, p_ac_id);
SET r_message_id = last_insert_id();
END//



-- ==================================================================
-- SP__update_outgoing_message_set
-- IN 
-- 		p_set_id integer - id of the set to update 
-- 		p_state integer - state of the message set 
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__update_outgoing_message_set(IN p_set_id integer, p_state integer)
LANGUAGE SQL
AS $$
	
	UPDATE amp_core.outgoing_message_set
	SET
	modified_ts = NOW(),
	state = p_state
	WHERE set_id = p_set_id;
END//



-- ==================================================================
-- SP__insert_incoming_message_set
-- IN 
-- 		p_created_ts integer - created timestamp
-- 		p_modified_ts integer - modified timestamp
-- 		p_state integer - state of the message set 
-- 		p_agent_id integer - agent of this message 
-- OUT 
-- 		r_set_id integer - id of the set
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_incoming_message_set(IN p_created_ts datetime,
p_modified_ts datetime, p_state integer, p_agent_id integer, OUT r_set_id integer)
LANGUAGE SQL
AS $$
INSERT INTO amp_core.incoming_message_set (created_ts, modified_ts, state, agent_id)
VALUES (p_created_ts, p_modified_ts, p_state, p_agent_id);

SET r_set_id = LAST_INSERT_ID();
END//


-- ==================================================================
-- SP__insert_incoming_message_entry
-- IN 
-- 		p_set_id integer - id of the outgoing message set this entry belongs toß
--      p_message_order integer - order of this message in the set
--      p_start_ts integer - start time 
--      p_ac_id integer - ac of this message 
-- OUT 
--      r_message_id integer - id of this message
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_incoming_message_entry(IN p_set_id integer, p_message_order integer, p_start_ts datetime, p_ac_id integer, OUT r_message_id integer)
LANGUAGE SQL
AS $$
INSERT INTO amp_core.incoming_message_entry (set_id, message_order, start_ts, ac_id)
VALUES (p_set_id, p_message_order, p_start_ts, p_ac_id);
SET r_message_id = last_insert_id();
END//



-- ==================================================================
-- SP__update_incoming_message_set
-- IN 
-- 		p_set_id integer - id of the set to update 
-- 		p_state integer - state of the message set 
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__update_incoming_message_set(IN p_set_id integer, p_state integer)
LANGUAGE SQL
AS $$
	
	UPDATE amp_core.incoming_message_set
	SET
	modified_ts = NOW(),
	state = p_state
	WHERE set_id = p_set_id;
END//



-- SP__insert_message_report_entry(message_id, order_num, ari_id, tnvc_id, ts)


CREATE OR REPLACE PROCEDURE SP__insert_message_report_entry(IN
       p_msg_id integer,
       p_order_num INT UNSIGNED,
       p_ari_id INT UNSIGNED,
       p_tnvc_id INT UNSIGNED,
       p_ts INT UNSIGNED,
       OUT r_obj_id integer
       )
LANGUAGE SQL
AS $$

    INSERT INTO report_definition (ari_id, ts, tnvc_id) VALUES (p_ari_id, p_ts, p_tnvc_id);
    SET r_obj_id = LAST_INSERT_ID();

    IF p_order_num IS NULL THEN
       SELECT order_num+1 INTO p_order_num FROM message_report_set_entry WHERE message_id=p_msg_id ORDER BY order_num DESC LIMIT 1;
    END IF;
    IF p_order_num IS NULL THEN
       SET p_order_num = 0;
    END IF; 

    INSERT INTO message_report_set_entry (message_id, report_id, order_num) VALUES (p_msg_id, r_obj_id, p_order_num);
    
$$;


-- SP__insert_message_group_agent_id(group_id, agent_id )


CREATE OR REPLACE PROCEDURE SP__insert_message_group_agent_id(IN
       p_group_id integer,
       p_agent INT UNSIGNED,
       OUT r_obj_id integer
       )
LANGUAGE SQL
AS $$
        INSERT INTO message_group_agents (group_id, agent_id) VALUES (p_group_id, p_agent);
        SET r_obj_id = LAST_INSERT_ID();
$$;


-- SP__insert_message_group_agent_name(group_id, agent_name)


CREATE OR REPLACE PROCEDURE SP__insert_message_group_agent_name(IN
       p_group_id integer,
       p_agent VARCHAR(128),
       OUT r_obj_id integer
       )
LANGUAGE SQL
AS $$
        DECLARE eid INT;  
        CALL SP__insert_agent(p_agent, eid); -- Select or Insert Agent ID
        INSERT INTO message_group_agents (group_id, agent_id) VALUES (p_group_id, eid);
        SET r_obj_id = LAST_INSERT_ID();

$$;


-- SP__insert_message_entry_agent( message_id, agent_name )


CREATE OR REPLACE PROCEDURE SP__insert_message_entry_agent(IN
       p_mid integer,
       p_agent VARCHAR(128)
       )
LANGUAGE SQL
AS $$
        DECLARE eid INT;  
        CALL SP__insert_agent(p_agent, eid); -- Select or Insert Agent ID
        INSERT INTO message_agents (message_id, agent_id) VALUES (p_mid, eid);

$$;



USE amp_core;

-- STORED PROCEDURE(S) For creating namespaces and adms

-- ==================================================================
-- SP__insert_namespace
--    insert a new namespace into the db
-- Parameters:
-- in 
--      p_namespace_type varchar - type of the namespace
-- 		p_issuing_org varchar - name of the issuing organization for this ADM.
-- 		p_name_string varchar- his is the human-readable name of the ADM that should appear
--           in message logs, user-interfaces, and other human-facing
--           applications
-- 		p_version varchar -This is a string representation of the version of the ADM.
--           ADM version representations are formated at the discretion of
--           the publishing organization.
-- out 
-- 		r_namespace_id integer - id of the namespace in the database 
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_namespace(IN p_namespace_type varchar, p_issuing_org varchar, p_name_string 
varchar, p_version varchar, OUT r_namespace_id integer)
LANGUAGE SQL
AS $$

    SELECT namespace_id INTO r_namespace_id
           FROM amp_core.namespace
           WHERE namespace_type=p_namespace_type AND issuing_org=p_issuing_org AND name_string=p_name_string AND version_name=p_version;
    IF (r_namespace_id IS NULL) THEN
    	INSERT INTO amp_core.namespace(namespace_type, issuing_org, name_string, version_name) VALUES(p_namespace_type, p_issuing_org, p_name_string, p_version); 
        SET r_namespace_id = LAST_INSERT_ID();
    END IF;
    
$$;



-- ==================================================================
-- SP__insert_network_defined_namespace
--    insert a new network defined adm into the db
-- Parameters:
-- in 
-- 		p_issuing_org varchar - name of the issuing organization for this ADM.
-- 		p_name_string varchar- this is the human-readable name of the ADM that should appear
--           in message logs, user-interfaces, and other human-facing
--           applications
-- 		p_version varchar -This is a string representation of the version of the ADM.
--           ADM version representations are formated at the discretion of
--           the publishing organization.
-- 		p_issuer_binary_string varchar - any string that identifies the organization that is
-- 			  defining an AMM object
-- 	    p_tag varchar - any string used to disambiguate AMM Objects for an Issuer
-- out 
-- 		r_namespace_id integer - id of the namespace in the database 
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_network_defined_namespace(IN p_issuing_org varchar, p_name_string varchar, 
p_version varchar, p_issuer_binary_string varchar, p_tag varchar, OUT r_namespace_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_namespace('NETWORK_CONFIG', p_issuing_org, p_name_string, p_version, r_namespace_id); 
    INSERT INTO amp_core.network_config(namespace_id, issuer_binary_string, tag) VALUES(r_namespace_id, p_issuer_binary_string, p_tag); 
$$;



-- ==================================================================
-- SP__insert_network_defined_namespace
--    insert a new moderated adm into the db
-- Parameters:
-- in 
-- 		p_issuing_org varchar - name of the issuing organization for this ADM.
-- 		p_name_string varchar- this is the human-readable name of the ADM that should appear
--           in message logs, user-interfaces, and other human-facing
--           applications
-- 		p_version varchar - This is a string representation of the version of the ADM.
--           ADM version representations are formated at the discretion of
--           the publishing organization.
-- 		p_adm_name_string varchar -  this is the human-readable name of the ADM that should appear
--           in message logs, user-interfaces, and other human-facing
--           applications
-- 		p_adm_enum integer - an unsigned integer in the range of 0 to
-- 			 (2^64)/20
-- 		p_adm_enum_label varchar - labeled based on the number of bytes
-- 			of the Nickname as a function of the size of the ADM enumeration
-- 		p_use_desc varchar - human readable use description
-- out
-- 		r_namespace_id integer - id of the namespace in the database 
-- ==================================================================
DROP PROCEDURE IF EXISTS SP__insert_adm_defined_namespace;

CREATE OR REPLACE PROCEDURE SP__insert_adm_defined_namespace(IN p_issuing_org varchar, p_namespace_string varchar, 
p_version varchar, p_adm_name_string varchar, p_adm_enum integer, p_adm_enum_label varchar, 
p_use_desc varchar, OUT r_namespace_id integer) 
LANGUAGE SQL
AS $$
	CALL SP__insert_namespace('MODERATED', p_issuing_org, p_namespace_string, p_version, r_namespace_id);
    INSERT INTO amp_core.adm(namespace_id, adm_name, adm_enum, adm_enum_label, use_desc) VALUES(r_namespace_id, 
    p_adm_name_string, p_adm_enum, p_adm_enum_label, p_use_desc); 
$$; 




-- ==================================================================
-- Author: David Linko	
-- 
-- Description:  inserting, updating and removing object formal and actual defintion. The backbone for the DB and all the objects that make it up. 
-- since deletes concasde if you remove the obj instance or definiton you remove that entity from the DB 
-- ==================================================================


USE amp_core;


-- ==================================================================
-- Parameters:
-- in 
-- 		p_obj_type varchar - object of the type
--      p_obj_name varchar -  human readable name of the new object
--      p_namespace_id integer - namespace this object belongs to
-- out 
-- 		r_obj_id integer - id of the new object in the database
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_obj_metadata(IN p_obj_type_id INT unsigned, p_obj_name varchar, p_namespace_id integer, OUT r_obj_id integer)
LANGUAGE SQL
AS $$

   SELECT obj_metadata_id INTO r_obj_id
              FROM amp_core.obj_metadata
              WHERE data_type_id=p_obj_type_id AND obj_name=p_obj_name AND namespace_id=p_namespace_id;

    IF (r_obj_id IS NULL) THEN
    	INSERT INTO amp_core.obj_metadata(data_type_id, obj_name, namespace_id) VALUES(p_obj_type_id, p_obj_name, p_namespace_id); 
            SET r_obj_id = LAST_INSERT_ID();
    END IF;

$$;


-- ==================================================================
-- Parameters:
-- in 
-- 		p_obj_id INT UNSIGNED - 
-- 
-- ==================================================================
DROP PROCEDURE IF EXISTS SP__delete_obj_metadata;

CREATE OR REPLACE PROCEDURE SP__delete_obj_metadata(IN p_obj_id INT UNSIGNED)
LANGUAGE SQL
AS $$ 
	DELETE FROM obj_metadata
WHERE obj_metadata_id = p_obj_id;

$$;




-- ==================================================================
-- Parameters:
-- in  
-- 		p_obj_metadata_id integer - 
-- 		p_use_desc varchar - 
-- out 
-- 		r_formal_id integer - 
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_obj_formal_definition(IN p_obj_metadata_id integer, p_use_desc varchar, OUT r_formal_id integer)
LANGUAGE SQL
AS $$

    -- Get the next available ID for automatic enumeration of new formal definitions
    SELECT data_type_id, adm_enum INTO @data_type, @adm_enum FROM vw_obj_metadata WHERE obj_metadata_id=p_obj_metadata_id;
    SELECT COALESCE(MAX(vof.obj_enum)+1,0) INTO @obj_enum FROM vw_obj_formal_def vof WHERE vof.data_type_id=@data_type AND vof.adm_enum=@adm_enum;      

	INSERT INTO amp_core.obj_formal_definition(obj_metadata_id, use_desc, obj_enum) VALUES(p_obj_metadata_id, p_use_desc, @obj_enum);
    
    SET r_formal_id = LAST_INSERT_ID();
$$;




-- ==================================================================
-- Parameters:
-- in IN p_obj_metadata_id integer, p_use_desc varchar, OUT r_actual_id integer)
--
-- out 
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_obj_actual_definition(IN p_obj_metadata_id integer, p_use_desc varchar, OUT r_actual_id integer)
LANGUAGE SQL
AS $$
	INSERT INTO amp_core.obj_actual_definition(obj_metadata_id, use_desc) VALUES(p_obj_metadata_id, p_use_desc); 
    SET r_actual_id = LAST_INSERT_ID();
$$;


-- ==================================================================
-- can use name or id for to delete 
-- Parameters:
-- in 
-- 		p_obj_id integer - Id of the specific obj to delete 
-- 		p_obj_name varchar - name of the obj to delete 
-- ==================================================================

 
CREATE OR REPLACE PROCEDURE SP__delete_obj_formal_definition(p_obj_id integer, p_obj_name varchar )
obj_delete:LANGUAGE SQL
AS $$
	IF( p_obj_id is NULL AND p_obj_name is not NULL) THEN
		SET p_obj_id =  (select obj_id FROM amp_core.obj_metadata WHERE obj_name = p_obj_name);
    ELSE 
		LEAVE obj_delete;
    END IF;
    
	DELETE FROM amp_core.obj_metadata WHERE obj_id = p_obj_id;
END//

 

-- ==================================================================
-- Parameters:
-- in 
-- 		p_act_id int UNSIGNED
--  	p_obj_name varchar
-- 		p_namespace_id int UNSIGNED 
--
-- ==================================================================
-- for just removing the obj instance 
-- two options for removal if you want to remove a specific instance you can specify the instance id, 
-- or if you want to remove all the instances of a specific definition you can supply the definition name
-- TODO: can add another option of adding a number and only removes up to that number of entries.
-- maybe too overloaded
DROP PROCEDURE IF EXISTS SP__delete_obj_actual_definition;

CREATE OR REPLACE PROCEDURE SP__delete_obj_actual_definition(p_act_id int UNSIGNED, p_obj_name varchar ) 
obj_inst_del:LANGUAGE SQL
AS $$ 

	-- if its just removing one instance 
	IF( p_inst_id is not null) THEN
		DELETE FROM obj_actual_definition WHERE actual_definition_id = p_act_id;
    -- if its removing all instances with this defeintion
	ELSE -- removing all instances with this name 
		IF( p_obj_name is null or p_namespace_id) then -- nothing to do 
			leave obj_inst_del;
		END IF;
		DELETE FROM amp_core.obj_actual_definition where obj_metadata_id =(select obj_metadata_id from obj_metadat where obj_name =  p_obj_name ); 
	END IF;
END//

USE amp_core;

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
p_result_type varchar, p_num_inputs integer, p_tnvc_id integer,  OUT r_definition_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_actual_definition(p_obj_id, p_use_desc, r_definition_id);
    INSERT INTO amp_core.operator_actual_definition(obj_actual_definition_id, data_type_id, num_operands, tnvc_id)
    VALUES(r_definition_id, (SELECT data_type_id FROM amp_core.data_type WHERE type_name = p_result_type), p_num_inputs, p_tnvc_id); 
$$;


-- ==================================================================
-- SP__delete_oper_actual_defintion
-- IN 
-- 		p_obj_id integer - id of this op to delete,  
-- 		p_obj_name varchar - name of this op to delete 
-- ==================================================================
DROP PROCEDURE IF EXISTS SP__delete_oper_actual_defintion;
 
CREATE OR REPLACE PROCEDURE SP__delete_oper_actual_defintion(IN p_obj_id integer, p_obj_name varchar)
oper_def_del:LANGUAGE SQL
AS $$
	IF( p_obj_id is Null AND p_obj_name is not NULL) THEN
		SET p_obj_id =  (select obj_id FROM amp_core.obj_metadata WHERE obj_name = p_obj_name);
    ELSE 
		LEAVE oper_def_del;
    END IF;
    
    SET @def_id = (select definition_id from obj_actual_definition where obj_actual_definition_id = p_obj_id);
	SET @fp_id = (SELECT fp_spec_id from macro_actual_definition where obj_actual_definition_id = @def_id );
    SET @ac_id = (SELECT ac_id FROM macro_actual_definition where obj_actual_definition_id = @def_id );
    
	DELETE FROM formal_parmspec WHERE fp_spec_id = @fp_id;
	DELETE FROM ari_collection WHERE ac_id = @ac_id;

	CALL SP__delete_obj_actual_defintion(p_obj_id, p_obj_name);
$$; 






USE amp_core;

-- STORED PROCEDURE(S) for the creating updating and deleting reports and report templates


-- auto adds ac which can be troublesome 
-- user has to make ac first 
/*
DROP PROCEDURE IF EXISTS SP__insert_report_template_metadata_format;

CREATE OR REPLACE PROCEDURE SP__insert_report_template_metadata_format(IN p_metadata_count integer, p_metadata_types_list varchar, p_metadata_names_list varchar, p_metadata_desc varchar, OUT r_tnvc_id integer)
LANGUAGE SQL
AS $$
	INSERT INTO amp_core.type_name_value_collection(num_entries, use_desc) VALUES(p_metadata_count, p_metadata_desc); 
    SET r_tnvc_id = LAST_INSERT_ID();
	SET @s = 'INSERT INTO amp_core.type_name_value(tnvc_id, data_type, data_name, order_num) VALUES'; 
    SET @loops = 1; 
    WHILE @loops < p_metadata_count DO 
		LANGUAGE SQL
AS $$
			-- @metadata_type
				SET @metadata_type = TRIM(SUBSTRING_INDEX(p_metadata_types_list, ',', 1));
				SET p_metadata_types_list = REPLACE(p_metadata_types_list, CONCAT(@metadata_type, ','), ''); 
    
 			-- @metadata_name
				SET @metadata_name = TRIM(SUBSTRING_INDEX(p_metadata_names_list, ',', 1)); 
				SET p_metadata_names_list = REPLACE(p_metadata_names_list, CONCAT(@metadata_name, ','), '');
                
				SET @s = CONCAT(@s, '(', r_tnvc_id, ',', (SELECT enum_id FROM amp_core.data_type WHERE type_name = @metadata_type), ',', '\'', @metadata_name, '\'', ',', @loops, '),');
                SET @loops = @loops + 1; 
        END; 
    END WHILE; 
 
    -- @metadata_type
	SET @metadata_type = TRIM((SUBSTRING_INDEX(p_metadata_types_list, ',', 1)));
    
	-- @metadata_name
	SET @metadata_name = TRIM(SUBSTRING_INDEX(p_metadata_names_list, ',', 1)); 

	SET @s = CONCAT(@s, '(', r_tnvc_id, ',', (SELECT enum_id FROM amp_core.data_type WHERE type_name = @metadata_type), ',', '\'', @metadata_name, '\'', ',', @loops, ');');
	PREPARE stmt FROM @s; 
    EXECUTE stmt; 
	
$$;
 
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


CREATE OR REPLACE PROCEDURE SP__insert_report_template_formal_definition(IN p_obj_id integer, p_use_desc varchar, p_formal_parmspec_id integer, p_ac_id integer, OUT r_definition_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_formal_definition(p_obj_id, p_use_desc, r_definition_id); 
    INSERT INTO amp_core.report_template_formal_definition(obj_formal_definition_id, fp_spec_id, ac_id) VALUES(r_definition_id, p_formal_parmspec_id, p_ac_id); 
$$;



-- ==================================================================
-- SP__insert_report_actual_definition 
-- IN 
-- 		p_obj_definition_id integer - metadata id for this report
-- 		p_ap_spec_id integer - id for the actual parmspec for this report 
-- 		p_use_desc varchar - human readable use description
-- 	OUT 
-- 		r_obj_actual_id integer - id of this actual report definition
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_report_actual_definition(IN p_obj_definition_id integer, p_ap_spec_id integer, p_ts TIMESTAMP, p_use_desc varchar, OUT r_obj_actual_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_actual_definition(p_obj_definition_id, p_use_desc, r_obj_actual_id); 
    INSERT INTO amp_core.report_template_actual_definition(obj_actual_definition_id, ap_spec_id, ts ) VALUES(r_obj_actual_id, p_ap_spec_id, p_ts);
$$; 
 
USE amp_core;

-- STORED PROCEDURE(S) for adding updating and deleting time base rule defintions and instances 

-- =================
-- for adding state based rules into the database 
-- SP__insert_sbr_actual_definition 
-- IN 
-- 		p_obj_id integer - metadata id of this SBR
-- 		p_use_desc varchar- human readable description
-- 		p_expr_id int UNSIGNED, - id of the expresion for this rule
-- 		p_ac_id int UNSIGNED, - id of the ari collection that defines the action of this rule 
-- 		p_start_time time - whem this rule starts 
-- OUT 
-- 		r_definition_id integer - id of the start 
-- ====================================


CREATE OR REPLACE PROCEDURE SP__insert_sbr_actual_definition(IN p_obj_id integer, p_use_desc varchar,  p_expr_id int UNSIGNED, p_ac_id int UNSIGNED, p_start_time time , OUT r_definition_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_actual_definition(p_obj_id, p_use_desc, r_definition_id); 
    INSERT INTO amp_core.sbr_actual_definition(obj_actual_definition_id, expression_id, run_count, start_time, ac_id) VALUES(r_definition_id, p_expr_id, p_run_count, p_start_time, p_ac_id);
$$;



-- ==================================================================
-- SP__delete_sbr_actual_definition;
-- Parameters:
-- in 
--      p_obj_id integer - id for the sbr to delete 
-- 		p_obj_name varchar -  name of the sbr to delete --
-- ==================================================================
DROP PROCEDURE IF EXISTS SP__delete_sbr_actual_definition;
 
CREATE OR REPLACE PROCEDURE SP__delete_sbr_actual_definition(IN p_obj_id integer, p_obj_name varchar)
sbr_def_del:LANGUAGE SQL
AS $$
	IF( p_obj_id is Null AND p_obj_name is not NULL) THEN
		SET p_obj_id =  (select obj_id FROM amp_core.obj_metadata WHERE obj_name = p_obj_name);
    ELSE 
		LEAVE sbr_def_del;
    END IF;
    
    IF(p_obj_name is NULL) THEN
		SET p_obj_name = (select obj_name from vw_sbr_formal where obj_id = p_obj_id);
    END IF ;
    
	SET @exp_id = (SELECT expression_id FROM vw_sbr_actual WHERE obj_actual_definition = p_obj_id); 
	SET @ac_id = (SELECT ac_id FROM vw_sbr_actual WHERE obj_actual_definition = p_obj_id); 
	
    DELETE FROM ari_collection WHERE ac_id = @ac_id;
    DELETE FROM expression WHERE expression_id = @exp_id;
	
    CALL SP__delete_obj_atual_defintion(p_obj_id, p_obj_name);
$$;

USE amp_core;

-- STORED PROCEDURE(S)


-- ==
-- function for string processing used by other sp
-- help make inserting large sets of data more user friendly 
-- ==


CREATE OR REPLACE PROCEDURE SP__get_delimiter_position(IN p_str varchar, p_delimiter varchar, p_start_position integer, OUT r_found_position integer)
LANGUAGE SQL
AS $$
	IF (p_str IS NOT NULL) && (p_start_position IS NOT NULL)THEN 
		LANGUAGE SQL
AS $$
			SET @length = CHAR_LENGTH(p_str); 
			SET @position_index = p_start_position; 
            SET @iterator_index = p_start_position; 
            SET @char_value = ''; 
            SET @delimiter_found = FALSE; 
            SET r_found_position = NULL; 
			WHILE (@position_index != @length) && (@delimiter_found != TRUE) DO 
				LANGUAGE SQL
AS $$
					SET @char_value = SUBSTRING(p_str, @iterator_index, 1);
                    IF @char_value LIKE p_delimiter THEN 
						SET @position_index = @iterator_index;
                        SET r_found_position = @position_index; 
                        SET @delimiter_found = TRUE; 
                    END IF; 
                    SET @iterator_index = @iterator_index + 1; 
				END;
			END WHILE; 
		END; 
    ELSE 
		LANGUAGE SQL
AS $$
			SET r_found_position = NULL; 
        END; 
    END IF; 
$$;




CREATE OR REPLACE PROCEDURE SP__null_string_check(INOUT p_string varchar)
LANGUAGE SQL
AS $$
	IF (p_string LIKE 'null') || (p_string LIKE 'NULL') || (p_string LIKE 'Null') THEN
		LANGUAGE SQL
AS $$
			SET p_string = NULL; 
        END; 
    END IF; 
$$;
USE amp_core;

-- STORED PROCEDURE(S) for adding deleting and updating Table template defintions and instances 


-- ==================================================================
-- SP__insert_table_template_actual_definition
-- IN
-- 		p_obj_id integer - obj_metadata id
-- 		p_use_desc varchar - human readble use desc
-- 		p_num_columns integer -  number of columns in the table
-- 		p_column_names_list varchar(10000) -  list of column names 
-- 		p_column_types_list varchar(10000) - list of column type
-- OUT 
-- 		r_definition_id integer - id of the the new table
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__insert_table_template_actual_definition(IN p_obj_id integer, p_use_desc varchar, p_columns_id integer, OUT r_definition_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_actual_definition(p_obj_id, p_use_desc, r_definition_id);
    INSERT INTO amp_core.table_template_actual_definition(obj_actual_definition_id, tnvc_id) VALUES(r_definition_id, p_columns_id); 
$$;


-- ==================================================================
-- SP__insert_table_template_actual_definition 
-- IN 
-- 		p_obj_id integer - id of the table to delete 
-- 		p_obj_name varchar -- name of the object to delete 
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__delete_table_template_actual_definition(IN p_obj_id integer)
LANGUAGE SQL
AS $$
	IF p_obj_id != NULL THEN LANGUAGE SQL
AS $$
		SET @tnvc_id = (select tnvc_id from table_template_actual_definition where obj_actual_definition_id = p_obj_id);
	END;
	ELSE LANGUAGE SQL
AS $$
		SET @tnvc_id = 
			(select tnvc_id from table_template_actual_definition where obj_atual_definition_id = 
				(select obj_actual_definition_id  from obj_actual_definition where obj_metadata_id = 
					(select obj_metadata_id from obj_metadata where obj_name = p_obj_name)));
	END;
   END IF;
   CALL SP__delete_tnvc(@tnvc_id);
   CALL SP__delete_obj_actual_definition(p_obj_id, null);
   
$$;




-- 
-- 
-- -- table_definition_id,  use_desc, 
-- CREATE OR REPLACE PROCEDURE SP__insert_table_instance(IN p_obj_definition_id integer,  p_use_desc varchar, p_row_values_list varchar(10000), OUT r_instance_id integer)
-- LANGUAGE SQL
AS $$
-- 	
--     -- have to visit how to store multiple rows is is just one long value collection splitting at every num_colmns?
-- 	CALL SP__insert_obj_instance(p_obj_definition_id, p_use_desc, r_instance_id); 
--     SET @n_rows = (select num_entries from amp_core.type_name_value_collection where tnvc_id =(select columns_list from amp_core.table_template_definition where definition_id = p_obj_definition_id));
--     CALL  SP__insert_tnv_collection(@num_rows, null, null, p_row_values_list , @tnvc_id);  
--     INSERT INTO amp_core.table_instance(instance_id, ap_spec_id) VALUES(r_instance_id, p_ap_spec_id);   
-- $$;
-- 
USE amp_core;

-- STORED PROCEDURE(S) for adding updating and deleting time base rule defintions and instances 
-- need type checking for actions, they need to be Macros or controls


-- ===============================================================
-- SP__insert_tbr_actual_definition 
-- IN
-- 		p_obj_id integer - metadata id
-- 		p_use_desc varchar - human readable descriptionb
-- 		p_wait_per time  - how long to wait before starting 
-- 		p_run_count biginteger - number of times to run 
-- 		p_start_time time - when to start 
-- 		p_ac_id int UNSIGNED - ac of the actions for this rules 
-- OUT 
-- 		r_definition_id integer - id of this tbr
-- ===============================================================


CREATE OR REPLACE PROCEDURE SP__insert_tbr_actual_definition(IN p_obj_id integer, p_use_desc varchar, 
p_wait_per time, p_run_count biginteger, p_start_time time, p_ac_id int UNSIGNED, OUT r_definition_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_actual_definition(p_obj_id, p_use_desc, r_definition_id); 
    INSERT INTO amp_core.tbr_actual_definition(obj_actual_definition_id, wait_period, run_count, start_time, ac_id) VALUES(r_definition_id, p_wait_per, p_run_count, p_start_time, p_ac_id);
$$;




-- ==================================================================
-- SP__delete_tbr_actual_definition;
-- Parameters:
-- in 
--      p_obj_id integer - id for the tbr to delete 
-- 		p_obj_name varchar -  name of the tbr to delete --
-- ==================================================================
DROP PROCEDURE IF EXISTS SP__delete_tbr_actual_definition;
 
CREATE OR REPLACE PROCEDURE SP__delete_tbr_actual_definition(IN p_obj_id integer, p_obj_name varchar)
tbr_def_del:LANGUAGE SQL
AS $$
	IF( p_obj_id is Null AND p_obj_name is not NULL) THEN
		SET p_obj_id =  (select obj_id FROM amp_core.obj_metadata WHERE obj_name = p_obj_name);
    ELSE 
		LEAVE tbr_def_del;
    END IF;
    
    IF(p_obj_name is NULL) THEN
		SET p_obj_name = (select obj_name from vw_tbr_formal where obj_id = p_obj_id);
    END IF ;
    

	SET @ac_id = (SELECT ac_id FROM vw_tbr_actual WHERE obj_actual_definition = p_obj_id); 
	
    DELETE FROM ari_collection WHERE ac_id = @ac_id;
	
    CALL SP__delete_obj_atual_defintion(p_obj_id, p_obj_name);
$$;
USE amp_core;

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


CREATE OR REPLACE PROCEDURE SP__insert_tnvc_collection(IN p_use_desc varchar, OUT r_tnvc_id integer)
LANGUAGE SQL
AS $$
	INSERT INTO amp_core.type_name_value_collection(use_desc) VALUES(p_use_desc);
    SET r_tnvc_id = LAST_INSERT_ID();
$$;


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


CREATE OR REPLACE PROCEDURE SP__insert_tnvc_entry(IN p_tnvc_id integer, p_order_num integer, p_data_type_name varchar, p_data_name varchar, OUT r_tnvc_entry_id integer)
LANGUAGE SQL
AS $$

    IF p_order_num IS NULL THEN
       SELECT order_num+1 INTO p_order_num FROM type_name_value_entry WHERE tnvc_id=p_tnvc_id ORDER BY order_num DESC LIMIT 1;
    END IF;
    IF p_order_num IS NULL THEN
       SET p_order_num = 0;
    END IF; 


	INSERT INTO `amp_core`.`type_name_value_entry`
(`tnvc_id`,
`order_num`,
`data_type_id`,
`data_name`)
VALUES
(p_tnvc_id,
p_order_num,
(SELECT data_type_id FROM data_type WHERE type_name = UPPER(p_data_type_name)),
p_data_name);

SET r_tnvc_entry_id = LAST_INSERT_ID();

$$;




CREATE OR REPLACE PROCEDURE SP__insert_tnvc_entry_id(IN p_tnvc_id integer, p_order_num integer, p_data_type_id integer, p_data_name varchar, OUT r_tnvc_entry_id integer)
LANGUAGE SQL
AS $$

    IF p_order_num IS NULL THEN
       SELECT order_num+1 INTO p_order_num FROM type_name_value_entry WHERE tnvc_id=p_tnvc_id ORDER BY order_num DESC LIMIT 1;
    END IF;
    IF p_order_num IS NULL THEN
       SET p_order_num = 0;
    END IF; 


INSERT INTO `amp_core`.`type_name_value_entry`
(`tnvc_id`,
`order_num`,
`data_type_id`,
`data_name`)
VALUES
(p_tnvc_id,
p_order_num,
p_data_type_id,
p_data_name);

SET r_tnvc_entry_id = LAST_INSERT_ID();

$$;


-- ==================================================================
--  SP__insert_tnvc_obj_entry
--  insert a new tnvc entry that is an ADM object
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   integer - id for this actual object
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_obj_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_obj_entry(IN p_tnvc_id integer,
                                                  p_order_num integer,
                                                  p_data_type varchar,
                                                  p_entry_value integer,
                                                  OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry(p_tnvc_id, p_order_num, p_data_type, NULL, r_tnvc_entry_id);
    INSERT INTO type_name_value_obj_entry (tnv_id, obj_actual_definition_id) VALUES (r_tnvc_entry_id, p_entry_value);
$$;



DROP PROCEDURE IF EXISTS SP__insert_tnvc_ac_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_ac_entry(IN p_tnvc_id integer,
                                                  p_order_num integer,
                                                  p_data_name varchar,
                                                  p_entry_value integer,
                                                  OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$

    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 37, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_ac_entry (tnv_id, ac_id) VALUES (r_tnvc_entry_id, p_entry_value);
$$;


DROP PROCEDURE IF EXISTS SP__insert_tnvc_tnvc_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_tnvc_entry(IN p_tnvc_id integer,
                                                  p_order_num integer,
                                                  p_data_name varchar, 
                                                  p_entry_value integer,
                                                  OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 35, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_tnvc_entry (tnv_id, tnvc_id) VALUES (r_tnvc_entry_id, p_entry_value);
$$;



-- ==================================================================
--  SP__insert_tnvc_ari_entry
--  insert a new tnvc entry that is an ADM object
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   integer - id for this actual object
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_ari_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_ari_entry(IN p_tnvc_id integer,
                                                  p_order_num integer,
                                                  p_data_name varchar,
                                                  p_entry_value integer,
                                                  OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry(p_tnvc_id, p_order_num, 'ari', p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_obj_entry (tnv_id, obj_actual_definition_id) VALUES (r_tnvc_entry_id, p_entry_value);
$$;


-- ==================================================================
--  SP__insert_tnvc_unk_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_unk_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_unk_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry(p_tnvc_id, p_order_num, 'unk', p_data_name, r_tnvc_entry_id);
$$;



-- ==================================================================
--  SP__insert_tnvc_int_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   int- value for this int_entry
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_int_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_int_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value int, OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 19, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_int_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
$$;


-- ==================================================================
--  SP__insert_tnvc_uint_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   integer - value for this uint_entry
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_uint_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_uint_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value integer , OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 20, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_uint_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
$$;


-- ==================================================================
--  SP__insert_tnvc_vast_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   bigint - value for this vast_entry
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_vast_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_vast_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value bigint , OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 21, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_vast_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
$$;


-- ==================================================================
--  SP__insert_tnvc_uvast_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   biginteger - value for this uvast_entry
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_uvast_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_uvast_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value biginteger , OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 22, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_uvast_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
$$;


-- ==================================================================
--  SP__insert_tnvc_tv_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   biginteger - value for this uvast_entry
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_tv_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_tv_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value biginteger , OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 32, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_uvast_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
$$;


-- ==================================================================
--  SP__insert_tnvc_uvast_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   biginteger - value for this uvast_entry
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_ts_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_ts_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value biginteger , OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 33, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_uvast_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
$$;


-- ==================================================================
--  SP__insert_tnvc_real32_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   float- value for this real32_entry
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_real32_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_real32_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value float, OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 23, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_real32_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
$$;


-- ==================================================================
--  SP__insert_tnvc_real64_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   double- value for this real64_entry
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_real64_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_real64_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value double, OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 24, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_real64_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
$$;


-- ==================================================================
--  SP__insert_tnvc_str_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   varchar- value for this string_entry
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_str_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_str_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value varchar, OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 18, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_string_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
$$;


-- ==================================================================
--  SP__insert_tnvc_bool_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   bool- value for this bool_entry
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_bool_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_bool_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value bool, OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 16, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_bool_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
$$;


-- ==================================================================
--  SP__insert_tnvc_byte_entry
--  insert a new tnvc entry for the specific primitive data type
--  in
--      p_tnv_entry_id integer - the id for this tnv entry
--      p_entry_value   tinyint- value for this byte_entry
-- ================================================================== 
DROP PROCEDURE IF EXISTS SP__insert_tnvc_byte_entry;

CREATE OR REPLACE PROCEDURE SP__insert_tnvc_byte_entry(IN p_tnvc_id integer, p_order_num integer,  p_data_name varchar,  p_entry_value tinyint, OUT r_tnvc_entry_id integer )
LANGUAGE SQL
AS $$
    CALL SP__insert_tnvc_entry_id(p_tnvc_id, p_order_num, 17, p_data_name, r_tnvc_entry_id);
    INSERT INTO type_name_value_byte_entry (tnv_id, entry_value) VALUES (r_tnvc_entry_id, p_entry_value);
$$;







-- ==================================================================
-- SP__insert_tnv_collection
-- inserts entries into the collection using ',' lists
-- IN
-- 		p_num_entries integer - number of entries in the collection
-- 		p_data_types_list varchar(10000) - list of the data types  
-- 		p_data_names_list varchar(10000) - list of the names
-- 		p_data_values_list varchar(10000) - list of the values
-- OUT 
-- 		r_tnvc_id integer - id of the collection
-- ==================================================================
-- 
-- 
-- CREATE OR REPLACE PROCEDURE SP__insert_tnv_collection(IN p_num_entries integer, p_data_types_list varchar(10000), p_data_names_list varchar(10000), p_data_values_list varchar(10000), OUT r_tnvc_id integer)
-- LANGUAGE SQL
AS $$ 
-- 	CALL SP__insert_tnvc(p_num_entries, r_tnvc_id); 
--     SET @tnvc_id = r_tnvc_id; 
--     SET @s = 'INSERT INTO amp_core.type_name_value(tnvc_id, order_num, data_type_id, data_name, obj_actual_definition_id) VALUES'; 
--     SET @loops = 1; 
--     WHILE @loops < p_num_entries DO 
-- 		LANGUAGE SQL
AS $$
-- 			-- @data_type
-- 				IF p_data_types_list IS NOT NULL THEN 
-- 					LANGUAGE SQL
AS $$ 
-- 						SET @data_type = TRIM(SUBSTRING_INDEX(p_data_types_list, ',', 1));
-- 						SET p_data_types_list = REPLACE(p_data_types_list, CONCAT(@data_type, ','), '');
-- 				    END; 
-- 				ELSE 
-- 					LANGUAGE SQL
AS $$
-- 						SET @data_type = 'NULL'; 
--                     END; 
-- 				END IF;
--                 
--  			-- @data_name
-- 				IF p_data_names_list IS NOT NULL THEN 
-- 					LANGUAGE SQL
AS $$ 
-- 						SET @data_name = TRIM(SUBSTRING_INDEX(p_data_names_list, ',', 1)); 
-- 						SET p_data_names_list = REPLACE(p_data_names_list, CONCAT(@data_name, ','), '');
--                     END;
-- 				ELSE 
-- 					LANGUAGE SQL
AS $$
-- 						SET @data_name = 'NULL'; 
--                     END; 
--                 END IF;
--                 
--             -- @data_value
-- 				IF p_data_values_list IS NOT NULL THEN 
-- 					LANGUAGE SQL
AS $$ 
-- 						SET @data_value = TRIM(SUBSTRING_INDEX(p_data_values_list, ',', 1));
-- 						SET p_data_values_list = REPLACE(p_data_values_list, CONCAT(@data_value, ','), '');
--                     END;
-- 				ELSE 
-- 					LANGUAGE SQL
AS $$
-- 						SET @data_value = 'NULL'; 
--                     END; 
-- 				END IF; 
-- 				SET @s = CONCAT(@s, '(', @tnvc_id, ',', @loops, ',', (SELECT data_type_id FROM amp_core.data_type WHERE type_name = @data_type), ',', '"', @data_name, '"', ',', '"', @data_value, '"', '),');
--                 SET @loops = @loops + 1; 
--         END; 
--     END WHILE; 
--  
--     -- @data_type
--     IF p_data_types_list IS NOT NULL THEN
-- 		LANGUAGE SQL
AS $$ 
-- 			SET @data_type = TRIM((SUBSTRING_INDEX(p_data_types_list, ',', 1)));
-- 		END; 
--     ELSE
-- 		LANGUAGE SQL
AS $$
-- 			SET @data_type = 'NULL'; 
--         END; 
--     END IF; 
--     
-- 	-- @data_name
--     IF p_data_names_list IS NOT NULL THEN
-- 		LANGUAGE SQL
AS $$ 
-- 			SET @data_name = TRIM(SUBSTRING_INDEX(p_data_names_list, ',', 1));
-- 		END;
-- 	ELSE 
-- 		LANGUAGE SQL
AS $$
-- 			SET @data_name = 'NULL'; 
--         END; 
-- 	END IF; 
--     
-- 	-- @data_value
--     IF p_data_values_list IS NOT NULL THEN
-- 		LANGUAGE SQL
AS $$ 
-- 			SET @data_value = TRIM(SUBSTRING_INDEX(p_data_values_list, ',', 1));
-- 		END; 
-- 	ELSE
-- 		LANGUAGE SQL
AS $$
-- 			SET @data_value = 'NULL'; 
--         END; 
--     END IF; 
-- 	SET @s = CONCAT(@s, '(', @tnvc_id, ',', @loops, ',', (SELECT data_type_id FROM amp_core.data_type WHERE type_name = @data_type), ',', '"', @data_name, '"', ',', '"', @data_value, '"', ')');
-- 	PREPARE stmt FROM @s; 
--     EXECUTE stmt; 

-- $$;
-- 

USE amp_core;

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
p_out_type integer,  p_expression_id integer, OUT r_definition_id integer)
LANGUAGE SQL
AS $$
	CALL SP__insert_obj_actual_definition(p_obj_id, p_use_desc, r_definition_id);
	-- call expresion builder for var Initializer
    CALL SP__insert_expression(p_out_type, p_expression_id, @r_expr_id);
	INSERT INTO amp_core.variable_actual_definition(obj_actual_definition_id, data_type_id, expression_id) VALUES(r_definition_id, p_out_type, @r_expr_id); 

$$;



-- ==================================================================
-- SP__delete_var_actual_definition;
-- Parameters:
-- in 
--      p_obj_id integer - id for the var to delete 
-- 		p_obj_name varchar -  name of the var to delete --
-- ==================================================================


CREATE OR REPLACE PROCEDURE SP__delete_variable_definition(IN p_definition_id integer, p_obj_name varchar)
LANGUAGE SQL
AS $$
	-- delete the expresion first
    SET @exp_id = (SELECT expression_id from variable_actual_definition where p_definition_id = obj_actual_definition);
    CALL SP__delete_expression(@exp_id);
    CALL SP__delete_obj_actual_definition(p_obj_id, p_use_desc, r_definition_id);
	
$$;

# for testing the delete function 

USE amp_core;

set @p_obj_name = 'bundles_by_priority';
select * from obj_definition join obj_identifier on obj_definition.obj_id = obj_identifier.obj_id;
-- select definition_id from obj_definition where obj_id = (SELECT obj_id FROM amp_core.obj_identifier WHERE obj_name = @p_obj_name);

-- set  @fp_spec_id_control_definitionobj_definitionformal_parmspecedd1 = (select fp_spec_id from amp_core.edd_definition where definition_id = (select definition_id from obj_definition where obj_id = (SELECT obj_id FROM amp_core.obj_identifier WHERE obj_name = @p_obj_name)));
-- CALL SP__insert_actual_parms_set(1, @fp_spec_id_edd1, 'UINT', '1', @ap_spec_id); 
-- CALL SP__insert_edd_instance(@edd_definition_id_9, @ap_spec_id,NULL, @edd_inst_id_1);


-- Select * from amp_core.obj_definition;
-- SELECT obj_id FROM amp_core.obj_identifier WHERE obj_name = @p_obj_name;
-- SELECT * from amp_core.obj_definition where obj_id = (SELECT obj_id FROM amp_core.obj_identifier WHERE obj_name = @p_obj_name);

SELECT * FROM vw_edd_instance;
-- CALL SP__delete_obj_definition(0, null, @p_obj_name);
call SP__delete_edd_instance(null, 'bundles_by_priority');
-- CALL SP__delete_edd_instance(null, @p_o-- bj_name);

SELECT * FROM vw_edd_instance;


