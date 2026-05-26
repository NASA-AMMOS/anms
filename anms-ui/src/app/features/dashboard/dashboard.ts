import {AfterViewInit, Component, inject, OnDestroy, OnInit} from '@angular/core';
import {Header} from '../../layout/header/header';
import {MatDivider} from '@angular/material/list';
import {Sidebar} from '../../layout/sidebar/sidebar';
import {RouterOutlet} from '@angular/router';
import {Breadcrumb} from '../breadcrumb/breadcrumb';
import {Constants} from '../../shared/constants';
import {ServiceStatusService} from '../../store/modules/service-status.service';

@Component({
  selector: 'app-dashboard',
  imports: [
    Header,
    MatDivider,
    Sidebar,
    RouterOutlet,
    Breadcrumb
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements AfterViewInit, OnDestroy {
  private serviceStatus = inject(ServiceStatusService);

  private statusWorkerId: number = -1;

  ngAfterViewInit(): void {
    this.statusWorkerId = setInterval(() => {
      this.serviceStatus.updateStatus();
    }, Constants.status_refresh_rate);
  }

  ngOnDestroy(): void {
    if(this.statusWorkerId !== -1) {
      clearInterval(this.statusWorkerId);
    }
  }
}
