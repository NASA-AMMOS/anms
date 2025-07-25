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
import 'core-js/stable';
import 'regenerator-runtime/runtime';
import 'intersection-observer';
import Vue from 'vue';
import moment from 'moment';
import * as d3 from 'd3';
import sanitizeHTML from 'sanitize-html';
import BootstrapVue from 'bootstrap-vue';
import App from '@app/core/App.vue';
import router from '@app/core/router';
import Constants from '@app/shared/constants';
import store from "@app/store";
import toastr from 'toastr';

/* import the fontawesome core */
import { library } from '@fortawesome/fontawesome-svg-core'

/* import font awesome icon component */
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

/* import specific icons */
import { faUserSecret, faUser, faArrowRightFromBracket } from '@fortawesome/free-solid-svg-icons'

/* add icons to the library */
library.add(faUserSecret)
library.add(faUser);
library.add(faArrowRightFromBracket);
// Register Plugins
Vue.use(BootstrapVue);

// Vue Settings
Vue.config.devtools = !Constants.BASE_RELEASE; // enable allowing use the vue-devtools plugin in the browser
Vue.config.performance = !Constants.BASE_RELEASE; // enable performance tracing
Vue.config.productionTip = false; // disable annoying console message

// Vue Constants
Vue.prototype.$sanitize = sanitizeHTML;
Vue.prototype.$moment = moment;
Vue.prototype.$d3 = d3;
Vue.prototype.$log = (() => {
  const levels = ['log', 'info', 'warn', 'error', 'debug', 'trace']; // https://console.spec.whatwg.org/
  let logFuncs = {};
  levels.forEach((level) => {
    logFuncs[level] = console[level].bind(console);
  });
  return logFuncs;
})();

Vue.component('font-awesome-icon', FontAwesomeIcon);

toastr.options.preventDuplicates = true;
toastr.options.timeOut = 5000;
toastr.options.closeButton = true;

// eslint-disable-next-line no-new
new Vue({
  el: '#vue-app',
  router,
  store,
  render: function (h) {
    return h(App);
  }
});
