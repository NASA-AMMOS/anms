# Copyright (c) 2025 The Johns Hopkins University Applied Physics
# Laboratory LLC.

# This file is part of the Delay-Tolerant Networking Management
# Architecture (DTNMA) Tools package.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# This is a postgres stateful database with data definition startup SQL scripts
FROM postgres:14


COPY anms_db_tables/*.sql /docker-entrypoint-initdb.d/
COPY dtnma-tools/refdb-sql/postgres/Database_Scripts/*/*.sql /docker-entrypoint-initdb.d/


# This is used for testing, it is easier to delete the amp_agent after inserting it using adm_amp_agent.sql instead of removing the script since other scripts are also relying on amp_agent
# COPY postgres/Database_Scripts/Routines/amp_agent_delete.sql /docker-entrypoint-initdb.d/31-amp_agent_delete.sql

HEALTHCHECK --start-period=10s --interval=10s --timeout=5s --retries=5 \
    CMD pg_isready -U healthcheck
