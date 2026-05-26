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
