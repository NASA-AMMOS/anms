import {Component, Inject} from '@angular/core';
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

@Component({
  selector: 'app-manage-agents-dialog',
  imports: [
    Crud,
    MatButton,
    MatDialogActions,
    MatDialogContent,
    MatDialogTitle,
    Reports,
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
    MatLabel
  ],
  templateUrl: './manage-agents-dialog.html',
  styleUrl: './manage-agents-dialog.css',
  standalone: true
})
export class ManageAgentsDialog {
  protected agentsInfo: AgentInfo[];

  protected ariMode: 'builder' | 'text' = 'builder';
  protected executionSet = false;

  protected selectedAriText = '';
  protected hexInput = '';
  protected ariText = '';

  constructor(
    private dialogRef: MatDialogRef<ManageAgentsDialog>,
    @Inject(MAT_DIALOG_DATA) public data: AgentInfo[],
  ) {
    this.agentsInfo = data;
  }

  close(): void {
    this.dialogRef.close();
  }

  protected submitTextInput(): void {
    this.ariText = `0x${this.hexInput}`;
  }

}
