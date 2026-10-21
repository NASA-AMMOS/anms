/*
 * Copyright (c) 2026 The Johns Hopkins University Applied Physics
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
import { Routes } from '@angular/router';
import {Dashboard} from './features/dashboard/dashboard';
import {Help} from './features/help/help';
import {DashboardHome} from './features/dashboard/components/dashboard-home/dashboard-home';
import {Monitor} from './features/management/monitor/monitor';
import {Agents} from './features/management/agents/agents';
import {Builder} from './features/management/builder/builder';
import {Status} from './features/status/status';
import {Adms} from './features/adms/adms';
import {PageNotFound} from './features/page-not-found/page-not-found';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  {
    path: 'dashboard',
    component: Dashboard,
    children: [
      {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full'
      },
      {
        path: 'home',
        component: DashboardHome
      },
      {
        path: 'monitor',
        component: Monitor
      },
      {
        path: 'agents',
        component: Agents
      },
      {
        path: 'builder',
        component: Builder
      },
      {
        path: 'status',
        component: Status
      },
      {
        path: 'adms',
        component: Adms
      },
      {
        path: 'help',
        component: Help,
      },
    ]

  },
  { path: '**', component: PageNotFound }
];
