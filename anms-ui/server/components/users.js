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
  const url = require('url');
  const utils = require('../shared/utils');
  const axios = require('axios');

  const permissions = require('../core/permissions');

  const config = require('../shared/config');
  const utilities = require('./utilities');

  const usersWebSafeFields = ['id', 'username', 'firstName', 'lastName', 'email', 'details'];
  const usersProfileWebSafeFields = ['id', 'username', 'first_name', 'last_name', 'email', 'created_at'];
  const adminUsersWebSafeFields = ['id', 'username', 'firstName', 'lastName', 'email', 'isEnabled', 'isMfaEnabled', 'roles', 'permissions', 'details'];

  const addUserFields = new Set(['username', 'firstName', 'lastName', 'email', 'password', 'details','roles','permissions']); // fast lookups
  const addUserFieldsArr = Array.from(addUserFields); // some ops require array

  const addUserProfileFields = new Set(['username', 'first_name', 'last_name', 'email']);
  const addUserProfileFieldsArr = Array.from(addUserProfileFields); // some ops require array

  const editUserFields = new Set(['firstName', 'lastName', 'email']); // fast lookups
  const editUserFieldsArr = Array.from(editUserFields); // some ops require array

  const requestTimeOut = 3000; //milliseconds

  // This is not working with anms-core
  exports.createUserWithHashes = async function (req, res, next) {

  };

  exports.getUserWebFields = async function (req, res, next) {
    try {
      return res.status(200).json(addUserFieldsArr);
    } catch (error) {
      return next(Boom.badGateway('Error Getting User Web Fields', error));
    }
  };

  exports.getAllUsersWebSafe = async function (req, res, next) {
    try {
      const usersReqHeader = createAuthenticationHeader(req);
      const page = req.page ? req.page : 1;
      const size = req.size ? req.size : 50;
      const requestUrl = generateAnmsCoreUrl('', {page: page, size: size});
      const response = await restApi({method: 'get', url: requestUrl, headers: usersReqHeader, timeout: 6000});
      logger.debug(`Core users response status: ${response.status}`);
      if (response.status >= 400) {
        return next(Boom.badGateway('Error authenticating user'));
      }
      {
        const results = response.data;
        let users = results.items;
        const viewMorePermissions = [permissions.systemPermissionsInv[permissions.systemPermissions.PERMISSION_ALL],
                                     permissions.systemPermissionsInv[permissions.systemPermissions.PERMISSION_ADD_USER],
                                     permissions.systemPermissionsInv[permissions.systemPermissions.PERMISSION_EDIT_USER]];
        const canViewMore = _.some(viewMorePermissions, function (perm) {
          return _.includes(req.user.permissions, perm);
        });
        users = _.reduce(users, function(results, user){
          const newUser = utils.camelCaseObject(user);
          results.push(newUser);
          return results;
        }, []);
        let filter = usersWebSafeFields;
        if (canViewMore) {
          filter = adminUsersWebSafeFields;
        }
        const cleanedUsers = _.map(users, (user) => {
          return _.pick(user, filter);
        });
        return res.status(200).json(cleanedUsers);
      }
    } catch (error) {
      return next(Boom.badGateway('Error Getting Users', error));
    }
  };

  exports.getUserByUsernameWebSafe = async function (req, res, next) {
    try {
      const usersReqHeader = createAuthenticationHeader(req);
      const userName = req.params.userName;
      const requestUrl = generateAnmsCoreUrl(`/${userName}`);
      logger.info("Sending getUser request to: ", requestUrl);
      const response = await restApi({method: 'get', url: requestUrl, headers: usersReqHeader, timeout: requestTimeOut});
      logger.debug(`Core users response status: ${response.status}`);
      if (response.status >= 400) {
        return next(utilities.errorCodeLookup(response.status));
      }
      return res.status(200).json(response.data);
    } catch (error) {
      logger.error("Function error: ",error.message);
      return next(Boom.badGateway(error.message, error));
    }
  };

  exports.createUserProfile = async function (req, res, next) {
    try {
      const userObj = req.body.data;
      const hasAllFields = _.every(addUserProfileFieldsArr, (field) => {
        return _.has(userObj, field);
      });
      if (!hasAllFields) {
        return next(Boom.badData('Missing Fields'));
      }
      //Check for authorization
      const remoteUser = req.headers["x-remote-user"];
      if (_.isNil(remoteUser) || userObj.username != remoteUser) {
        logger.info(`${remoteUser} is unauthorized to create profile of ${userObj.username}`);
        return next(Boom.unauthorized('Cannot create profile of other user'));
      }

      const filteredUserProfile = _.pick(userObj, addUserProfileFieldsArr);
      const usersReqHeader = createAuthenticationHeader(req);
      const profileInfo =  utils.snakeCaseObject(filteredUserProfile);
      
      const response = await restApi({method: 'post', url: generateAnmsCoreUrl(''), headers: usersReqHeader, data: profileInfo});
      logger.debug(`Core users response status: ${response.status}`);
      if (response.status >= 400 && response.status < 500) {
        const boomObj = Boom.boomify(new Error(), {statusCode: response.status, details: response.data});
        logger.info(boomObj);
        return response.status === 409 ? res.status(409).json(response.data.field) : next(boomObj);
      }
      if (response.status >= 500) {
        return next(Boom.internal('Internal server error'));
      }
      logger.info(response.data);
      return res.status(201).json(_.pick(response.data, usersProfileWebSafeFields));
    } catch (error) {
      logger.error("Function error: ",error.message);
      return next(Boom.badGateway(error.message, error));
    }
  };

  exports.addUser = async function (req, res, next) {
    try {
      const userObj = req.body;
      const hasAllFields = _.every(addUserFieldsArr, (field) => {
        return _.has(userObj, field);
      });
      if (!hasAllFields) {
        return next(Boom.badData('Missing Fields'));
      }
      
      // extract details
      const hasUserOrg = _.has(userObj, 'organization');
      const filteredUser = _.pick(userObj, addUserFieldsArr);
      // add details
      const detailsObj = {};
      if (hasUserOrg) {
        detailsObj.organization = userObj.organization;
        delete filteredUser.organization;
      }
      filteredUser.details = detailsObj;
      // assign roles (for now)
      // TODO: pass proper permissions and roles on user create form
      filteredUser.roles = _.isEmpty(filteredUser.roles) ? [permissions.systemRoles.ROLE_USER] : filteredUser.roles;
      filteredUser.permissions = _.isEmpty(filteredUser.permissions) ?
        permissions.systemMappings[permissions.systemRoles.ROLE_USER] : filteredUser.permissions;
      // check password
      // TODO: do complexity verifications...
      if (_.size(filteredUser.password) < config.auth.passwordComplexity.minsize) {
        return next(Boom.badData('Invalid Password Length'));
      }
      const usersReqHeader = createAuthenticationHeader(req);
      const response = await restApi({method: 'post', url: generateAnmsCoreUrl(''), headers: usersReqHeader, data: utils.snakeCaseObject(filteredUser)});
      logger.debug(`Core users response status: ${response.status}`);
      if (response.status >= 400) {
        return next(Boom.badGateway('Error authenticating user'));
      }
      return res.status(201).json(_.pick(response.data, adminUsersWebSafeFields));
    } catch (error) {
      return next(Boom.badGateway('Error Creating User', error));
    }
  };

  exports.updateUserProfile = async function (req, res, next) {
    try {
      const userName = req.params.userName;;
      const userUpdate = req.body.data;
      if (!_.isString(userName)) {
        return next(Boom.badData('Invalid UserName'));
      }
      //Check for authorization
      const remoteUser = req.headers["x-remote-user"];
      if (_.isNil(remoteUser) || userName != remoteUser) {
        logger.info(`${remoteUser} is unauthorized to create profile of ${userName}`);
        return next(Boom.unauthorized('Cannot update profile of other user'));
      }
      const validData = _.isPlainObject(userUpdate);
      if (!validData) {
        return next(Boom.badData('Invalid User Data'));
      }
      logger.info("updateUser data: ", userUpdate);
      const usersReqHeader = createAuthenticationHeader(req);
      const requestUrl = generateAnmsCoreUrl(`/${userName}`);
      logger.info("Sending request to: ", requestUrl);
      const response = await restApi({method: 'put', url: requestUrl, headers: usersReqHeader, data: userUpdate, timeout: requestTimeOut});
      if (response.status >= 400 && response.status < 500) {
        const boomObj = Boom.boomify(new Error(), {statusCode: response.status, details: response.data});
        logger.info(boomObj);
        return response.status === 409 ? res.status(409).json(response.data.field) : next(boomObj);
      }
      if (response.status >= 500) {
        return next(Boom.internal('Internal server error'));
      }
      return res.sendStatus(response.status);
    } catch (error) {
      logger.error("Function error: ",error.message);
      return next(Boom.badGateway(error.message, error));
    }
  };

  // Function that only allows updating your own account (assuming you're not an admin)
  exports.updateUserDetails = async function (req, res, next) {
    try {
      const userId = req.params.id;
      const userUpdate = req.body.data;
      if (!_.isString(userId)) {
        return next(Boom.badData('Invalid User ID Type'));
      }
      const validData = _.isPlainObject(userUpdate);
      if (!validData) {
        return next(Boom.badData('Invalid User Data'));
      }
      // Security Check
      if ((req.user.id + '') !== userId) {
        return next(Boom.unauthorized('Unable to update profile.')); // we don't want to disclose ID exist...
      }
      const filteredUser = _.pick(userUpdate, profileUserFieldsArr);
      const hasUserOrg = _.has(filteredUser, 'organization');
      if (hasUserOrg) {
        filteredUser.details = {organization: userUpdate.organization};
        delete filteredUser.organization;
      }
      const usersReqHeader = createAuthenticationHeader(req);
      const response = await restApi({method: 'put', url: generateAnmsCoreUrl(`/${userId}`), headers: usersReqHeader, data: utils.snakeCaseObject(filteredUser)});
      logger.debug(`Core users response status: ${response.status}`);
      if (response.status >= 400 && response.status < 500) {
        return next(Boom.badGateway('Error authenticating user'));
      }
      if (response.status === 500) {
        logger.err(response.data);
        return next(Boom.internal('Internal Server Error', response.data));
      }
      return res.sendStatus(200);
    } catch (error) {
      return next(Boom.badGateway('Error Getting User Data', error));
    }
  };

  // Function that only allows updating your own account (assuming you're not an admin)
  exports.updateUserHashedPassword = async function (req, res, userId, hashed_password, next) {
    try {
      if (!_.isString(userId)) {
        return next(Boom.badData('Invalid User ID'));
      }
      const usersReqHeader = createAuthenticationHeader(req);
      const response = await restApi({method: 'put', url: generateAnmsCoreUrl(`/${userId}/password/hashed`), headers: usersReqHeader, data: {password: hashed_password}});
      logger.debug(`Core users response status: ${response.status}`);
      if (response.status >= 400) {
        return next(Boom.badGateway('Error updating users password'));
      }
      return res.sendStatus(200);
    } catch (error) {
      return next(Boom.badGateway('Error Changing User Password', error));
    }
  };

  exports.enableUser = async function (req, res, next) {

    try {
      const userId = req.params.id;
      if (!_.isString(userId)) {
        return next(Boom.badData('Invalid User ID'));
      }

      const usersReqHeader = createAuthenticationHeader(req);
      const response = await restApi({method: 'patch', url: generateAnmsCoreUrl(`/${userId}/enable`), headers: usersReqHeader});
      logger.debug(`Core users response status: ${response.status}`);
      if (response.status >= 400) {
        return next(Boom.badGateway('Error authenticating user'));
      }
      return res.status(200).json(response.data);

    } catch (error) {
      return next(Boom.badGateway('Error Enabling User', error));
    }

  };

  exports.disableUser = async function (req, res, next) {

    try {
      const userId = req.params.id;
      if (!_.isString(userId)) {
        return next(Boom.badData('Invalid User ID'));
      }

      const usersReqHeader = createAuthenticationHeader(req);
      const response = await restApi({method: 'patch', url: generateAnmsCoreUrl(`/${userId}/disable`), headers: usersReqHeader});
      logger.debug(`Core users response status: ${response.status}`);
      if (response.status >= 400) {
        return next(Boom.badGateway('Error authenticating user'));
      }
      return res.status(200).json(response.data);

    } catch (error) {
      return next(Boom.badGateway('Error Disabling User', error));
    }

  };

  function filterUserFields(req, res, userObj, filterFields) {
    if (userObj == null) {
      return res.sendStatus(404);
    }
    const canViewMore = _.some(filterFields, function (perm) {
      return _.includes(req.user.permissions, perm);
    });
    let filter = filterFields;
    if (canViewMore) {
      filter = adminUsersWebSafeFields;
    }
    const cleanedUser = _.pick(userObj, filter);
    return res.status(200).json(cleanedUser);
  }

  function generateAnmsCoreUrl(pathPart, params) {
    let coreUrlObject = _.cloneDeepWith(config.core.uri);
    let path = '/users' + pathPart;
    _.set(coreUrlObject, 'pathname', path);
    if(!_.isUndefined(params)){
      _.set(coreUrlObject, 'query', params);
    }
    return url.format(coreUrlObject);
  }

  function restApi(options) {
    return axios({
      ...options,
      validateStatus: () => true
    });
  }

  function createAuthenticationHeader(req) {
    return {
      'Authorization': req.headers.authorization,
      'accept': 'application/json'
    };
  }

  function createAutherizationHeader(req, authorization_fields) {
    let headers = {

    };
    for (var header_field of authorization_fields) {
      headers[authorization_fields] = authorization_fields;
    }
    return headers;
  }

})();
