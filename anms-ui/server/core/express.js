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

  /**
   * Module dependencies.
   */
  const fs = require('fs');
  const hpp = require('hpp');
  const _ = require('lodash');
  const cors = require('cors');
  const path = require('path');
  const boom = require('@hapi/boom');
  const util = require('util');
  const csurf = require('csurf');
  const crypto = require('crypto');
  const helmet = require('helmet');
  const morgan = require('morgan');
  const redis = require('redis');
  const express = require('express');
  const nunjucks = require('nunjucks');
  const flash = require('connect-flash');
  const favicon = require('serve-favicon');
  const bodyParser = require('body-parser');
  const compression = require('compression');
  const session = require('express-session');
  const errorHandler = require('errorhandler');
  const cookieParser = require('cookie-parser');
  const methodOverride = require('method-override');
  const RedisStore = require('connect-redis')(session);
  const expressEnforcesSSL = require('express-enforces-ssl');

  const routes = require('./routes');
  const logger = require('../shared/logger');
  const config = require('../shared/config');

  module.exports = function (app) {

    // Configure trust of reverse proxy
    app.set('trust proxy', config.proxied);

    // Security settings
    app.disable('x-powered-by');
    app.use(helmet({
      hsts: false,
      frameguard: {
        action: 'sameorigin' // Set X-Frame: sameorigin to prevent click jacking site-framing by anyone
      },
      noCache: config.debug // avoid caching in debug mode
    }));
    if (config.ssl.enabled === true && config.ssl.hstsLock === true) {
      app.use(helmet.hsts());
      app.use(expressEnforcesSSL());
    }

    app.use(hpp({})); // Parameter Pollution attacks
    app.use(cors({origin: false})); // peace of mind

    // Enable gzip compression
    app.use(compression({}));

    nunjucks.configure(config.client.root, {
      autoescape: false,
      express: app,
      noCache: config.debug,
      watch: config.debug,
      tags: {
        blockStart: '<%',
        blockEnd: '%>',
        variableStart: '<$',
        variableEnd: '$>',
        commentStart: '<#',
        commentEnd: '#>'
      }
    });

    const staticFiles = express.static(path.join(config.client.root), {index: false});

    // we shouldn't have that many multiple pages to begin with, so this is ok...
    const indexHtmlPath = path.posix.join(config.uris.webBase, path.basename(config.client.index));

    //Setting the fav icon and static folders
    if (fs.existsSync(config.client.favicon)) {
      app.use(favicon(path.join(config.client.favicon)));
    }
    app.use(path.posix.join(config.uris.webBase, '/'), function (req, res, next) {
      // nunjucks will server-side render these...
      if (req.path === indexHtmlPath) {
        return next();
      }
      return staticFiles(req, res, next);
    });

    // Logging
    const morganEnv = (config.debug || config.tests) ? 'dev' : 'combined';
    app.use(morgan(morganEnv, {
      stream: {
        write: function (str) {
          logger.log(str);
        }
      }
    }));

    // Configure parsing Content Types (bodyParser should be above methodOverride)
    app.use(bodyParser.urlencoded({extended: false})); // parse application/x-www-form-urlencoded
    app.use(bodyParser.json({limit: '1mb'})); // parse application/json
    app.use(bodyParser.text({limit: '100kb'})); // parse text/plain
    // app.use(methodOverride()); // enables PUT, PATCH, and DELETE on <form></form>

    // Configure Cookie Parser (cookieParser should be above session)
    app.use(cookieParser(config.auth.sessionSecret)); // not needed since express-session 1.5

    // Configure Session Management
    const sessionStore = new RedisStore({
      client: (() => {
        if (!config.redis.enabled) {
          return {};
        }
        let rClient = redis.createClient(config.redis.parsedUri, config.redis.opts);
        rClient.unref(); // allows the program to exit once no more commands are pending...
        rClient.on('error', logger.error);
        return rClient;
      })(),
      prefix: config.redis.sessionPrefix,
      ttl: 86400000
    });
    const finalSessionStore = config.redis.enabled ? sessionStore : new session.MemoryStore();

    app.use(session({
      store: finalSessionStore,
      secret: config.auth.sessionSecret,
      name: 'anms.sid',
      proxy: config.proxied,
      rolling: true, // each request resets the session expiration clock
      resave: false, // don't save session if unmodified
      saveUninitialized: false, // Guest sessions are the easiest way to have CSRF token for login (don't create session until something stored)
      cookie: {
        path: config.uris.webBase,
        httpOnly: true,
        sameSite: 'Lax', // https://www.chromestatus.com/feature/5088147346030592
        maxAge: 86400000, // cookie expires after 1 day idle
        secure: config.ssl.enabled || (config.proxied && config.proxiedSSL)
      }
    }));

    // check for session store disconnection
    app.use(function (req, res, next) {
      if (!req.session) {
        return next(boom.badGateway('Problem establishing your session.')); // handle error
      }
      next(); // otherwise continue
    });

    app.use(flash());

    if (config.enableCSRF) {
      app.use(csurf({cookie: false})); // Using CSRF tokens...
      // Setting XSRF Cookie for Angular
      app.use(function (req, res, next) {
        res.cookie('XSRF-TOKEN', req.csrfToken());
        next();
      });
    }

    if (config.debug || config.tests) {
      app.use(errorHandler({
        dumpExceptions: true,
        showStack: true
      }));
      app.set('view options', {
        pretty: true
      });
    }

    // Init Api Routes (Don't Cache This Ever?)
    app.use(config.uris.apiBase, helmet.noCache(), routes.api);

    // Init Web Routes
    app.use(config.uris.webBase, routes.web);

    app.use(function responseErrorHandler(err, req, res, next) {
      logger.warn('responseErrorHandler', err);
      if (_.get(err, 'isBoom') === true) {
        res.status(err.output.statusCode).json(err.message);
      } else if (_.has(err, 'code') && _.has(err, 'message') && err.code >= 400) {
        let boomErr;
        if (_.isError(err)) {
          boomErr = boom.boomify(err, {statusCode: err.code, message: err.message});
        } else {
          boomErr = new boom(err.message, {statusCode: err.code});
        }
        res.status(err.code).json(boomErr.output);
      } else { // Not Handled
        next(err);
      }
    });

    // NOTE: next must be here even if it's not used
    app.use(function unknownErrorHandler(err, req, res, next) { // no middleware responded

      err = err || {};
      logger.err('unknownErrorHandler', err);
      res.status(500);

      // respond with json
      if (req.accepts('json') && _.startsWith(req.url, config.uris.apiBase)) {
        res.json('Resource does not exists.');
      }

      // respond with html page
      else if (req.accepts('html')) {
        res.type('html').sendFile(config.client.error);
      }

      // respond with text if default
      else {
        res.type('txt').send('Resource does not exists.');
      }

    });

    return app;

  };

})();
