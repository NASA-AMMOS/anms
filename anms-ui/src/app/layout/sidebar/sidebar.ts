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
  standalone: true
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

  onManagementSummaryKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();        // avoid scrolling on Space
      this.showNavTitle = true;
    }
  }
}
