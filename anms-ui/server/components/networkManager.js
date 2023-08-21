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


  exports.getVersion = async function (req, res, next) {
    try {
      const url = utils.generateAnmsCoreUrl(['nm', 'version']);
      const version = await axios.get(url);
      if (version === null) {
        return res.status(404);
      }
      return res.status(200).json(version.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  exports.nm_register_agent = async function (req, res, next) {
    try {
      const agentId = req.body
      const url = utils.generateAnmsCoreUrl(['nm', 'agents']);
      const manResponse = await axios.post(url, agentId);
      if (manResponse === null) {
        return res.status(404);
      }
      return res.status(200).json(manResponse.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  exports.nm_put_hex_idx = async function (req, res, next) {
    try {
      const agentId = req.params.idx;
      const hex = req.body;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent IDX'));
      }
      const url = utils.generateAnmsCoreUrl(['nm', 'agents', 'idx', agentId, 'hex']);
      const manResponse = await axios.put(url, hex);
      if (manResponse === null) {
        return res.status(404);
      }
      return res.status(200).json(manResponse.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  exports.nm_put_hex_eid = async function (req, res, next) {
    try {
      const agentId = req.params.eid;
      const hex = req.body;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent EID'));
      }
      const url = utils.generateAnmsCoreUrl(['nm', 'agents', 'eid', agentId, 'hex']);
      const manResponse = await axios.put(url, hex);
      if (manResponse === null) {
        return res.status(404);
      }
      return res.status(200).json(manResponse.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  exports.nm_clear_reports = async function (req, res, next) {
    try {
      const agentId = "eid/" + req.params.addr;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent ID'));
      }
      const url = utils.generateAnmsCoreUrl(['nm', 'agents', agentId, 'clear_reports']);
      const manResponse = await axios.put(url);
      if (manResponse === null) {
        return res.status(404);
      }
      return res.status(200).json(manResponse.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  exports.nm_clear_tables = async function (req, res, next) {
    try {
      const agentId = "eid/" + req.params.addr;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent ID'));
      }
      const url = utils.generateAnmsCoreUrl(['nm', 'agents', agentId, 'clear_tables']);
      const manResponse = await axios.put(url);
      if (manResponse === null) {
        return res.status(404);
      }
      return res.status(200).json(manResponse.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  exports.nm_get_reports_hex = async function (req, res, next) {
    try {
      const agentId = "eid/" + req.params.addr;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent ID'));
      }
      const url = utils.generateAnmsCoreUrl(['nm', 'agents', agentId, 'reports', 'hex']);
      const manResponse = await axios.get(url);
      if (manResponse === null) {
        return res.status(404);
      }
      return res.status(200).json(manResponse.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  exports.nm_get_reports = async function (req, res, next) {
    try {
      const agentId = "eid/" + req.params.addr;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent ID'));
      }
      const url = utils.generateAnmsCoreUrl(['nm', 'agents', agentId, 'reports']);
      const manResponse = await axios.get(url);
      if (manResponse === null) {
        return res.status(404);
      }
      return res.status(200).json(manResponse.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };


  exports.nm_get_reports_text = async function (req, res, next) {
    try {
      const agentId = "eid/" + req.params.addr;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent ID'));
      }
      const url = utils.generateAnmsCoreUrl(['nm', 'agents', agentId, 'reports', 'text']);
      const manResponse = await axios.get(url);
      if (manResponse === null) {
        return res.status(404);
      }
      return res.status(200).json(manResponse.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  exports.nm_get_reports_json = async function (req, res, next) {
    try {
      const agentId = "eid/" + req.params.addr;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent ID'));
      }
      const url = utils.generateAnmsCoreUrl(['nm', 'agents', agentId, 'reports', 'json']);
      const manResponse = await axios.get(url);
      if (manResponse === null) {
        return res.status(404);
      }
      return res.status(200).json(manResponse.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  exports.nm_get_reports_debug = async function (req, res, next) {
    try {
      const agentId = "eid/" + req.params.addr;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent ID'));
      }
      const url = utils.generateAnmsCoreUrl(['nm', 'agents', agentId, 'reports', 'debug']);
      const manResponse = await axios.get(url);
      if (manResponse === null) {
        return res.status(404);
      }
      return res.status(200).json(manResponse.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  exports.nm_get_agents_info = async function (req, res, next) {
    try {
      const agentId = "eid/" + req.params.addr;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent ID'));
      }
      const url = utils.generateAnmsCoreUrl(['nm', 'agents', agentId]);
      const manResponse = await axios.get(url);
      if (manResponse === null) {
        return res.status(404);
      }
      return res.status(200).json(manResponse.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  exports.nm_put_clear_reports = async function (req, res, next) {
    try {
      const agentId = "eid/" + req.params.addr;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent ID'));
      }
      const url = utils.generateAnmsCoreUrl(['nm', 'agents', agentId, 'reports', 'clear']);
      const manResponse = await axios.put(url);
      if (manResponse === null) {
        return res.status(404);
      }
      return res.status(200).json(manResponse.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };
})();
