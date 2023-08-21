
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
  const Boom = require('@hapi/boom');
  const logger = require('../shared/logger');
  const axios = require('axios');
  const utils = require('../shared/utils');
  let request = require('request');
  
  const config = require('../shared/config');
  request = request.defaults({
    json: true,
    baseUrl: _.get(config,'core.parsedUri'),
    encoding: 'utf8',
    timeout: 60000 * 10 // 10 minutes
  });
exports.acknowledgeAlert = async function(req, res, next){
  try {
    const index = Number(req.params.index);
    const url = utils.generateAnmsCoreUrl(['alerts', 'acknowledge', index]);
    const ret = await axios.put(url);
    return res.status(200).json(ret.data);
  } catch (err) {
    return next(Boom.badGateway('Error sending parameter put', err));
  }
};
exports.getAlerts = async function(req, res, next){
  return new Promise(function (resolve, reject) {
    request.get({url: '/alerts/incoming'}, function (error, response, body) {
      logger.info(JSON.stringify(response));
      if (error) {
        logger.err("error sending request to core:", error);
        reject(error);
      } else if (response.statusCode >= 400 && response.statusCode < 500) {
        return next(Boom.badGateway('Error talking to core'));
      } else {
        resolve(body);
      }
    });
  }).then(function(statusObj) {
    return res.json(statusObj);
  }).catch(function(errObj) {
    return next(Boom.badGateway(errObj));
  });
} 
exports.putAlerts = async function (req, res, next) {
    try {
      const new_alerts = req.body.data
      console.log(new_alerts)
      // add to alert list
      new_alerts.forEach((alert) => {
        // agents.addAlert(alert);
        // request.put({url: '/app', data: alert});
      });

      return res.status(200).json();
    } catch (err) {
      return next(Boom.badGateway('Error sending parameter put', err));
    }
  };

  })();
