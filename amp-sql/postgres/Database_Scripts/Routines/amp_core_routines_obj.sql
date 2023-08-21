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

-- ==================================================================
-- Author: David Linko	
-- 
-- Description:  inserting, updating and removing object formal and actual defintion. The backbone for the DB and all the objects that make it up. 
-- since deletes concasde if you remove the obj instance or definiton you remove that entity from the DB 
-- ==================================================================


-- ==================================================================
-- Parameters:
-- in 
-- 		p_obj_type varchar - object of the type
--      p_obj_name varchar -  human readable name of the new object
--      p_namespace_id integer - namespace this object belongs to
-- out 
-- 		r_obj_id integer - id of the new object in the database
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_obj_metadata(IN p_obj_type_id integer, p_obj_name varchar, p_namespace_id integer, INOUT r_obj_id integer)
LANGUAGE plpgsql
AS $$ BEGIN

   SELECT obj_metadata_id INTO r_obj_id
              FROM obj_metadata
              WHERE data_type_id=p_obj_type_id AND obj_name=p_obj_name AND namespace_id=p_namespace_id;

    IF (r_obj_id IS NULL) THEN
    	INSERT INTO obj_metadata(data_type_id, obj_name, namespace_id) VALUES(p_obj_type_id, p_obj_name, p_namespace_id) RETURNING obj_metadata_id into r_obj_id;
      
    END IF;

end$$;


-- ==================================================================
-- Parameters:
-- in 
-- 		p_obj_id integer - 
-- 
-- ==================================================================

CREATE OR REPLACE PROCEDURE SP__delete_obj_metadata(IN p_obj_id integer)
LANGUAGE plpgsql
AS $$ BEGIN 
	DELETE FROM obj_metadata
WHERE obj_metadata_id = p_obj_id;

end$$;




-- ==================================================================
-- Parameters:
-- in  
-- 		p_obj_metadata_id integer - 
-- 		p_use_desc varchar - 
-- out 
-- 		r_formal_id integer - 
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_obj_formal_definition(IN p_obj_metadata_id integer, p_use_desc varchar, INOUT r_formal_id integer)
LANGUAGE plpgsql

AS $$ 
DECLARE
 data_type integer;
 adm_enum_this INTEGER;
 obj_enum integer;

BEGIN

    -- Get the next available ID for automatic enumeration of new formal definitions
    SELECT data_type_id, vw_obj_metadata.adm_enum INTO data_type, adm_enum_this FROM vw_obj_metadata WHERE obj_metadata_id=p_obj_metadata_id;
    SELECT COALESCE(MAX(vof.obj_enum)+1,0) INTO obj_enum FROM vw_obj_formal_def vof WHERE vof.data_type_id=data_type AND vof.adm_enum=adm_enum_this;      

	INSERT INTO obj_formal_definition(obj_metadata_id, use_desc, obj_enum) VALUES(p_obj_metadata_id, p_use_desc, obj_enum) RETURNING obj_formal_definition_id INTO r_formal_id;
end$$;




-- ==================================================================
-- Parameters:
-- in IN p_obj_metadata_id integer, p_use_desc varchar, INOUT r_actual_id integer)
--
-- out 
-- ==================================================================
CREATE OR REPLACE PROCEDURE SP__insert_obj_actual_definition(IN p_obj_metadata_id integer, p_use_desc varchar, INOUT r_actual_id integer)
LANGUAGE plpgsql
AS $$ BEGIN
	INSERT INTO obj_actual_definition(obj_metadata_id, use_desc) VALUES(p_obj_metadata_id, p_use_desc) RETURNING  obj_actual_definition_id INTO r_actual_id;
end$$;


-- ==================================================================
-- can use name or id for to delete 
-- Parameters:
-- in 
-- 		p_obj_id integer - Id of the specific obj to delete 
-- 		p_obj_name varchar - name of the obj to delete 
-- ================================================================== 
CREATE OR REPLACE PROCEDURE SP__delete_obj_formal_definition(p_obj_id integer, p_obj_name varchar )
LANGUAGE plpgsql

AS $$ 
<<obj_delete>>
BEGIN
	IF( p_obj_id is NULL AND p_obj_name is not NULL) THEN
		select obj_id FROM obj_metadata WHERE obj_name = p_obj_name into p_obj_id;
    ELSE 
		exit obj_delete;
    END IF;
    
	DELETE FROM obj_metadata WHERE obj_id = p_obj_id;
END$$;

 

-- ==================================================================
-- Parameters:
-- in 
-- 		p_act_id integer
--  	p_obj_name varchar
-- 		p_namespace_id integer 
--
-- ==================================================================
-- for just removing the obj instance 
-- two options for removal if you want to remove a specific instance you can specify the instance id, 
-- or if you want to remove all the instances of a specific definition you can supply the definition name
-- TODO: can add another option of adding a number and only removes up to that number of entries.
-- maybe too overloaded
CREATE OR REPLACE PROCEDURE SP__delete_obj_actual_definition(p_act_id integer, p_obj_name varchar ) 
LANGUAGE plpgsql
AS $$ 
<<obj_inst_del>>
BEGIN 

	-- if its just removing one instance 
	IF( p_inst_id is not null) THEN
		DELETE FROM obj_actual_definition WHERE actual_definition_id = p_act_id;
    -- if its removing all instances with this defeintion
	ELSE -- removing all instances with this name 
		IF( p_obj_name is null or p_namespace_id) then -- nothing to do 
			exit obj_inst_del;
		END IF;
		DELETE FROM obj_actual_definition where obj_metadata_id =(select obj_metadata_id from obj_metadat where obj_name =  p_obj_name ); 
	END IF;
END$$;
