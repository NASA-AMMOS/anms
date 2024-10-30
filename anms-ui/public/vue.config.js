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
  "use strict";

  const _ = require("lodash");
  const path = require("path");
  const webpack = require("webpack");
  const CopyPlugin = require("copy-webpack-plugin");

  const config = require("../server/shared/config");

  const publicDir = path.join(config.root, "public");
  const releaseDir = path.join(config.root, "release");
  const isProduction = process.env.NODE_ENV === "production";

  const scriptsOutput = path.join("assets", "scripts");
  const stylesOutput = path.join("assets", "styles");
  const imagesOutput = path.join("assets", "images");
  const publicAppDir = path.join(publicDir, "app");
  const publicAssetsDir = path.join(publicDir, "assets");
  const publicModulesDir = path.join(publicDir, "node_modules");

  const faviconGlob = path.join(publicDir, "favicon.png");
  const scriptsGlob = path.join(publicDir, "assets", "scripts", "**/*.js");
  const viewsGlob = path.join(publicDir, "assets", "views", "**/*.html");
  const stylesGlob = path.join(publicDir, "assets", "styles", "**/*.scss");

  // Patch: FIPS-140 mode disallows md4 and md5, but webpack hardcodes it all over the place: https://github.com/webpack/webpack/issues/13572
  const crypto = require("crypto");
  const crypto_orig_createHash = crypto.createHash;
  const algoBad = new Set(["md4", "md5", "sha1"]);
  const console = require("console");
  crypto.createHash = function (algorithm) {
    try {
      return crypto_orig_createHash(
        algoBad.has(algorithm) ? "sha256" : algorithm
      );
    } catch (err) {
      console.error("bad algo", algorithm, err);
      throw err;
    }
  };

  const htmlMinifierOpts = {
    ignoreCustomComments: [
      /Johns Hopkins University Applied Physics Laboratory. All Rights Reserved/,
    ],
    removeComments: true,
    removeRedundantAttributes: false,
    removeScriptTypeAttributes: false,
    removeStyleLinkTypeAttributes: false,
    useShortDoctype: false,
    collapseWhitespace: true,
    caseSensitive: true,
    minifyCSS: true,
    minifyJS: { compress: false, output: { comments: "some", quote_style: 3 } },
  };

  // vue.config.js
  module.exports = {
    publicPath: "", // we use the <base> tag...
    filenameHashing: true,
    outputDir: releaseDir,
    // relative to outputDir
    assetsDir: "assets",
    lintOnSave: false,
    runtimeCompiler: true,
    productionSourceMap: !isProduction,
    // cannot use parallel mode with the crypto fix above
    parallel: false,
    // Defaults: https://github.com/vuejs/vue-cli/blob/v3.8.2/packages/@vue/cli-service/lib/commands/serve.js#L138
    devServer: {
      host: config.net.bindInterface,
      port: config.net.port + 1,
      onBeforeSetupMiddleware: function (devServer) {
        devServer.app.all("*", function (req, res) {
          res.redirect(
            302,
            config.ssl.enabled ? config.uris.sslWeb : config.uris.web
          ); // 302 to prevent permanent...
        });
      },
      devMiddleware: {
        writeToDisk: true,
        stats: "minimal",
      },
      static: {
        directory: publicAssetsDir,
      },
      hot: true, // set to false to disable hot-replacement
      client: {
        logging: "info",
      },
      historyApiFallback: false,
    },
    pages: {
      index: {
        // entry for the page
        entry: "app/main.js",
        // the source template
        template: "index.html",
        // output as outputDir/index.html
        filename: "index.html",
        // chunks to include on this page
        // chunks: ['chunk-vendors', 'chunk-common', 'index'] // default
      },
    },
    configureWebpack: (config) => {
      let configToMerge = {
        plugins: [
          new webpack.IgnorePlugin({
            resourceRegExp: /^\.\/locale$/,
            contextRegExp: /moment$/,
          }),
          new CopyPlugin([
            { from: viewsGlob, to: releaseDir, context: publicDir },
            { from: faviconGlob, to: releaseDir, context: publicDir },
          ]), // todo (minify, etc.)
        ],
        resolve: {
          fallback: {
            crypto: false,
            stream: false,
          },
        },
      };
      if (isProduction) {
        // change minifier options
        // config.optimization.minimizer[0].options
      }
      return configToMerge; // must always return if we want to merge it
    },
    chainWebpack: (config) => {
      // Adjust Aliases
      config.resolve.alias.delete("@");
      config.resolve.alias.set("@app", publicAppDir);
      config.resolve.alias.set("@assets", publicAssetsDir);
      config.resolve.alias.set("@modules", publicModulesDir);
      // https://github.com/vuejs/vue-cli/issues/2436
      config.plugins.delete("copy"); // we may use public dir as main dir in the future
      // Remove the prefetch/preload plugins if it causes issues with server-side templating...
      // config.plugins.delete('prefetch-index');
      // config.plugins.delete('preload-index');
      // Adjust JS output path
      const jsOutputName = path.basename(config.output.get("filename"));
      const jsOutputHashName = path.basename(
        config.output.get("chunkFilename")
      );
      config.output.set("filename", path.join(scriptsOutput, jsOutputName));
      config.output.set(
        "chunkFilename",
        path.join(scriptsOutput, jsOutputHashName)
      );
      if (isProduction) {
        // Adjust CSS output path
        config.plugin("extract-css").tap((args) => {
          let options = args[0];
          const outputName = path.basename(options.filename);
          const outputHashName = path.basename(options.chunkFilename);
          options.filename = path.join(stylesOutput, outputName);
          options.chunkFilename = path.join(stylesOutput, outputHashName);
          return args;
        });
        // Adjust HTML Minification
        config.plugin("html-index").tap((args) => {
          let options = args[0];
          options.minify = htmlMinifierOpts;
          return args;
        });
      }
      // Set whitespace to original value (default is condense, used to be preserve)
      config.module
        .rule("vue")
        .use("vue-loader")
        .loader("vue-loader")
        .tap((options) => {
          options.compilerOptions.whitespace = "preserve";
          return options;
        });
      // Add Worker Loader
      config.module.rule("js").exclude.add(/\.worker\.js$/);
      config.module
        .rule("web-worker")
        .test(/\.worker\.js$/)
        .use("worker-loader")
        .loader("worker-loader")
        .options({
          name: "[hash:8].[name].[ext]", // path.join(scriptsOutput, '[hash:8].[name].[ext]') // <-- enable in the future when it's easier to get pyodide
        });
    },
    pluginOptions: {
      "style-resources-loader": {
        preProcessor: "scss",
        patterns: [
          // stylesGlob
        ],
      },
    },
  };
})();
