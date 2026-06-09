import { Component } from '@angular/core';
import {MatIcon} from "@angular/material/icon";
import {MatListItemIcon} from "@angular/material/list";
import {RouterLink} from '@angular/router';
import {MatMiniFabButton} from '@angular/material/button';

@Component({
  selector: 'app-dashboard-home',
  imports: [
    MatIcon,
    MatListItemIcon,
    RouterLink,
    MatMiniFabButton
  ],
  templateUrl: './dashboard-home.html',
  styleUrl: './dashboard-home.css',
})
export class DashboardHome {}
