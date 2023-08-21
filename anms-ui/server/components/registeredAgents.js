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

  exports.getAgentById = async function (req, res, next) {
    try {
      const agentId = req.params.id;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent ID'));
      }
      const url = utils.generateAnmsCoreUrl(['agents', 'id', agentId]);
      const agentObj = await axios.get(url);
      if (agentObj === null) {
        return res.status(404);
      }
      return res.status(200).json(agentObj.data);
    } catch (err) {
      return next(Boom.badGateway('Error Getting Agent', err));
    }
  };

  exports.getAgentsPaged = async function (req, res, next) {
    try {
      if (req.query.page === undefined) {
        return next(Boom.badData('Invalid page=' + req.query.page));
      }
      if (req.query.size === undefined) {
        return next(Boom.badData('Invalid size=' + req.query.size));
      }
      const params = {'page': req.query.page, 'size': req.query.size };
      const url = utils.generateAnmsCoreUrl(['agents'], params);
      const agents = await axios.get(url);
      return res.status(200).json(agents.data);
    } catch (err) {
      return next(Boom.badGateway('Error Getting Paged Agents', err));
    }
  };

  exports.getAgentsPagedBySearch = async function (req, res, next) {
    try {
      const agentQuery = req.params.query;
      if (!_.isString(agentQuery)) {
        return next(Boom.badData('Invalid Agent Search'));
      }
      if (req.query.page === undefined) {
        return next(Boom.badData('Invalid page=' + req.query.page));
      }
      if (req.query.size === undefined) {
        return next(Boom.badData('Invalid size=' + req.query.size));
      }
      const params = {'page': req.query.page, 'size': req.query.size };
      const url = utils.generateAnmsCoreUrl(['agents', 'search', agentQuery], params);
      const agents = await axios.get(url);
      return res.status(200).json(agents.data);
    } catch (err) {
      return next(Boom.badGateway('Error Getting Agents with search', err));
    }
  };

  exports.getAgentsOperations = async function (req, res, next) {
    try {
      // TODO agentid dependent 
      const agentId = req.params.id;
    

      const url = utils.generateAnmsCoreUrl(['agents', 'parameter', 'definition', 'all']);
      const optObj = await axios.get(url);
      
      return res.status(200).json(optObj.data);
    } catch (err) {
      return next(Boom.badGateway('Error Getting Agents parameter', err));
    }
  };

  exports.putAgentsOperations = async function (req, res, next) {
    try {
      const agentId = Number(req.params.id);
      const optId = Number(req.params.optId);
      const params = req.body;
      const url = utils.generateAnmsCoreUrl(['agents', 'parameter', 'send', agentId, optId]);
      const ret = await axios.put(url, params);
      
      return res.status(200).json(ret.data);
    } catch (err) {
      return next(Boom.badGateway('Error sending parameter put', err));
    }
  };
})();
