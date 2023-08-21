##
## Copyright (c) 2023 The Johns Hopkins University Applied Physics
## Laboratory LLC.
##
## This file is part of the Asynchronous Network Managment System (ANMS).
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##     http://www.apache.org/licenses/LICENSE-2.0
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## This work was performed for the Jet Propulsion Laboratory, California
## Institute of Technology, sponsored by the United States Government under
## the prime contract 80NM0018D0004 between the Caltech and NASA under
## subcontract 1658085.
##

# This is a postgres stateful database with data definition startup SQL scripts

FROM postgres:14

COPY postgres/Database_Scripts/Tables/amp_core_create_database.sql /docker-entrypoint-initdb.d/00-amp_core_create_database.sql
COPY postgres/Database_Scripts/Tables/transcoder.sql /docker-entrypoint-initdb.d/00-transcoder.sql
COPY postgres/Database_Scripts/Tables/adm_data.sql /docker-entrypoint-initdb.d/01-adm_data.sql

COPY postgres/Database_Scripts/Views/obj_view.sql /docker-entrypoint-initdb.d/01-obj_view.sql
COPY postgres/Database_Scripts/Views/ari_view.sql /docker-entrypoint-initdb.d/14-ari_view.sql
COPY postgres/Database_Scripts/Views/ctrl_view.sql /docker-entrypoint-initdb.d/04-ctrl_view.sql
COPY postgres/Database_Scripts/Views/edd_view.sql /docker-entrypoint-initdb.d/05-edd_view.sql
COPY postgres/Database_Scripts/Views/mac_view.sql /docker-entrypoint-initdb.d/06-mac_view.sql
COPY postgres/Database_Scripts/Views/oper_view.sql /docker-entrypoint-initdb.d/07-oper_view.sql
COPY postgres/Database_Scripts/Views/message_view.sql /docker-entrypoint-initdb.d/08-message_view.sql
COPY postgres/Database_Scripts/Views/rpt_view.sql /docker-entrypoint-initdb.d/13-rpt_view.sql
COPY postgres/Database_Scripts/Views/sbr_view.sql /docker-entrypoint-initdb.d/09-sbr_view.sql
COPY postgres/Database_Scripts/Views/tbr_view.sql /docker-entrypoint-initdb.d/10-tbr_view.sql
COPY postgres/Database_Scripts/Views/tblt_view.sql /docker-entrypoint-initdb.d/11-tblt_view.sql
COPY postgres/Database_Scripts/Views/tnvc_view.sql /docker-entrypoint-initdb.d/12-tnvc_view.sql
COPY postgres/Database_Scripts/Views/parm_view.sql /docker-entrypoint-initdb.d/13-parm_view.sql
COPY postgres/Database_Scripts/Views/var_view.sql /docker-entrypoint-initdb.d/13-var_view.sql
COPY postgres/Database_Scripts/Views/namespace_view.sql /docker-entrypoint-initdb.d/13-namespace_view.sql

COPY postgres/Database_Scripts/Routines/all_routines.sql /docker-entrypoint-initdb.d/16-all_routines.sql
COPY postgres/Database_Scripts/Tables/healthcheck_roles.sql /docker-entrypoint-initdb.d/17-healthcheck_roles.sql
COPY postgres/Database_Scripts/amp_core_functions.sql /docker-entrypoint-initdb.d/17-amp_core_functions.sql
# This is used for testing, it is easier to delete the amp_agent after inserting it using adm_amp_agent.sql instead of removing the script since other scripts are also relying on amp_agent
# COPY postgres/Database_Scripts/Routines/amp_agent_delete.sql /docker-entrypoint-initdb.d/31-amp_agent_delete.sql

HEALTHCHECK --start-period=10s --interval=10s --timeout=5s --retries=5 \
    CMD pg_isready -U healthcheck
