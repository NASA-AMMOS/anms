--
-- Copyright (c) 2025 The Johns Hopkins University Applied Physics
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



-- tables used by the core for user management and for network status tracking


-- user for man user and accessing in the ui
-- create an admin and a normal user
-- can create super set of this for things not supported ect

CREATE SEQUENCE user_id_seq minvalue 0;
CREATE TABLE "user" (
                      id integer NOT NULL DEFAULT nextval('user_id_seq'),
                      username character varying(255) NOT NULL UNIQUE,
                      email character varying(255) UNIQUE,
                      first_name character varying(255),
                      last_name character varying(255),
                      password character varying(255),
                      is_enabled boolean DEFAULT true,
                      is_mfa_enabled boolean DEFAULT false,
                      is_ldap_user boolean DEFAULT false,
                      last_login_at timestamp with time zone,
                      last_login_ip character varying(255),
                      current_login_at timestamp with time zone,
                      current_login_ip character varying(255),
                      login_count integer DEFAULT 0,
                      token character varying(255) UNIQUE,
                      token_secret character varying(255),
                      otp_secret character varying(64),
                      otp_secret_registered boolean DEFAULT false,
                      otp_secret_forgot character varying(64),
                      password_token_reset character varying(255),
                      roles integer[],
                      permissions integer[],
                      details jsonb,
                      created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      PRIMARY KEY (id)
);
ALTER SEQUENCE user_id_seq OWNED BY "user".id;
ALTER SEQUENCE user_id_seq RESTART WITH 0;


-- whenyou send invites to user
-- admin send invites get token for setup time out
CREATE SEQUENCE invite_id_seq minvalue 0;
CREATE TABLE invite (
                        id integer NOT NULL DEFAULT nextval('invite_id_seq'),
                        email character varying(255) NOT NULL UNIQUE,
                        token character varying(255),
                        token_secret character varying(255),
                        token_expire timestamp with time zone,
                        is_enabled boolean DEFAULT true,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (id)
);
ALTER SEQUENCE invite_id_seq OWNED BY invite.id;
ALTER SEQUENCE invite_id_seq RESTART WITH 0;


--things wanted to see for agents
-- redundant from registered agent
-- CREATE SEQUENCE agent_id_seq minvalue 0;
-- CREATE TABLE agent (
--                        id integer NOT NULL DEFAULT nextval('agent_id_seq'),
--                        name character varying(255) NOT NULL UNIQUE,
--                        status integer,
--                        historical_data json[],
--                        received_reports json[],
--                        supported_a_d_ms character varying(255)[],
--                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
--                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--                        PRIMARY KEY (id)
-- );
-- ALTER SEQUENCE agent_id_seq OWNED BY agent.id;
-- ALTER SEQUENCE agent_id_seq RESTART WITH 0;

-- temp things that might be ready to be removed
CREATE SEQUENCE alert_id_seq minvalue 0;
CREATE TABLE alert (
                       id integer NOT NULL DEFAULT nextval('alert_id_seq'),
                       title text,
                       status integer NOT NULL,
                       message text,
                       created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       PRIMARY KEY (id)
);
ALTER SEQUENCE alert_id_seq OWNED BY alert.id;
ALTER SEQUENCE alert_id_seq RESTART WITH 0;

CREATE SEQUENCE network_status_id_seq minvalue 0;
CREATE TABLE networkStatus (
                               id integer NOT NULL DEFAULT nextval('network_status_id_seq'),
                               name text,
                               status integer DEFAULT 0,
                               historical_data json[],
                               received_reports json[],
                               supported_a_d_ms text[],
                               "to" integer,
                               "from" integer,
                               created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               PRIMARY KEY (id)
);
ALTER SEQUENCE network_status_id_seq OWNED BY networkStatus.id;
ALTER SEQUENCE network_status_id_seq RESTART WITH 0;