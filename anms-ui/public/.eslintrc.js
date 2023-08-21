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
  root: true,
  env: {
    es6: true,
    node: true,
    browser: true
  },
  globals: {
    'Constants': 'readonly'
  },
  'extends': [
    'plugin:lodash/canonical',
    'plugin:vue/recommended',
    '@vue/standard'
  ],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'indent': ['error', 2, {'SwitchCase': 1}],
    'linebreak-style': 0,
    'eol-last': 2,
    'quotes': [2, 'single'],
    'semi': [2, 'always'],
    'eqeqeq': [2, 'smart'],
    'padded-blocks': 'off',
    'no-use-before-define': [2, 'nofunc'],
    'no-unused-vars': ['warn', {'vars': 'local', 'args': 'none'}],
    'no-multi-str': 2,
    'no-irregular-whitespace': 2,
    'object-curly-spacing': 'off',
    'space-before-function-paren': ['error', {anonymous: 'ignore', named: 'never', asyncArrow: 'always'}],
    'lodash/prefer-lodash-method': ['warn'],
    'vue/html-self-closing': ['warn', {html: {void: 'always', normal: 'any'}}],
    'vue/script-indent': ['warn', 2, {'switchCase': 1, 'baseIndent': 1}],
    'vue/singleline-html-element-content-newline': 'off',
    'vue/max-attributes-per-line': 'off',
    'vue/html-closing-bracket-newline': ['error', {singleline: 'never', multiline: 'never'}],
    'vue/html-closing-bracket-spacing': ['error', {selfClosingTag: 'never'}],
    'vue/multiline-html-element-content-newline': ['error', {ignoreWhenEmpty: true, allowEmptyLines: true}]
  },
  overrides: [
    {
      files: ['*.vue'],
      rules: {
        indent: 'off'
      }
    }
  ],
  parserOptions: {
    parser: 'babel-eslint'
  }
};
