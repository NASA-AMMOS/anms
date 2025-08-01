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
  const Boom = require('@hapi/boom');
  const axios = require('axios');
  const utils = require('../shared/utils');

  exports.putTranscodedHex = async function(req,res,next){
    try {
      // /transcoder/ui/incoming/{cbor}/hex
      const cbor = req.params.cbor
      const url = utils.generateAnmsCoreUrl(['transcoder','ui','incoming',cbor,'hex']);
      const uri = await axios.put(url);
      return res.status(200).json(uri.data);
    } catch (err) {
      return next(Boom.badGateway('Error sending msg for transcoder', err));
    }
  };

  exports.putTranscodedString = async function(req,res,next){
    try {
      // /transcoder/ui/incoming/str
      const reqBody = req.body;
      const params = {'input_ari': req.body.ari};
      const url = utils.generateAnmsCoreUrl(['transcoder','ui','incoming','str'],params);
      const uri = await axios.put(url);
      return res.status(200).json(uri.data);
    } catch (err) {
      return next(Boom.badGateway('Error sending msg for transcoder', err));
    }
  };

  exports.putTranscodeAndSendString = async function(req,res,next){
    try {
      // /transcoder/ui/incoming_send/str
      const reqBody = req.body;
      const params = {'ari': req.body.ari, 'eid': req.body.eid};
      const url = utils.generateAnmsCoreUrl(['transcoder','ui','incoming_send','str'],params);
      const uri = await axios.put(url);
      return res.status(200).json(uri.data);
    } catch (err) {
      return next(Boom.badGateway('Error sending msg for transcoder', err));
    }
  };
     
  exports.getTranscoderPaged = async function (req, res, next) {
    try {
      if (req.query.page === undefined) {
        return next(Boom.badData('Invalid page=' + req.query.page));
      }
      if (req.query.size === undefined) {
        return next(Boom.badData('Invalid size=' + req.query.size));
      }
      const params = {'page': req.query.page, 'size': req.query.size };
      const url = utils.generateAnmsCoreUrl(['transcoder','db','all'], params);

      const transcoderLog = await axios.get(url);
      return res.status(200).json(transcoderLog.data);
    } catch (err) {
      return next(Boom.badGateway('Error Getting Paged transcoderLog', err));
    }
  };

  exports.getTranscoderById = async function (req, res, next) {
    try {
      const id = req.params.id;
      const url = utils.generateAnmsCoreUrl(['transcoder', 'db', 'id', id]);
      const transcoderLog = await axios.get(url);
      return res.status(200).json(transcoderLog.data);
    } catch (err) {
      return next(Boom.badGateway("Error Getting Transcoder By Id", err));
    }
  }

  exports.getTranscoderPagedBySearch = async function (req, res, next) {
    try {
      const transcoderQuery = req.params.query;
      if (!_.isString(transcoderQuery)) {
        return next(Boom.badData('Invalid Agent Search'));
      }
      if (req.query.page === undefined) {
        return next(Boom.badData('Invalid page=' + req.query.page));
      }
      if (req.query.size === undefined) {
        return next(Boom.badData('Invalid size=' + req.query.size));
      }
      const params = {'page': req.query.page, 'size': req.query.size };
      const url = utils.generateAnmsCoreUrl(['transcoder', 'db', 'search', encodeURIComponent(transcoderQuery)], params);
      console.log("[getTranscoderPagedBySearch]: url");
      console.log(url);
      const transcoderLog = await axios.get(url);
      console.log("[getTranscoderPagedBySearch]: transcoderLog.data");
      console.log(transcoderLog.data);
      return res.status(200).json(transcoderLog.data);
    }
    catch (err) {
      return next(Boom.badGateway('Error Getting transcoderLog with search', err));
    }
  };

})();
