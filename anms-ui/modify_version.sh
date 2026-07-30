#!/usr/bin/env bash
set -e
##
## Copyright (c) 2023 The Johns Hopkins University Applied Physics
## Laboratory LLC.
##
## This file is part of the Asynchronous Network Management System (ANMS).
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

# --------------------------------------------------------------------
# Determine the UI version.
#   - If BUILD_VERSION is defined in the environment, use it.
#   - Otherwise, fall back to the result of `git describe --tags`.
# --------------------------------------------------------------------
UI_VERSION="${BUILD_VERSION:-$(git describe --tags)}"

# Path to the file that contains the placeholder version.
TARGET_FILE="./src/environments/environment.ts"

# --------------------------------------------------------------------
# In‑place replacement:
#   The line in environment.ts looks like:
#       UI_VERSION: 'unknown', // NOTE: Auto‑updated at build‑time …
#   We replace whatever is between the single quotes with $UI_VERSION.
# --------------------------------------------------------------------
sed -i.bak -E "s/(UI_VERSION:[[:space:]]*')[^']*(')/\1${UI_VERSION}\2/" "$TARGET_FILE"

echo "UI_VERSION updated to '${UI_VERSION}' in ${TARGET_FILE}"
