import {Component, Inject} from '@angular/core';
import {Crud} from '../crud/crud';
import {MatButton} from '@angular/material/button';
import {MatDialogActions, MatDialogContent, MatDialogTitle} from '@angular/material/dialog';
import {Reports} from '../reports/reports';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {AgentInfo} from '../agent-modal/agent-modal';
import {MatChip, MatChipSet} from '@angular/material/chips';
import {MatDivider} from '@angular/material/divider';

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
    MatDivider
  ],
  templateUrl: './manage-agents-dialog.html',
  styleUrl: './manage-agents-dialog.css',
  standalone: true
})
export class ManageAgentsDialog {
  protected agentsInfo: AgentInfo[];

  constructor(
    private dialogRef: MatDialogRef<ManageAgentsDialog>,
    @Inject(MAT_DIALOG_DATA) public data: AgentInfo[],
  ) {
    this.agentsInfo = data;
  }

  close(): void {
    this.dialogRef.close();
  }

}
