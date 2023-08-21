/*
 * Copyright (c) 2023 The Johns Hopkins University Applied Physics
 * Laboratory LLC.
 *
 * This file is part of the Asynchronous Network Managment System (ANMS).
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

  var _ = require('lodash');
  var path = require('path');
  var winston = require('winston');
  var WinstonDailyRotate = require('winston-daily-rotate-file');

  module.exports.provider = null;
  module.exports.initProvider = function (logPath) {
    if (!_.isNull(module.exports.provider)) {
      return module.exports.provider;
    }
    module.exports.provider = new (winston.Logger)({ // winston.createLogger({ <-- winston@3
      transports: [
        new (WinstonDailyRotate)({
          name: 'Debug.log',
          maxFiles: 30,
          // maxSize: '500m',
          auditFile: null,
          zippedArchive: false,
          datePattern: 'YYYY-MM-DD',
          dirname: logPath,
          filename: 'debug.%DATE%.log',
          json: true // remove on winston@3
        }),
        new (WinstonDailyRotate)({
          name: 'PrettyDebug.log',
          maxFiles: 30,
          // maxSize: '500m',
          auditFile: null,
          zippedArchive: false,
          datePattern: 'YYYY-MM-DD',
          dirname: logPath,
          filename: 'debug.pretty.%DATE%.log',
          json: false // remove on winston@3
        }),
        new (winston.transports.Console)({
          name: 'Console.log',
          handleExceptions: true,
          handleRejections: true,
          humanReadableUnhandledException: true, // remove on winston@3
          json: false, // remove on winston@3
          colorize: true, // remove on winston@3
          timestamp: true // remove on winston@3
        })
      ],
      exceptionHandlers: [
        // https://github.com/winstonjs/winston/issues/1479
        // Reason we haven't migrated to winston@3 yet...
        new (WinstonDailyRotate)({
          name: 'Crash.log',
          maxFiles: 30,
          // maxSize: '500m',
          auditFile: null,
          zippedArchive: false,
          datePattern: 'YYYY-MM-DD',
          dirname: logPath,
          filename: 'crash.%DATE%.log',
          handleExceptions: true,
          handleRejections: true,
          humanReadableUnhandledException: true, // remove on winston@3
          json: true // remove on winston@3
        }),
        new (WinstonDailyRotate)({
          name: 'PrettyCrash.log',
          maxFiles: 30,
          // maxSize: '500m',
          auditFile: null,
          zippedArchive: false,
          datePattern: 'YYYY-MM-DD',
          dirname: logPath,
          filename: 'crash.pretty.%DATE%.log',
          handleExceptions: true,
          handleRejections: true,
          humanReadableUnhandledException: true, // remove on winston@3
          json: false // remove on winston@3
        })
      ],
      exitOnError: false
    });
    return module.exports.provider;
  };

  module.exports.bunyanProvider = function () {
    const logFuncs = {
      // config is the object passed to the client constructor.
      fatal: module.exports.provider.error,
      error: module.exports.provider.error,
      warning: module.exports.provider.warn,
      warn: module.exports.provider.warn,
      info: module.exports.provider.info,
      debug: module.exports.provider.debug,
      trace: module.exports.provider.verbose,
      close: _.noop,
      // recursive getter mimicking bunyan's child
      child: function () {
        return logFuncs;
      }
    };
    return logFuncs;
  };

})();
