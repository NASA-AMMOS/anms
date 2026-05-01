import {AfterViewInit, Component, inject} from '@angular/core';
import {MatDivider, MatListItem, MatListItemIcon, MatNavList} from "@angular/material/list";
import {MatIcon} from "@angular/material/icon";
import {MatTooltip} from '@angular/material/tooltip';
import {NgClass} from '@angular/common';
import {RouterLink} from '@angular/router';
import {RoutesEnum} from '../../shared/routes.enum';
import {DataShareService} from '../../shared/data-share.service';
import {ServiceStatusService} from '../../store/modules/service-status.service';

@Component({
  selector: 'app-sidebar',
  imports: [
    MatDivider,
    MatIcon,
    MatListItem,
    MatListItemIcon,
    MatNavList,
    MatTooltip,
    NgClass,
    RouterLink,
  ],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css',
})
export class Sidebar implements AfterViewInit {
  protected showNavTitle = false;
  protected readonly RoutesEnum = RoutesEnum;
  protected readonly dataShareService = inject(DataShareService);
  protected readonly serviceStatus = inject(ServiceStatusService);

  protected managementDetails: any;

  ngAfterViewInit(): void {
    this.managementDetails = document.getElementById('managementDetails');
    this.managementDetails.open = false;
  }

  protected toggleManagementDetails() {
    this.managementDetails.open = !this.managementDetails.open;
    if(this.managementDetails.open) {
      this.showNavTitle = true;
    }
  }
}
