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
import Vue from 'vue';
import Router from 'vue-router';
import Home from '@app/components/home/Home.vue';
import About from '@app/components/about/About.vue';
import Constants from '@app/shared/constants';
import User from '@app/components/user/User';
import UserProfile from '@app/components/user/UserProfile';
import UserAdmin from '@app/components/user/UserAdmin';
import Dashboard from "../components/management/monitor/Monitor";
import Agents from "../components/management/agents/Agents";
import build_ari from "../components/management/builder/buildAri";
import Status from "../components/status/Status";
import Adm from "../components/adm/Adm";



Vue.use(Router);

export default new Router({
  mode: 'history',
  base: Constants.BASE_URL,
  linkActiveClass: 'active',
  linkExactActiveClass: 'active',
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/home',
      name: 'home',
      component: Home
    },
    {
      path: '/about',
      name: 'about',
      component: About
    },
    {
      path: '/monitor',
      name: 'Monitor',
      component: Dashboard
    },
    {
      path: '/agents',
      name: 'Agents',
      component: Agents
    },
    {
      path: '/agents/alerts/:alert',
      name: 'sending alerts',
      component: Agents,
      
    },
    {
      path: '/agents/cbor/:cbor',
      name: 'Agents CBOR',
      component: Agents,
      props: true
    },
    {
      path: '/agents/cbors/:cbors',
      name: 'Agents CBORs',
      component: Agents,
      props: true
    },    
    {
      path: '/build',
      name: 'Build ari',
      component: build_ari,
    },
    {
      path: '/status',
      name: 'Status',
      component: Status,
      props: true
    },
    {
      path: '/user',
      name: 'user',
      component: User,
      redirect: {name: 'userProfile'},
      children: [
        {
          path: 'profile',
          name: 'userProfile',
          component: UserProfile
        },
        {
          path: 'admin',
          name: 'userAdministration',
          component: UserAdmin,
          beforeEnter: (to, from, next) => {
            // TODO: validate using permissions instead?
            const allowRoute = _.intersection(Constants.USER_DETAILS.roles, ['ROLE_SUPER_ADMIN', 'ROLE_ADMIN']).length >= 1;
            if (!allowRoute) {
              return next(false); // prevent
            }
            // TODO: should redirect to unauthorized page...
            return next(); // allow
          }
        }
      ]
    },
    {
      path: '/adms',
      name: 'Adms',
      component: Adm,
      props: true
    },
    {
      path: '*',
      redirect: '/'
    }
  ]
});
