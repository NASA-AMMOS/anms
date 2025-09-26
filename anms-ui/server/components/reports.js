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
  const axios = require('axios');
  const utils = require('../shared/utils');


  exports.getReportNameByAgent = async function(req,res,next){
    try {
      // /entry/name/{agent_id}
      let obj_agent_id = req.params.obj_agent_id
      
      const url = utils.generateAnmsCoreUrl(['report','entry','name', obj_agent_id]);
      const aris = await axios.get(url);
      return res.status(200).json(aris.data);
    } catch (err) {
      return next(Boom.badGateway('Error Getting Paged Agents', err));
    }
  };

  exports.getReportEntriesByAgent = async function(req,res,next){
    try {
      // /entry/values/{agent_id}/{ADM}/{report_name}
      let obj_agent_id = req.params.obj_agent_id
      let correlator_nonce = encodeURIComponent(req.params.correlator_nonce)
      
      const url = utils.generateAnmsCoreUrl(['report','entries','table', obj_agent_id, correlator_nonce]);
      const name_entries = await axios.get(url);
      return res.status(200).json(name_entries.data);
    } catch (err) {
      return next(Boom.badGateway('Error Getting reports', err));
    }
  };
})();


