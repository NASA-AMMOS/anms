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

  const _ = require('lodash');
  const path = require('path');
  const redis = require('redis');
  const rateLimit = require('express-rate-limit');
  const RedisLimiterStore = require('rate-limit-redis');

  const config = require('../shared/config');
  const logger = require('../shared/logger');


  // Configure Rate Limiter
  const enableRateLimiter = config.auth.rateLimiter === true && config.redis.enabled === true;
  const rateLimiterOptions = {
    windowMs: config.auth.requestLimitWindow, // request window,
    max: config.auth.requestLimit, // # max requests per time-window
    skip: enableRateLimiter ? _.constant(false) : _.constant(true)
  };
  if (enableRateLimiter) {
    rateLimiterOptions.store = new RedisLimiterStore({
      expiry: (config.auth.requestLimitWindow / 1000),
      resetExpiryOnChange: false,
      prefix: config.redis.limiterPrefix,
      client: (() => {
        if (!config.redis.enabled) {
          return {};
        }
        let rClient = redis.createClient(config.redis.parsedUri, config.redis.opts);
        rClient.unref(); // allows the program to exit once no more commands are pending...
        rClient.on('error', logger.error);
        return rClient;
      })()
    });
  }
  const userLimiter = rateLimit(rateLimiterOptions);

  module.exports = {

    api: (function () {
      const express = require('express');
      const multer = require('multer');
      const upload = multer();
      const router = express.Router();
      router.use(express.json());
      router.use(express.urlencoded({extended: true}));
      // route middleware that will happen on every request
      router.use(function (req, res, next) {
        // Do something here in the future? Maybe...
        next(); // continue doing what we were doing and go to the route
      });

      // Better Message
      router.all('/', function (req, res) {
        res.status(200).json('Welcome to the AMMOS ANMS API!');
      });

      //------------- JSON Routes -------------//

      const hello = require('../components/hello');

      // ---- Example Routes --- //
      router.get('/hello', userLimiter, hello.getHello);

       // ---- Core Routes ---- //
      const core = require('../components/core');
      router.get('/core/service_status', userLimiter, core.getServiceStatus);

      // ---- User Routes ---- //
      const users = require('../components/users');

      router.get('/users/:userName', userLimiter, users.getUserByUsernameWebSafe);
      router.post('/users', users.createUserProfile);
      router.put('/users/:userName', users.updateUserProfile);

       // ---- Adm Routes ---- //
       const adms = require('../components/adms');

      router.get('/core/adms', userLimiter, adms.getAll);
      router.get('/core/adms/:adm_enum', userLimiter, adms.getOne);
      router.post('/core/adms', upload.single('adm'), adms.upload);
      


      // ---- Agents Routes ---- //
      const agents = require('../components/registeredAgents');
      router.get('/agents', userLimiter, agents.getAgentsPaged);
      router.get('/agents/id/:id', userLimiter, agents.getAgentById);
      router.get('/agents/search/:query', userLimiter, agents.getAgentsPagedBySearch);
      router.get('/agents/parameter/name/:id', userLimiter, agents.getAgentsOperations);
      router.put('/agents/parameter/send/:id/:optId', agents.putAgentsOperations);

      // alerts
      const alerts = require('../components/alerts');
      router.put('/alerts/incoming', alerts.putAlerts);
      router.get('/alerts/incoming', userLimiter, alerts.getAlerts);
      router.put('/alerts/acknowledge/:index', alerts.acknowledgeAlert);

      // --- Builder Routes --- //
      const builder = require('../components/ariBuilder');
      router.get('/build/ari/all', userLimiter, builder.getARIs);
      router.get('/build/ari/id/:meta_id/:obj_id', userLimiter, builder.getARIParmInfo);

      // --Transcoder routes -- //
      const transcoder = require('../components/transcoder')
      router.put('/transcoder/ui/incoming/:cbor/hex', transcoder.putTranscodedHex)
      router.put('/transcoder/ui/incoming/str', transcoder.putTranscodedString)
      router.get('/transcoder/ui/loguserLimiter, ', transcoder.getTranscoderPaged)
      router.get('/transcoder/ui/log/search/:queryuserLimiter, ', transcoder.getTranscoderPagedBySearch)

      // ---NM Routes ---///
      const networkManager = require('../components/networkManager')
      router.get('/nm/versionuserLimiter, ', networkManager.getVersion)
      router.post('/nm/agents', networkManager.nm_register_agent);
      router.put('/nm/agents/idx/:idx/hex', networkManager.nm_put_hex_idx);
      router.put('/nm/agents/eid/:eid/hex', networkManager.nm_put_hex_eid);
      router.put('/nm/agents/eid/:addr/clear_reports', networkManager.nm_clear_reports);
      router.put('/nm/agents/eid/:addr/clear_tables ', networkManager.nm_clear_tables);
      router.get('/nm/agents/eid/:addr/reports/hex', userLimiter, networkManager.nm_get_reports_hex);
      router.get('/nm/agents/eid/:addr/reports', userLimiter, networkManager.nm_get_reports);
      router.get('/nm/agents/eid/:addr/reports/text', userLimiter, networkManager.nm_get_reports_text);
      router.get('/nm/agents/eid/:addr/reports/json', userLimiter, networkManager.nm_get_reports_json);
      router.get('/nm/agents/eid/:addr/reports/debug', userLimiter, networkManager.nm_get_reports_debug);
      router.get('/nm/agents/eid/:addr', userLimiter, networkManager.nm_get_agents_info);
      router.put('/nm/agents/eid/:addr/reports/clear', networkManager.nm_put_clear_reports);

      // --Reports Routes -- //
      const reports = require('../components/reports')
      router.get('/report/entry/name/:obj_agent_id', userLimiter, reports.getReportNameByAgent);
      router.get('/report/entries/table/:obj_agent_id/:adm/:report_name', userLimiter, reports.getReportEntriesByAgent);

      //------------- Unknown API Routes -------------//
      router.all('/*', function (req, res, next) {
        next({code: 404, message: 'Resource not found.'});
      });

      return router;

    })(),

    web: (function () {

      const router = require('express').Router();
      const indexPageMatches = ['/index.html', '/index', '/'];

      // route middleware that will happen on every request
      router.use(function (req, res, next) {
        next(); // continue doing what we were doing and go to the route
      });

      const pageHandlers = require('../components/main');

      //------------- Main Page -------------//
      router.get(indexPageMatches, pageHandlers.preMainPageHandler, userLimiter, pageHandlers.mainPageHandler);

      //------------- HTML5 Matcher -------------//
      router.get('/*', pageHandlers.preMainPageHandler, userLimiter, pageHandlers.mainPageHandler);

      //------------- Routes -------------//

      router.all('/*', function (req, res) {
        res.status(404);
        res.type('html').sendFile(config.client.error);
      });

      return router;

    })()

  };

})();

