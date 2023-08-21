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
module.exports = {
  'root': true,
  'parserOptions': {
    'ecmaVersion': 2018, // node 8~, 10+
    'sourceType': 'module',
    'ecmaFeatures': {
      'impliedStrict': true
    }
  },
  'env': {
    'node': true,
    'es6': true
  },
  'extends': ['eslint:recommended', 'plugin:node/recommended'],
  'rules': {
    'indent': ['error', 2, {'SwitchCase': 1, 'ArrayExpression': 'first'}],
    'linebreak-style': 0,
    'eol-last': 2,
    'quotes': [2, 'single'],
    'semi': [2, 'always'],
    'eqeqeq': [2, 'smart'],
    'no-use-before-define': [2, 'nofunc'],
    'no-unused-vars': ['warn', {'vars': 'local', 'args': 'none'}],
    'no-multi-str': 2,
    'no-irregular-whitespace': 2,
    'space-before-function-paren': ['error', {anonymous: 'ignore', named: 'never', asyncArrow: 'always'}]
  }
};
