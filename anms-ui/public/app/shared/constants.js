/*
 * Copyright (c) 2023 The Johns Hopkins University Applied Physics
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
import jQuery from 'jquery';

const Constants = Object.assign({}, window.Constants);
const anms_env_config = Object.assign({}, window.anms_env_config);

console.log("Constants:", Constants);
console.log("anms_env_config:", anms_env_config);

// Bootstrap Finished, Remove Init
jQuery('#vue-init').remove();
jQuery('#env-config').remove();

window.Constants = undefined;
window.anms_env_config = undefined;

const uiversion = anms_env_config.VUE_APP_UI_VERSION;
// const status_refresh_rate = anms_env_config.VUE_APP_STATUS_REFRESH_RATE; //ms -the rate of updating services' status
const status_refresh_rate = 60000; //ms -the rate of updating services' status

console.log(status_refresh_rate)
const service_info = anms_env_config.SERVICE_INFO;

export default Constants;
export {uiversion, 
    status_refresh_rate, 
    service_info
};
