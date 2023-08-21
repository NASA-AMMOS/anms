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
  const fs = require('fs');
  const yaml = require('js-yaml');
  const winston = require('winston');

  module.exports = {
    init: initUtils
  };

  function initUtils(filePath, _env_prefix) {
    return new ConfigParser(filePath, _env_prefix);
  }

  function ConfigParser(filePath, _env_prefix) {
    if (!(this instanceof ConfigParser)) {
      return new ConfigParser(filePath, _env_prefix);
    }
    ConfigParser.types = Object.freeze({
      INTEGER: 0,
      FLOAT: 1,
      BOOLEAN: 2,
      STRING: 3,
      NULL: 4,
      UNSUPPORTED: -1
    });
    this.envPrefix = _env_prefix;
    this.fileCfg = configYamlLoader(filePath);
    this.extendConfig = function (configObj) {
      const self = this;
      // Paths that will be extended via config file or env variables...
      const pathsToExtend = parseObjPaths(configObj);
      _.each(pathsToExtend, function (path) {
        const objValue = _.get(configObj, path, null);
        const objType = self.getType(objValue);
        const envName = _.toUpper(_.snakeCase(path));
        const envVal = self.getFromEnv(envName, objType, null);
        if (envVal === null) {
          _.set(configObj, path, self.getFromFileCfg(path, _.get(configObj, path, null)));
        } else {
          _.set(configObj, path, envVal);
        }
      });
    };
    this.getType = function (value) {
      // order of evaluation is strategic...
      const isBoolean = _.isBoolean(value) || value === 'true' || value === 'false';
      const isInteger = _.isInteger(value);
      const isFloat = _.isFinite(value) && !_.isInteger(value);
      const isString = _.isString(value);
      const isNull = _.isNull(value);
      if (isNull) {
        return ConfigParser.types.NULL;
      } else if (isBoolean) {
        return ConfigParser.types.BOOLEAN;
      } else if (isInteger) {
        return ConfigParser.types.INTEGER;
      } else if (isFloat) {
        return ConfigParser.types.FLOAT;
      } else if (isString) {
        return ConfigParser.types.STRING;
      } else {
        return ConfigParser.types.UNSUPPORTED;
      }
    };
    this.getFromFileCfg = function (path, _default) {
      if (_.isUndefined(_default)) {
        _default = null;
      }
      const pathResult = _.get(this.fileCfg, path, _default);
      const isEnv = _.isString(pathResult) && _.startsWith(pathResult, '$');
      return isEnv ? _.get(process.env, _.trimStart(pathResult, '$'), _default) : pathResult;
    };
    this.getFromEnv = function (name, type, _default) {
      if (_.isUndefined(_default)) {
        _default = null;
      }
      const parsedName = _.isString(this.envPrefix) ? this.envPrefix + '_' + _.toUpper(name) : _.toUpper(name);
      let value = _.get(process.env, parsedName, _default);
      if (_.isNull(value)) {
        return value;
      }
      switch (type) {
        case ConfigParser.types.INTEGER:
          value = _.parseInt(value, 10);
          break;
        case ConfigParser.types.FLOAT:
          value = parseFloat(value);
          break;
        case ConfigParser.types.BOOLEAN:
          value = _.toLower(value) === 'true' ? true : _.toLower(value) === 'false' ? false : value;
          break;
        case ConfigParser.types.STRING:
          break;
        default:
          break;
      }
      return value;
    };
  }

  function configYamlLoader(path) {
    const configExists = fs.existsSync(path);
    if (configExists === true) {
      winston.info('Loaded Configuration File', path);
      const yamlBlob = fs.readFileSync(path, 'utf8');
      const result = yaml.safeLoad(yamlBlob);
      return _.isPlainObject(result) ? result : {};
    } else {
      return {};
    }
  }

  // http://stackoverflow.com/questions/36128171/list-all-possible-paths-using-lodash
  // modified a bit
  function parseObjPaths(obj, parentKey) {
    let result;
    if (_.isArray(obj)) {
      let idx = 0;
      result = _.flatMap(obj, function (obj) {
        return parseObjPaths(obj, (parentKey || '') + '[' + idx++ + ']');
      });
    }
    else if (_.isPlainObject(obj)) {
      result = _.flatMap(_.keys(obj), function (key) {
        return _.map(parseObjPaths(obj[key], key), function (subkey) {
          return (parentKey ? parentKey + '.' : '') + subkey;
        });
      });
    }
    else {
      result = [];
    }
    // remove roots
    _.remove(result, function (path) {
      return _.some(result, function (res) {
        return _.startsWith(res, path + '.') || _.startsWith(res, path + '[');
      });
    });
    return _.concat(result, parentKey || []);
  }

})();
