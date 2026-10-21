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
import {Component, inject, OnInit} from '@angular/core';
import {KeyValuePipe} from '@angular/common';
import {Utils} from '../../shared/utils';
import {ServiceStatusService} from '../../store/modules/service-status.service';

@Component({
  selector: 'app-status',
  imports: [
    KeyValuePipe
  ],
  templateUrl: './status.html',
  styleUrl: './status.css',
})
export class Status implements OnInit {

  protected serviceStatus = inject(ServiceStatusService);
  protected utils = inject(Utils);

  ngOnInit(): void {
    this.updateServiceStatus();
  }

  protected updateServiceStatus() {
    this.serviceStatus.updateStatus();
  }

}
