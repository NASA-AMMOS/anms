# ANMS-UI Angular
## Software Stack
- Angular 21
- Bootstrap 5

## Development
Project source files are Located under `angular-port/anms-ui` until VUE to Angular port is complete.  

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

