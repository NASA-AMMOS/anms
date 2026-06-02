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

  // IMPORTANT: ROLES NUMBERS DO NOT WARRANT LEVEL OF ACCESS (it's just a simplification for mapping)
  const SYSTEM_PERMISSIONS = {
    PERMISSION_ALL: 0,
    PERMISSION_ADD_USER: 100,
    PERMISSION_EDIT_USER: 200,
    PERMISSION_VIEW_USER: 300,
  };
  const SYSTEM_PERMISSIONS_INV = _.invert(SYSTEM_PERMISSIONS);

  // TODO: role planner, etc.
  const SYSTEM_ROLES = {
    ROLE_SUPER_ADMIN: 0,
    ROLE_ADMIN: 1,
    ROLE_USER: 2
  };
  const SYSTEM_ROLES_INV = _.invert(SYSTEM_ROLES);

  const SYSTEM_DEFAULT_MAPPINGS = {};
  const SYSTEM_DEFAULT_MAPPINGS_INV = {};
  SYSTEM_DEFAULT_MAPPINGS[SYSTEM_ROLES.ROLE_SUPER_ADMIN] = [SYSTEM_PERMISSIONS.PERMISSION_ALL];
  SYSTEM_DEFAULT_MAPPINGS_INV[SYSTEM_ROLES.ROLE_SUPER_ADMIN] = permissionMappingInverter(SYSTEM_ROLES.ROLE_SUPER_ADMIN);
  SYSTEM_DEFAULT_MAPPINGS[SYSTEM_ROLES.ROLE_ADMIN] = [
    SYSTEM_PERMISSIONS.PERMISSION_ADD_USER,
    SYSTEM_PERMISSIONS.PERMISSION_EDIT_USER,
    SYSTEM_PERMISSIONS.PERMISSION_VIEW_USER,
  ];
  SYSTEM_DEFAULT_MAPPINGS_INV[SYSTEM_ROLES.ROLE_ADMIN] = permissionMappingInverter(SYSTEM_ROLES.ROLE_ADMIN);
  SYSTEM_DEFAULT_MAPPINGS_INV[SYSTEM_ROLES_INV[SYSTEM_ROLES.ROLE_ADMIN]] = SYSTEM_DEFAULT_MAPPINGS[SYSTEM_ROLES.ROLE_ADMIN];
  SYSTEM_DEFAULT_MAPPINGS[SYSTEM_ROLES.ROLE_USER] = [];
  SYSTEM_DEFAULT_MAPPINGS_INV[SYSTEM_ROLES.ROLE_USER] = permissionMappingInverter(SYSTEM_ROLES.ROLE_USER);

  function permissionMappingInverter(role) {
    return _.map(SYSTEM_DEFAULT_MAPPINGS[role], function (perm) {
      return SYSTEM_PERMISSIONS_INV[perm];
    });
  }

  module.exports = {
    systemRoles: SYSTEM_ROLES,
    systemRolesInv: SYSTEM_ROLES_INV,
    systemPermissions: SYSTEM_PERMISSIONS,
    systemPermissionsInv: SYSTEM_PERMISSIONS_INV,
    systemMappings: SYSTEM_DEFAULT_MAPPINGS,
    systemMappingsInv: SYSTEM_DEFAULT_MAPPINGS_INV
  };

})();
