import {Component, inject, Input} from '@angular/core';
import {ApiService} from '../../../../shared/api.service';
import {ToastrService} from 'ngx-toastr';
import {FormsModule} from '@angular/forms';

export interface Operation {
  command_name: string;
  command_parameters: string[];
  agent_parameter_id: number | string;
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
})
export class Crud {
  @Input() agentId!: number | string;
  @Input() operations: Operation[] = [];
  private apiService = inject(ApiService);
  private toastr = inject(ToastrService)

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

    this.apiService
      .apiPutCRUD(this.agentId, this.selected.agent_parameter_id, this.finalValues)
      .subscribe({
        next: (response: any) => {
          this.toastr.success(`${response.statusText} ${response.data}`);
          this.selected = -1;
          this.params = [];
        }, error: (error: any) => {
          console.error('crud error', error);
          this.toastr.error(error);
        }
      });
  }
}
