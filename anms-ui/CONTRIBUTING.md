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
### Development Code Guidelines ###

###### Coding Philosophy [Zen](https://www.python.org/dev/peps/pep-0020/):

>- **Beautiful** is better than ugly.
>- **Explicit** is better than implicit.
>- **Simple** is better than complex.
>- Complex is better than complicated.
>- **Flat** is better than nested.
>- Sparse is better than dense.
>- **Readability** counts.
>- Special cases aren't special enough to break the rules.
>  - Although practicality beats purity.
>- Errors should never pass silently.
>  - Unless explicitly silenced.
>- In the face of ambiguity, refuse the temptation to guess.
>- There should be one-- and preferably only one --obvious way to do it.
>  - Although that way may not be obvious at first unless you're Dutch.
>- Now is better than never.
>  - Although never is often better than \*right\* now.
>- If the implementation is hard to explain, it's a bad idea.
>- If the implementation is easy to explain, it may be a good idea.
>- **Namespaces** are one honking great idea -- let's do more of those!
>- **Conventions** over configuration, when it makes sense


###### General Code Style ([Code Style Guide](http://google-styleguide.googlecode.com/svn/trunk/javascriptguide.xml)):
    indent_style = space
    indent_size = 2
    continuation_indent_size = 4
    end_of_line = lf
    charset = utf-8
    trim_trailing_whitespace = true
    insert_final_newline = true
* The `.editorconfig` file is used to enforce some of these settings on common development IDE's, see [EditorConfig](http://editorconfig.org/).

###### Python Code Style
* Follow Pep8 with some exclusions as needed.
* TBD: pylint and flake8 should be enabled in the future to verify this.

###### Vue Code Style
* VueJS code should adhere as best as possible to the following style guidelines:
  * [Vue JS Style Guide](https://vuejs.org/v2/style-guide/)
  * [Vue JS Training](https://www.fullstack.io/30-days-of-vue)
  * Recommended browser extension for VueJS development: https://github.com/vuejs/vue-devtools

###### NodeJS Code Style
* Most of above applies to NodeJS code as well using best judgement; some good starting points:
  * [Guide 1](https://github.com/felixge/node-style-guide)
  * [Guide 2](https://github.com/RisingStack/node-style-guide)

###### Collection Manipulations/Transformation (JS)
* When dealing with any type of array, object, strings and collection, please prefer the use of [lodash](https://lodash.com/) to bring about code portability and simplicity.
* Although lodash and lodash-fp is preferred, in many cases, especially on NodeJS, please make use of [AsyncJS](https://github.com/caolan/async) to maintain overall performance on asynchronicity of operations.
* With async/await in NodeJS8, instead of AsyncJS, use `bluebird` library in combination with async/await, unless performance is critical.

###### Dates Development Guideline (JS/Python)
* All dates, be it in the back end or front end, will be read/written in UTC timezone, and should be using [ISO8601](https://en.wikipedia.org/wiki/ISO_8601) format.
    * In the backend, please use either `arrow` or `datetime` (appropriately) to achieve this.
    * In the backend, for timing, use `default_timer` from `timeit` module rather than the `time` module.
    * Please use [moment.js](http://momentjs.com/) to achieve this efficiently on the frontend.
        * For example: ```moment().utc().format()``` will give an [ISO8601](https://en.wikipedia.org/wiki/ISO_8601) time formatted string.
        * For example: ```moment().utc().valueOf()``` will give a proper unix timestamp in milliseconds.
* All dates will be displayed in the user's time zone only when they are *presented* to them. (Always let the browser convert UTC to Local)
    * For Example: ```moment(dateObjInUtc).format()``` will give an [ISO8601](https://en.wikipedia.org/wiki/ISO_8601) time formatted string in the user's time zone.

###### Editor
* The preferred IDE of choice for development and compatibility [IntelliJ Ultimate](https://www.jetbrains.com/idea/download/).
* Visual Studio Code also offers nice features with the Vue, Python, NodeJS plugins.

###### Code Linting (JS)
* The `.eslintrc` file is used to enforce common javascript settings for code quality purposes, see [ESLint](http://eslint.org/)
  * Configure in IntelliJ in: **Preferences --> Language & Frameworks --> JavaScript --> Code Quality Tools --> ESLint (`Enable` and `Automatic Search`)**

###### Code Assistance (Frontend JS)
* For editors (e.g. webpack) who use webpack as a means to provide code assistance, you can specify the webpack config file location from the following path:
  * `<project_root>/web/public/node_modules/@vue/cli-service/webpack.config.js`

# Production Deployment / Release

>>>
As much as we can hope that defaults for development to be the same as defaults for production, that is simply unachievable for the sake of robustness and security.
Code needs to be cleaned from APL remnants, configuration will vary based on OS and hardware, and lastly measures need to be taken to ensure the survivability of
the system during shutdowns and other potentially unexpected events. Additionally, if deploying on a sponsor site, we need to follow AOS quality standards. 
>>>
