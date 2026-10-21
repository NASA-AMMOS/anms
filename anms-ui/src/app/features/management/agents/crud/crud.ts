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
import {Component, inject, Input} from '@angular/core';
import {ApiService} from '../../../../shared/api.service';
import {ToastrService} from 'ngx-toastr';
import {FormsModule} from '@angular/forms';

export interface Operation {
  command_name: string;
  command_parameters: string[];
  // any other fields you may have
}

interface ParamModel {
  name: string;
  value: string;
}

@Component({
  selector: 'app-crud',
  imports: [
    FormsModule
  ],
  templateUrl: './crud.html',
  styleUrl: './crud.css',
  standalone: true
})
export class Crud {
  @Input() agentId!: number | string;
  @Input() operations: Operation[] = [];
  private apiService = inject(ApiService);
  private toastr = inject(ToastrService) // FIXME update to notificationService

  selected: Operation | -1 = -1;
  params: ParamModel[] = [];
  finalValues: Record<string, string> = {};

  onOperationChange(): void {
    // Clear existing params
    this.params = [];

    if (this.selected === -1 || !this.selected) {
      return;
    }

    const commandParameters = this.selected.command_parameters || [];
    commandParameters.forEach((value) => {
      this.params.push({name: value, value: ''});
    });
  }

  onClick(): void {
    if (this.selected === -1 || !this.selected) {
      this.toastr.warning('Please select an operation first.');
      return;
    }

    this.finalValues = {};
    this.params.forEach((param) => {
      this.finalValues[param.name] = param.value;
    });
  }
}
