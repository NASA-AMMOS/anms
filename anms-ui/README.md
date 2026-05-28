<!--
Copyright (c) 2026 The Johns Hopkins University Applied Physics
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
# ANMS-UI Angular
## Software Stack
- Angular 21
- Bootstrap 5

### Configuration
For local development and remote VM server use `proxy.confiig.json`  
_NOTE_ `proxy.config.json` is used by default for dev-server profile builds. Change this behavior under `angular.json`.
Currently, proxy config is set to `anms-test` VM.  
Environment setup is done with `src/environments` `environment.ts` for deployment and `environment.development.ts` for development

### Install dependencies and Run
- Install all required dependency defined under `package.json` with `npm install`
  - Note that npm requires `node v22.12.0`
  - All modules are installed under `node_modules` directory
  - Install `ng` globally with `npm install -g @angular/cli`
- Run anms-ui with `ng serve`
  - Open web app in a browser `localhost:4200`

## Build and Deploy
Build application for deployment with `ng build`  
The deployment ready output `dist/anms-ui` Copy the content to deployment directory of a web app server. For example, if using tomcat, then `webapps/anms-ui`.

