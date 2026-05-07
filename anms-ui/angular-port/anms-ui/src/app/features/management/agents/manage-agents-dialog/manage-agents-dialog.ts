import {Component, Inject, OnInit} from '@angular/core';
import { ApiService } from '../../../../shared/api.service';
import {Crud} from '../crud/crud';
import {MatButton} from '@angular/material/button';
import {MatDialogActions, MatDialogContent, MatDialogTitle} from '@angular/material/dialog';
import {Reports} from '../reports/reports';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {AgentInfo} from '../agent-modal/agent-modal';
import {MatChip, MatChipSet} from '@angular/material/chips';
import {MatDivider} from '@angular/material/divider';
import {MatButtonToggle, MatButtonToggleGroup} from '@angular/material/button-toggle';
import {FormsModule} from '@angular/forms';
import {MatFormField, MatPrefix, MatLabel} from '@angular/material/form-field';
import {MatCheckbox} from '@angular/material/checkbox';
import {MatInput} from '@angular/material/input';
import {Ari} from './ari.model';
import {MatAutocomplete, MatAutocompleteTrigger, MatOption} from '@angular/material/autocomplete';

@Component({
  selector: 'app-manage-agents-dialog',
  imports: [
    Crud,
    MatButton,
    MatDialogContent,
    MatDialogTitle,
    MatChipSet,
    MatChip,
    MatDivider,
    MatButtonToggleGroup,
    MatButtonToggle,
    FormsModule,
    MatFormField,
    MatCheckbox,
    MatInput,
    MatPrefix,
    MatLabel,
    MatAutocompleteTrigger,
    MatAutocomplete,
    MatOption
  ],
  templateUrl: './manage-agents-dialog.html',
  styleUrl: './manage-agents-dialog.css',
  standalone: true
})
export class ManageAgentsDialog implements OnInit {
  protected agentsInfo: AgentInfo[];

  protected ariMode: 'builder' | 'text' = 'builder';
  protected executionSet = false;

  protected selectedAriText = '';
  protected hexInput = '';
  protected ariText = '';

  protected aris: Ari[] = [];
  protected filteredAris: Ari[] = [];
  protected ariSearchText = '';

  protected selectedAri: Ari | null = null;
  protected ariParams: {
    name: string;
    type: string;
    selectedAri: Ari | null;
    searchText: string;
    filteredAris: Ari[];
  }[] = [];


  constructor(
    private dialogRef: MatDialogRef<ManageAgentsDialog>,
    @Inject(MAT_DIALOG_DATA) public data: AgentInfo[],
    private api: ApiService,
  ) {
    this.agentsInfo = data;
  }

  ngOnInit(): void {
    this.api.apiQueryForARIs().subscribe({
      next: (data: Ari[]) => {
        this.aris = data;
        this.filteredAris = data;
      },
      error: (err) => console.error('Failed to load ARIs', err),
    });
  }

  close(): void {
    this.dialogRef.close();
  }

  protected submitTextInput(): void {
    this.ariText = `0x${this.hexInput}`;
  }

  protected filterAris(value: string | Ari | null): void {
    const search =
      typeof value === 'string'
        ? value.toLowerCase()
        : this.displayAri(value).toLowerCase();

    this.filteredAris = this.aris.filter(ari =>
      ari.display.toLowerCase().includes(search)
    );
  }

  protected onAriSelected(ari: Ari): void {
    this.selectedAri = ari;

    this.ariParams = (ari.param_names ?? []).map((paramName, index) => ({
      name: paramName,
      type: ari.param_types?.[index] ?? '',
      selectedAri: null,
      searchText: '',
      filteredAris: this.aris,
    }));

    this.updateAriText();
  }

  protected onParamAriSelected(paramIndex: number, ari: Ari): void {
    this.ariParams[paramIndex].selectedAri = ari;
    this.updateAriText();
  }

  protected updateAriText(): void {
    if (!this.selectedAri) {
      this.ariText = '';
      return;
    }

    if (this.ariParams.length === 0) {
      this.ariText = this.selectedAri.display;
      return;
    }

    const paramTexts = this.ariParams.map(param =>
      param.selectedAri ? param.selectedAri.display : `<${param.name}>`
    );

    this.ariText = `${this.selectedAri.display}(${paramTexts.join(', ')})`;
  }

  protected displayAri = (ari: Ari | null): string => {
    return ari?.display ?? '';
  };

  protected filterParamAris(paramIndex: number): void {
    const param = this.ariParams[paramIndex];
    const search = param.searchText.toLowerCase();

    param.filteredAris = this.aris.filter(ari =>
      ari.display?.toLowerCase().includes(search)
    );
  }

}
