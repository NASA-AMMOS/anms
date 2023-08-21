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

  const _ = require('lodash');
  const path = require('path');
  const Boom = require('@hapi/boom');
  const crypto = require('crypto');
  const QRCode = require('qrcode');

  const logger = require('../shared/logger');
  const config = require('../shared/config');

  // we shouldn't have that many multiple pages to begin with, so this is ok...
  const indexHtmlPath = path.posix.join(config.uris.webBase, path.basename(config.client.index));
  const userOmits = ['password', 'tokenSecret', 'otpSecret', 'otpSecretForgot'];

  exports.preMainPageHandler = function (req, res, next) {
    return next();
  };

  exports.mainPageHandler = function (req, res, next) {
    const sanitizedUser = _.omit(req.user, userOmits);
    console.info("Mainpagehandler", req.body);
    res.status(200).type('html').render(config.client.index, {
      user: JSON.stringify(sanitizedUser),
      userNameRemote: req.headers["x-remote-user"],
      baseUrl: config.uris.webBasePath,
      apiUrl: config.uris.apiBasePath,
      clientAddress: req.ip,
      baseVersion: config.client.version,
      baseRelease: !(config.debug || config.tests)
    });
  };

})();
