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
(function () {
  'use strict';

  var fs = require('fs');
  var _ = require('lodash');
  var util = require('util');
  var path = require('path');
  var config = require('./config');
  var logPath = _.isString(config.logPath) && fs.existsSync(config.logPath) ? config.logPath : path.join(config.root, 'logs');
  var loggerInstance = require('./loggerInstance').initProvider(logPath);


  // See: https://github.com/nodejs/node/blob/master/lib/console.js

  module.exports.log = function () {
    if (config.logger === true) {
      loggerInstance.info(util.format.apply(this, arguments));
    }
  };

  module.exports.info = function () {
    if (config.logger === true) {
      loggerInstance.info(util.format.apply(this, arguments));
    }
  };

  module.exports.debug = function () {
    if (config.logger === true) {
      loggerInstance.debug(util.format.apply(this, arguments));
    }
  };

  module.exports.warning = module.exports.warn = function () {
    if (config.logger === true) {
      loggerInstance.warn(util.format.apply(this, arguments));
    }
  };

  module.exports.error = module.exports.err = function () {
    if (config.logger === true) {
      loggerInstance.error(util.format.apply(this, arguments));
    }
  };

})();
