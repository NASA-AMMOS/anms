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

  // Load app configuration
  const fs = require('fs');
  const url = require('url');
  const dns = require('dns');
  const _ = require('lodash');
  const crypto = require('crypto');
  const path = require('path');
  const rootPath = path.normalize(__dirname + '/../..');
  const configEnvParser = require('./configUtils').init(path.join(rootPath, 'config.yaml'), 'ANMS_UI');
  if (configEnvParser.getFromFileCfg('nodeEnv', 'development') === 'production') {
    process.env.NODE_ENV = 'production';
  }
  const publicRoot = 'public';
  const releaseRoot = 'release'; // yarn build
  
  const config = {
    root: rootPath,
    logPath: null,
    dns: null, // Set's DNS NodeJS will use
    debug: true,
    tests: false,
    logger: true,
    proxied: false,
    proxiedSSL: false,
    proxyBase: null,
    relativeBase: true,
    maxWorkers: 16,
    clustering: false,
    enableCSRF: false,
    nodeEnv: process.env.NODE_ENV || 'development',
    tempDir: path.join(rootPath, 'tmp'),
    dataDir: path.join(rootPath, 'data'),
    uris: {
      web: null,
      sslWeb: null,
      api: null,
      sslApi: null,
      webBase: '/',
      apiBase: '/api/',
      webBasePath: null,
      apiBasePath: null,
    },
    net: {
      port: 9030,
      sslPort: 9443,
      proto: 'http',
      sslProto: 'https',
      host: 'localhost',
      sslHost: 'localhost',
      bindInterface: '0.0.0.0',
      bindIPCSocketPath: null
    },
    ssl: {
      enabled: false,
      redirect: false,
      hstsLock: false,
      http2: false,
      crt: 'default.crt',
      key: 'default.key',
      phrase: null
    },
    client: {
      name: 'anms',
      version: '0.1.0',
      root: path.join(rootPath, releaseRoot),
      app: path.join(rootPath, publicRoot, 'app'),
      styles: path.join(rootPath, releaseRoot, 'styles'),
      assets: path.join(rootPath, releaseRoot, 'assets'),
      scripts: path.join(rootPath, releaseRoot, 'scripts'),
      npmAssets: path.join(rootPath, publicRoot, 'node_modules'),
      favicon: path.join(rootPath, releaseRoot, 'favicon.png'),
      index: path.join(rootPath, releaseRoot, 'index.html'),
      error: path.join(rootPath, releaseRoot, 'assets', 'views', '404.html'),
      error500: path.join(rootPath, releaseRoot, 'assets', 'views', '500.html')
    },
    core: {
      uri: {
        protocol: 'http',
        hostname: configEnvParser.getFromFileCfg('CORE_HOSTNAME', 'anms-core'),
        port: configEnvParser.getFromFileCfg('CORE_PORT', '5555'),
        pathname: '/'
      },
      parsedUri: null
    },
    auth: {
      rateLimiter: true,
      requestLimitWindow: 60 * 60 * 1000, // 1 hour window
      requestLimit: 3600 // 3600 request per requestLimitWindow
    },
    redis: {
      enabled: true,
      limiterPrefix: 'limiter:',
      sessionPrefix: 'session:',
      parsedUri: null,
      uri: {
        protocol: 'redis',
        hostname: configEnvParser.getFromFileCfg('REDIS_HOSTNAME', 'redis'),
        port: configEnvParser.getFromFileCfg('REDIS_PORT', '6379'),
        pathname: '0', // db number
        slashes: true
      },
      opts: {
        parser: 'javascript',
        prefix: 'cl:'
      }
    },
    smtp: {
      enabled: false,
      defaultFrom: 'AMMOS ANMS <noreply@anms.jhuapl.edu>',
      clientOpts: {
        pool: false,
        host: '',
        port: 25,
        secure: false, // true only for port 465,
        auth: null, // {user: null, pass: null}
        authMethod: null, // e.g. PLAIN
        requireTLS: true,
        tls: {
          rejectUnauthorized: true
        },
        debug: false
      }
    },
  };

  // ** READ IN ENVIRONMENT SETTINGS AND NORMALIZE, DO NOT TOUCH!!! ** //
  configEnvParser.extendConfig(config);

  // Normalize URI's
  config.redis.parsedUri = url.format(config.redis.uri);

  // Normalize Base's
  config.uris.webBase = path.posix.join('/', config.uris.webBase, '/');
  config.uris.apiBase = path.posix.join('/', config.uris.apiBase, '/');
  config.proxyBase = _.isString(config.proxyBase) ? path.posix.join('/', config.proxyBase, '/') : null;

  // Populate Server Uri's
  config.uris.web = url.format({protocol: config.net.proto, port: config.net.port, hostname: config.net.host, pathname: config.uris.webBase});
  config.uris.sslWeb = url.format({protocol: config.net.sslProto, port: config.net.sslPort, hostname: config.net.sslHost, pathname: config.uris.webBase});
  config.uris.api = url.format({protocol: config.net.proto, port: config.net.port, hostname: config.net.host, pathname: config.uris.apiBase});
  config.uris.sslApi = url.format({protocol: config.net.sslProto, port: config.net.sslPort, hostname: config.net.sslHost, pathname: config.uris.apiBase});

  // Perform Relative or Absolute Path Mappings
  if (config.relativeBase === true) {
    if (_.isString(config.proxyBase)) {
      config.uris.webBasePath = path.posix.join(config.proxyBase, config.uris.webBase);
      config.uris.apiBasePath = path.posix.join(config.proxyBase, config.uris.apiBase);
    } else {
      config.uris.webBasePath = config.uris.webBase;
      config.uris.apiBasePath = config.uris.apiBase;
    }
  } else {
    const webResolver = config.ssl.enabled ? config.uris.sslWeb : config.uris.web;
    const apiResolver = config.ssl.enabled ? config.uris.sslApi : config.uris.api;
    if (_.isString(config.proxyBase)) {
      config.uris.webBasePath = url.resolve(webResolver, path.posix.join(config.proxyBase, config.uris.webBase));
      config.uris.apiBasePath = url.resolve(apiResolver, path.posix.join(config.proxyBase, config.uris.apiBase));
    } else {
      config.uris.webBasePath = url.resolve(webResolver, config.uris.webBase);
      config.uris.apiBasePath = url.resolve(apiResolver, config.uris.apiBase);
    }
  }

  // Configure DNS For NodeJS
  if (config.dns !== null) {
    if (_.isString(config.dns)) {
      dns.setServers([config.dns]);
    } else if (_.isArray(config.dns)) {
      dns.setServers(config.dns);
    }
  }


  config.auth.sessionSecret = config.debug === true ? 'bunEt@aT@Ech4pRaRu2a4A5#?u&?UfUF' : crypto.randomBytes(256).toString('hex');

  // Verify if custom path is provided to ssl ca_certs, otherwise, try to find them in ca_certs directory
  if (config.ssl.enabled) {
    const isValidCrt = _.isString(config.ssl.crt);
    const isValidKey = _.isString(config.ssl.key);
    if (!isValidCrt || !isValidKey) {
      config.ssl.crt = null;
      config.ssl.key = null;
    } else {
      const potentialCrtPaths = [config.ssl.crt, path.join(rootPath, 'ca_certs', config.ssl.crt)];
      const potentialKeyPaths = [config.ssl.key, path.join(rootPath, 'ca_certs', config.ssl.key)];
      const crtPathExist = _.map(potentialCrtPaths, fs.existsSync);
      const keyPathExist = _.map(potentialKeyPaths, fs.existsSync);
      _.some(potentialCrtPaths, function (path, idx) {
        if (crtPathExist[idx] === true) {
          config.ssl.crt = fs.readFileSync(path);
          return true;
        } else {
          return false;
        }
      });
      _.some(potentialKeyPaths, function (path, idx) {
        if (keyPathExist[idx] === true) {
          config.ssl.key = fs.readFileSync(path);
          return true;
        } else {
          return false;
        }
      });
      // cert is still not a buffer, lets try to ingest it as a buffer...
      if (!_.isBuffer(config.ssl.crt)) {
        config.ssl.crt = Buffer.from(config.ssl.crt, 'utf8');
      }
      // key is still not a buffer, lets try to ingest it as a buffer...
      if (!_.isBuffer(config.ssl.key)) {
        config.ssl.key = Buffer.from(config.ssl.key, 'utf8');
      }
    }
  }

  if (_.isString(config.net.bindIPCSocketPath)) {
    if (process.platform === 'win32') {
      config.net.bindIPCSocketPath = null;
    } else {
      try {
        const socketPath = path.dirname(config.net.bindIPCSocketPath);
        fs.accessSync(socketPath, fs.constants.R_OK | fs.constants.W_OK);
        if (fs.existsSync(config.net.bindIPCSocketPath)) {
          fs.unlinkSync(config.net.bindIPCSocketPath);
        }
      } catch (e) {
        config.net.bindIPCSocketPath = null;
      }
    }
  }

  config.core.parsedUri = url.format(config.core.uri);
  


  module.exports = config;

})();
