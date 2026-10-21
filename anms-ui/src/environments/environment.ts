/*
 * Copyright (c) 2026 The Johns Hopkins University Applied Physics
 * Laboratory LLC.
 *
 * This file is part of the Asynchronous Network Management System (ANMS).
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *     http://www.apache.org/licenses/LICENSE-2.0
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * This work was performed for the Jet Propulsion Laboratory, California
 * Institute of Technology, sponsored by the United States Government under
 * the prime contract 80NM0018D0004 between the Caltech and NASA under
 * subcontract 1658085.
 */
export const environment = {
  UI_VERSION: 'unknown', // NOTE: Auto-updated at build-time by modify_version.sh
  VUE_APP_STATUS_REFRESH_RATE: 60000, // milliseconds

  BASE_API_URL: 'http://anms-test:8080',

  SERVICE_INFO: {
    names: [
      "adminer","anms-core","authnz","amp-manager",
      "postgres","redis","grafana","grafana-image-renderer"
    ],
    normal_status: ["running","healthy"],
    error_status: ["not-running","unhealthy"]
  }
};
