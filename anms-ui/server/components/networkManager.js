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

  const Boom = require('@hapi/boom');
  const logger = require('../shared/logger');
  const axios = require('axios');

  // Base URL for amp-manager REST API
  // Environment variables from docker-compose: ION_MGR_HOST=amp-manager, ION_MGR_PORT=8089
  const nmBaseUrl = 'http://' + (process.env.ION_MGR_HOST || 'localhost') + ':' + (process.env.ION_MGR_PORT || '8089');

  /**
   * Get amp-manager version info
   */
  exports.getVersion = async function (req, res, next) {
    try {
      const url = nmBaseUrl + '/nm/api/version';
      const version = await axios.get(url);
      return res.status(200).json(version.data);
    } catch (err) {
      logger.error('nm getVersion failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  /**
   * Register a new agent
   */
  exports.nm_register_agent = async function (req, res, next) {
    try {
      const agentId = req.body;
      const url = nmBaseUrl + '/nm/api/agents';
      const response = await axios.post(url, agentId);
      return res.status(201).json(response.data);
    } catch (err) {
      logger.error('nm_register_agent failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  /**
   * Send hex command to agent by IDX
   */
  exports.nm_put_hex_idx = async function (req, res, next) {
    try {
      const agentId = req.params.idx;
      const hex = req.body;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent IDX'));
      }
      const url = nmBaseUrl + '/nm/api/agents/idx/' + agentId + '/hex';
      const response = await axios.put(url, hex);
      return res.status(200).json(response.data);
    } catch (err) {
      logger.error('nm_put_hex_idx failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  /**
   * Send hex command to agent by EID
   */
  exports.nm_put_hex_eid = async function (req, res, next) {
    try {
      const agentId = req.params.eid;
      const hex = req.body;
      if (!_.isString(agentId)) {
        return next(Boom.badData('Invalid Agent EID'));
      }
      const url = nmBaseUrl + '/nm/api/agents/eid/' + agentId + '/hex';
      const response = await axios.put(url, hex);
      return res.status(200).json(response.data);
    } catch (err) {
      logger.error('nm_put_hex_eid failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  /**
   * Clear reports for an agent
   */
  exports.nm_clear_reports = async function (req, res, next) {
    try {
      const agentId = req.params.addr;
      const url = nmBaseUrl + '/nm/api/agents/eid/' + agentId + '/clear_reports';
      const response = await axios.put(url);
      return res.status(200).json(response.data);
    } catch (err) {
      logger.error('nm_clear_reports failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  /**
   * Clear tables for an agent
   */
  exports.nm_clear_tables = async function (req, res, next) {
    try {
      const agentId = req.params.addr;
      const url = nmBaseUrl + '/nm/api/agents/eid/' + agentId + '/clear_tables';
      const response = await axios.put(url);
      return res.status(200).json(response.data);
    } catch (err) {
      logger.error('nm_clear_tables failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  /**
   * Get agent reports in hex format
   */
  exports.nm_get_reports_hex = async function (req, res, next) {
    try {
      const agentId = req.params.addr;
      const url = nmBaseUrl + '/nm/api/agents/eid/' + agentId + '/reports/hex';
      const response = await axios.get(url);
      return res.status(200).json(response.data);
    } catch (err) {
      logger.error('nm_get_reports_hex failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  /**
   * Get agent reports
   */
  exports.nm_get_reports = async function (req, res, next) {
    try {
      const agentId = req.params.addr;
      const url = nmBaseUrl + '/nm/api/agents/eid/' + agentId + '/reports';
      const response = await axios.get(url);
      return res.status(200).json(response.data);
    } catch (err) {
      logger.error('nm_get_reports failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  /**
   * Get agent reports in text format
   */
  exports.nm_get_reports_text = async function (req, res, next) {
    try {
      const agentId = req.params.addr;
      const url = nmBaseUrl + '/nm/api/agents/eid/' + agentId + '/reports/text';
      const response = await axios.get(url);
      return res.status(200).json(response.data);
    } catch (err) {
      logger.error('nm_get_reports_text failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  /**
   * Get agent reports in JSON format
   */
  exports.nm_get_reports_json = async function (req, res, next) {
    try {
      const agentId = req.params.addr;
      const url = nmBaseUrl + '/nm/api/agents/eid/' + agentId + '/reports/json';
      const response = await axios.get(url);
      return res.status(200).json(response.data);
    } catch (err) {
      logger.error('nm_get_reports_json failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  /**
   * Get agent reports in debug format
   */
  exports.nm_get_reports_debug = async function (req, res, next) {
    try {
      const agentId = req.params.addr;
      const url = nmBaseUrl + '/nm/api/agents/eid/' + agentId + '/reports/debug';
      const response = await axios.get(url);
      return res.status(200).json(response.data);
    } catch (err) {
      logger.error('nm_get_reports_debug failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  /**
   * Get agent information
   */
  exports.nm_get_agents_info = async function (req, res, next) {
    try {
      const agentId = req.params.addr;
      const url = nmBaseUrl + '/nm/api/agents/eid/' + agentId;
      const response = await axios.get(url);
      return res.status(200).json(response.data);
    } catch (err) {
      logger.error('nm_get_agents_info failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };

  /**
   * Clear reports via PUT
   */
  exports.nm_put_clear_reports = async function (req, res, next) {
    try {
      const agentId = req.params.addr;
      const url = nmBaseUrl + '/nm/api/agents/eid/' + agentId + '/reports/clear';
      const response = await axios.put(url);
      return res.status(200).json(response.data);
    } catch (err) {
      logger.error('nm_put_clear_reports failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };


  /**
   * List all agents (GET /nm/agents)
   */
  exports.nm_get_agents = async function (req, res, next) {
    try {
      const url = nmBaseUrl + '/nm/api/agents';
      const response = await axios.get(url);
      return res.status(200).json(response.data);
    } catch (err) {
      logger.error('nm_get_agents failed:', err.message);
      return next(Boom.badGateway('Error talking to NM', err));
    }
  };
})();
