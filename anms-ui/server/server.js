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

  // Global Modules

  const fs = require('fs');
  const url = require('url');
  const _ = require('lodash');
  const path = require('path');
  const http = require('http');
  const https = require('https');
  const http2 = require('spdy'); // replace with http2 when express v5 comes out
  const process = require('process');
  const winston = require('winston');
  const cluster = require('cluster');
  const express = require('express');

  // Local Modules
  const logger = require('./shared/logger');
  const config = require('./shared/config');
  const initHandlers = require('./init');

  // If using v8 profiling, disable this
  if (module.parent) {
    throw new Error('server.js must be run in its own process');
  }

  // Patch: FIPS-140 mode disallows md4 and md5, but some modules hardcode algorithms
  const crypto = require("crypto");
  const crypto_orig_createHash = crypto.createHash;
  const algoBad = new Set(["md4", "md5", "sha1"]);
  const console = require('console');
  crypto.createHash = function(algorithm) {
    try {
      return crypto_orig_createHash(algoBad.has(algorithm) ? "sha256" : algorithm);
    }
    catch (err) {
      console.error('bad algo', algorithm, err);
      throw err;
    }
  };

  // Server running in debug mode (avoid child processes to use same debug port if clustering)
  const isDebug = process.execArgv.some(function (arg) {
    // Regex taken from https://github.com/joyent/node/commit/43ec1b1c2e77d21c7571acd39860b9783aaf5175
    return /^(--debug|--debug-brk)(=\d+)?$/.test(arg);
  });

  if (cluster.isMaster || process.env.pm_id === '0' || process.env.NODE_APP_INSTANCE === '0') {
    winston.info('Starting Application with Configuration:\n', JSON.stringify(config, null, 4));
    initHandlers.initDefaults(); // Init
  }

  if (config.clustering === true && cluster.isMaster && !isDebug) {

    const numCPUs = require('os').cpus().length;
    const numWorkers = (numCPUs <= config.maxWorkers) ? numCPUs : config.maxWorkers;

    for (let i = 0; i < numWorkers; ++i) {
      cluster.fork();
    }

    // Log when our workers are alive
    cluster.on('online', function (worker) {
      logger.info('Worker', worker.id, 'alive and well.');
    });

    // Listen for dying workers
    cluster.on('exit', function (worker) {
      // Replace the dead worker, we're not sentimental
      logger.err('Worker ' + worker.id + ' died :(');
      cluster.fork();
    });

  } else {

    let server, redirectServer;
    let serverSocketOpts = {};
    const app = express();

    // Express settings
    require('./core/express')(app);

    // IPC Handler
    if (config.net.bindIPCSocketPath !== null) {
      serverSocketOpts.path = config.net.bindIPCSocketPath;
    } else {
      serverSocketOpts.port = config.ssl.enabled ? config.net.sslPort : config.net.port;
      serverSocketOpts.host = config.net.bindInterface;
    }

    // Subtle Warning
    if (config.net.port === config.net.sslPort) {
      logger.warn('SSL Port and Port are the same!!!');
    }

    if (config.ssl.enabled) {
      const shouldRedirect = config.ssl.redirect === true && config.net.port !== config.net.sslPort && config.net.bindIPCSocketPath === null;
      // redirects not supported in IPC mode
      if (shouldRedirect) {
        const redirectApp = express();
        redirectApp.get('*', function (req, res) {
          res.redirect(301, url.format({protocol: config.net.sslProto, port: config.net.sslPort, hostname: config.net.sslHost}));
        });
        redirectServer = http.createServer(redirectApp);
        redirectServer.listen(config.net.port, config.net.bindInterface, function () {
          logger.info('Listening on', config.uris.web, 'for HTTP traffic', config.net.bindInterface);
        });
      }
      if (config.ssl.http2) {
        // TODO: change to createSecureServer when using http2 module
        server = http2.createServer({key: config.ssl.key, cert: config.ssl.crt, passphrase: config.ssl.phrase}, app);
      } else {
        server = https.createServer({key: config.ssl.key, cert: config.ssl.crt, passphrase: config.ssl.phrase}, app);
      }
      server.listen(serverSocketOpts, function () {
        if (config.net.bindIPCSocketPath !== null) {
          logger.info('Listening on', server.address(), 'for HTTPS traffic');
        } else {
          logger.info('Listening on', config.uris.sslWeb, 'for HTTPS traffic on', config.net.bindInterface);
        }
      });
    } else {
      // TODO: change to http2.createServer(app) when using http2 module
      server = config.ssl.http2 ? http2.createServer({spdy: {ssl: false}}, app) : http.createServer(app);
      server.listen(serverSocketOpts, function () {
        if (config.net.bindIPCSocketPath !== null) {
          logger.info('Listening on', server.address(), 'for HTTP traffic');
        } else {
          logger.info('Listening on', config.uris.web, 'for HTTP traffic on', config.net.bindInterface);
        }
        if (config.ssl.http2) {
          logger.warn('Warning! There are no browsers known that support unencrypted HTTP/2 at this time.');
          logger.warn('Disable http2 if the browser is the end client or check https://http2.github.io/faq/#does-http2-require-encryption');
        }
      });
    }

    // exit hook
    if (process.platform !== 'win32') {
      process.on('SIGINT', (code) => {
        logger.log(code, 'received... Shutting Down Server...');
        _.hasIn(server, 'close') ? server.close() : _.noop();
        _.hasIn(redirectServer, 'close') ? redirectServer.close() : _.noop();
        process.exit(0);
      });
      process.on('SIGTERM', (code) => {
        logger.log(code, 'received... Shutting Down Server...');
        _.hasIn(server, 'close') ? server.close() : _.noop();
        _.hasIn(redirectServer, 'close') ? redirectServer.close() : _.noop();
        process.exit(0);
      });
    }

    //expose app
    exports = module.exports = app;

  }

}());
