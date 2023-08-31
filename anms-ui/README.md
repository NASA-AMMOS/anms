<!--
Copyright (c) 2023 The Johns Hopkins University Applied Physics
Laboratory LLC.

This file is part of the Asynchronous Network Management System (ANMS).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This work was performed for the Jet Propulsion Laboratory, California
Institute of Technology, sponsored by the United States Government under
the prime contract 80NM0018D0004 between the Caltech and NASA under
subcontract 1658085.
-->
## AMMOS ANMS Web Interface ##

## COPYRIGHT NOTICE 

* Copyright (C) 2015-2022 The Johns Hopkins University Applied Physics Laboratory LLC.

### Software Requirements (Subject to Update) ###

* [NodeJS](https://nodejs.org/) (Version 8.X, 10.X, 12.X)
* [Yarn](https://yarnpkg.com/) (Version >= 1.12.X, Not 2.X) `npm install -g yarn`
* [Redis](https://redis.io/) (Version 5.X, 6.X)(configure the URL in `config.js`)

# OSX/Linux Quick Build 

* Make sure to have above dependencies.
* Shortcut: `make build` to configure the web/python portions.
  * Make will not install NodeJS/Yarn/Redis itself.
* Use `make up` to bring up the system, do not use `make up` for development.

#### Building the System ####

The web application resides in the `./public` directory.
The web server resides in the `./server` directory.
In order to build and install the two components run the script `prep_packages.sh`.

#### Configuration ####
A default set of configuration values are defined in `server/shared/config.js`.  Configuration items may be overridden via a configuration file or by setting environment variables.  Configuration items read from configuration file override the default values and items read from environment variables override both those defined in a configuration file and the default configuration.

A configuration file named `config.yaml` may be placed in the root of the application directory.  This file is expected to contain configuration in YAML file format (e.g. `name: obj or value`).  Configuration items are defined hierarchically in the same structure as they are defined in `config.js`.  Configuration items defined in this file will override the default configuration value with a matching hierarchy of names.  A subset of the elements of a nested object may be included and only those values provided will be overridden.

Environment variables with the prefix "ANMS_" are applied as configuration overrides.  The corresponding environment variable name for a configuration item is the concatenation of all names along the path through the object tree with:
* a prefixed by `ANMS_`
* all names upper-case
* name elements delimited by "_"

For example, given the default configuration of:
```javascript:w
...
core: {
  uri: {
    protocol: 'http',
    hostname: 'anms-core',
    port: '5555',
    pathname: '/'
  },
  parsedUri: null
},
...
```
Overriding the hostname can be accomplished through the environment variable named `ANMS_CORE_NAME`.

#### Running the application ####

Once these applications are configured:

* Run the Server Middleware, from the `server` directory, run `node server.js`
* For Web Development, from the `public` directory, run `yarn run serve`
  * For the same result with no hot-module swap (browser refresh required each change), run `yarn run build:watch` instead.
* For Non-Web Development, from the `public` directory, run `yarn run build`

#### Building the System (Docker) ####
* Make sure to have the latest Docker (19+) and Docker Compose (1.27+) installed
* From the root directory of the project, run `make docker-up` to build and run the system

Important Note:

>>>
The intention is to have webpack's development server hot-plug the assets and use the NodeJS to actually render the web application.
Because of this, for web development, `yarn run serve` has to be running and Node has to be running.
Hence, the URL provided by `yarn run serve` is setup to actually redirect you to the configured URL for the NodeJS server.
Additionally, this allows using our NodeJS for development directly, which is desirable if we want to target the deployment environment.
>>>

Enabling HTTP(s)/HTTP2 (for development only):

* On the certs directory run: `openssl req -x509 -newkey rsa:2048 -nodes -sha256 -subj '/CN=localhost' -keyout default.key -out default.crt`
* Set `config.ssl.enabled` to `true` and `config.ssl.http2` to `true` in `config.js`





