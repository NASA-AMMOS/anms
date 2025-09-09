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
  let logger = require('../shared/logger');
  let request = require('request');
  const url = require('url');
  const utils = require('../shared/utils');

  const permissions = require('../core/permissions');

  const config = require('../shared/config');
  const utilities = require('./utilities');

  const requestTimeOut = 3000; //milliseconds
  const axios = require('axios');
  const FormData = require('form-data');
  const ACCEPTED_ADM_TYPE = 'application/octet-stream';

  exports.getAll = async function (req, res, next) {
    try {
      const usersReqHeader = utils.createAuthenticationHeader(req);
      return new Promise(function (resolve, reject) {
        let requestUrl = utils.generateAnmsCoreUrl(["adms"]);
        logger.info("Sending get all adm request to: ", requestUrl);
        request({
          method: 'Get',
          url: requestUrl,
          headers: usersReqHeader,
          json: true,
          timeout: requestTimeOut
        }, function (error, response, body) {
          logger.info("Receive response")
          logger.debug(JSON.stringify(response));
          if (error) {
            reject(error);
          } else if (response.statusCode >= 400) {
            let boomObj = utilities.errorCodeLookup(response.statusCode);
            next(boomObj);
          } else {
            resolve(body);
          }
        });
      }).then(function(admObj) {
        logger.info("Resolving response")
        logger.info(admObj)
          return res.status(200).json(admObj);
      }).catch(function(error) {
        logger.error("Request error: ", error);
        return next(Boom.internal(error.message));
      });
    } catch (error) {
      logger.error("Function error: ",error.message);
      return next(Boom.badGateway(error.message, error));
    }
  };
  exports.getOne = async function (req, res, next) {
    try {
      const adm_enm = req.params.adm_enum;
      const adm_namespace = req.params.namespace;

      const url = utils.generateAnmsCoreUrl(["adms", adm_enm, adm_namespace]);

      const json = await axios.get(url);
      if (json === null) {
        return res.status(404);
      }
      return res.status(200).json(json.data);
    } catch (err) {
      return next(Boom.badGateway('Error talking to CORE', err));
    }
  };

  exports.upload = async function (req, res, next) {
      const usersReqHeader = utils.createAuthenticationHeader(req);
      const file = req.file;
      console.info(file.mimetype)
      if (!_.isNull(file) && file.mimetype != ACCEPTED_ADM_TYPE) {
        return res.status(415).json({"message": `Not support this ${file.mimetype}`});
      }
      let requestUrl = utils.generateAnmsCoreUrl(["adms"]);
      console.info("Upload requestUrl: ", requestUrl);
     
      const formData = new FormData();
      //Reference: https://maximorlov.com/send-a-file-with-axios-in-nodejs/

      //Here we have file data is a buffer or stream,
      //Therefore, we need to add filename at the end
      //Normal formData append function only takes into 2 arguments
      formData.append('file', file.buffer, file.originalname);
      const headers = {
          ...usersReqHeader,
          'Content-Type': 'multipart/form-data'
      };
      const response = await axios.post(requestUrl,
        formData,
          {
              headers
          }
      ).catch(function (error) {
        console.error("Upload file error: ", error.response.statusText)
        return error.response
      });
      if (_.isNil(response) || _.isNil(response.data) || _.isNil(response.data.message)) {
        response.status = 500;
        console.error(response);
        response.data = {"message": "Internal Server Error"};
      }
      return res.status(response.status).json(response.data);
  };

})();
