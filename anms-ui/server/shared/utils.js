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

  const fs = require('fs');
  const url = require('url');
  const glob = require('glob');
  const path = require('path');
  const crypto = require('crypto');

  const _ = require('lodash');
  const async = require('async');
  const Promise = require('bluebird');

  const config = require('../shared/config');

  module.exports = {
    genClientIp: genClientIp,
    isNumberLike: isNumberLike,
    jsonTryParse: jsonTryParse,
    pseudoRandomHexBytes: pseudoRandomHexBytes,
    parseGlobConfigs: parseGlobConfigs,
    snakeCaseObject: snakeCaseObject,
    camelCaseObject: camelCaseObject,
    generateAnmsCoreUrl: generateAnmsCoreUrl,
    createAuthenticationHeader: createAuthenticationHeader
  };

  function genClientIp(req) {
    let result = '127.0.0.1';
    if (!_.isUndefined(req.ip)) {
      result = req.ip || result;
    } else if (!_.isUndefined(req.ips)) {
      result = req.ips[0] || result; // grab first one in case of many
    } else {
      result = req.header('X-Forwarded-For') ||
        req.connection.remoteAddress ||
        req.socket.remoteAddress ||
        req.connection.socket.remoteAddress || result;
    }
    return result;
  }

  function pseudoRandomHexBytes(bytesCount) {
    return new Promise(function (resolve, reject) {
      crypto.randomBytes(bytesCount, function (err, raw) {
        if (err) {
          return reject(err);
        } else {
          return resolve(raw.toString('hex'));
        }
      });
    });
  }

  function isNumberLike(n) {
    // https://github.com/lodash/lodash/issues/1148
    try {
      return !isNaN(parseFloat(n)) && isFinite(n);
    } catch (e) {
      return false;
    }
  }

  function jsonTryParse(potentialJson) {
    try {
      return JSON.parse(potentialJson);
    } catch (ex) {
      return {};
    }
  }

  function parseGlobConfigs(pathGlob) {
    var parsedConfigs = {};
    return new Promise(function (resolve, reject) {
      glob(pathGlob, {}, function (er, files) {
        if (er) {
          return reject(er);
        }
        async.each(files, function (filePath, eachCb) {
          fs.readFile(filePath, 'utf8', function (err, data) {
            if (err) {
              return eachCb(err);
            }
            try {
              Object.assign(parsedConfigs, JSON.parse(data));
              eachCb();
            } catch (e) {
              return eachCb(e);
            }
          });
        }, function (err) {
          if (err) {
            return reject(err);
          }
          resolve(parsedConfigs);
        });
      });
    });
  }

  function generateAnmsCoreUrl(pathParts, params) {
    let coreUrlObject = _.cloneDeepWith(config.core.uri);
    let path = _.join(pathParts, '/');
    _.set(coreUrlObject, 'pathname', path);
    if(!_.isUndefined(params)){
      _.set(coreUrlObject, 'query', params);
    }
    return url.format(coreUrlObject);
  }

  function createAuthenticationHeader(req) {
    return {
      'Authorization': req.headers.authorization,
      'accept': 'application/json'
    };
  }

  function camelCaseObject(object) {
    return _.reduce(object, function(result, value, key){
      _.set(result, _.camelCase(key), value);
      return result;
    }, {});
  }

  function snakeCaseObject(object) {
    return _.reduce(object, function(result, value, key){
      _.set(result, _.snakeCase(key), value);
      return result;
    }, {});
  }


})();

