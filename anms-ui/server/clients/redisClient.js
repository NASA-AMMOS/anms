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

  const redis = require('redis');
  const BPromise = require('bluebird');

  const logger = require('../shared/logger');
  const config = require('../shared/config');

  module.exports = {
    client: client() // Singleton Client on first Call
  };

  function client() {

    if (!config.redis.enabled) {
      return BPromise.reject(new Error('Redis not Enabled'));
    }

    BPromise.promisifyAll(redis);

    return new BPromise(function (resolve, reject) {

      const redisClient = redis.createClient(config.redis.parsedUri, config.redis.opts);

      redisClient.on('ready', onReady);
      redisClient.on('connect', onConnect);
      redisClient.on('reconnecting', onReconnecting);
      redisClient.on('warning', onWarning);
      redisClient.on('error', onError);
      redisClient.on('end', onEnd);

      function onReady() {
        logger.info('Redis Ready');
        return resolve(redisClient);
      }

      function onConnect() {
        logger.info('Redis Connected at', config.redis.uri);
      }

      function onReconnecting(rObj) {
        logger.warn('Redis Reconnecting', rObj);
        return reject('Redis Reconnecting');
      }

      function onWarning(warnObj) {
        logger.warn('Redis Warning', warnObj);
      }

      function onError(err) {
        logger.err('Redis Error', err);
        return reject(err);
      }

      function onEnd() {
        logger.info('Redis Connection Ended');
        return reject('Redis Connection Ended');
      }

    });

  }

})();

