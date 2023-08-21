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

-- STORED PROCEDURE(S)


-- ==
-- function for string processing used by other sp
-- help make inserting large sets of data more user friendly 
-- ==


CREATE OR REPLACE PROCEDURE SP__get_delimiter_position(IN p_str varchar, p_delimiter varchar, p_start_position integer, INOUT r_found_position integer)
LANGUAGE plpgsql
AS $$ 
DECLARE
length int;
position_index int;
iterator_index int;
char_value varchar;
delimiter_found BOOLEAN;
BEGIN
	IF (p_str IS NOT NULL) && (p_start_position IS NOT NULL)THEN 
		 BEGIN
			length := CHAR_LENGTH(p_str); 
			position_index := p_start_position; 
            iterator_index := p_start_position; 
            char_value := ''; 
            delimiter_found := FALSE; 
            r_found_position := NULL; 
			WHILE (position_index != length) && (delimiter_found != TRUE) loop 
				 
					char_value := SUBSTRING(p_str, iterator_index, 1);
                    IF char_value LIKE p_delimiter THEN 
						position_index := iterator_index;
                        r_found_position := position_index; 
                        delimiter_found := TRUE; 
                    END IF; 
                    iterator_index := iterator_index + 1; 
				
			END LOOP; 
		END; 
    ELSE 
		 BEGIN
			r_found_position := NULL; 
        END; 
    END IF; 
end$$;




CREATE OR REPLACE PROCEDURE SP__null_string_check(INOUT p_string varchar)
LANGUAGE plpgsql
AS $$ BEGIN
	IF (p_string LIKE 'null') || (p_string LIKE 'NULL') || (p_string LIKE 'Null') THEN BEGIN
			 p_string := NULL; 
        END; 
    END IF; 
end$$;