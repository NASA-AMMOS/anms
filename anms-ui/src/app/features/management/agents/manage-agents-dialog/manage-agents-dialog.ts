import {Component, inject, Inject, OnInit} from '@angular/core';
import { ApiService } from '../../../../shared/api.service';
import {MatDialogContent, MatDialogTitle} from '@angular/material/dialog';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {AgentInfo} from '../agent-modal/agent-modal';
import {MatChip, MatChipSet} from '@angular/material/chips';
import {MatDivider} from '@angular/material/divider';
import {Ari} from '../model/ari.model';
import {NotificationService} from '../../../../shared/notification.service';
import {forkJoin, switchMap} from 'rxjs';
import {AriCommandBuilder, AriCommandOutput} from '../../shared/ari-command-builder/ari-command-builder';

interface ManageAgentsDialogData {
  agents: AgentInfo[];
  cborCommands?: string[];
}

@Component({
  selector: 'app-manage-agents-dialog',
  imports: [
    MatDialogContent,
    MatDialogTitle,
    MatChipSet,
    MatChip,
    MatDivider,
    AriCommandBuilder
  ],
  templateUrl: './manage-agents-dialog.html',
  styleUrl: './manage-agents-dialog.css',
  standalone: true
})

export class ManageAgentsDialog implements OnInit {
  protected notificationService = inject(NotificationService);
  protected agentsInfo: AgentInfo[];

  protected aris: Ari[] = [];
  protected filteredAris: Ari[] = [];

  constructor(
    private dialogRef: MatDialogRef<ManageAgentsDialog>,
    @Inject(MAT_DIALOG_DATA) public data: ManageAgentsDialogData,
    private api: ApiService,
  ) {
    this.agentsInfo = data.agents;
  }

  ngOnInit(): void {
    this.api.apiQueryForARIs().subscribe({
      next: (data: Ari[]) => {
        this.aris = data;
        this.filteredAris = data;
      },
      error: (err) => this.notificationService.error('Failed to load ARIs',err),
    });
  }

  close(): void {
    this.dialogRef.close();
  }

  protected handleCommand(command: AriCommandOutput): void {
    if (!this.data.agents.length) {
      this.notificationService.error('No agents selected');
      return;
    }

    const value = command.value.trim();

    if (!value) {
      this.notificationService.error('No command value to send');
      return;
    }

    if (command.mode === 'cbor') {
      this.sendRawCbor(value);
      return;
    }

    this.transcodeThenSend(value);
  }

  private transcodeThenSend(ariText: string): void {
    this.api.apiPutTranscodedString(ariText).pipe(
      switchMap((transcodeResponse) =>
        this.api.apiGetTranscoderLogById(`${transcodeResponse.id}`)
      ),
      switchMap((logResponse) => {
        const cbor = logResponse.cbor;

        if (!cbor) {
          throw new Error('Transcoder log did not include CBOR');
        }

        return this.sendRawCborRequest([cbor]);
      }),
    ).subscribe({
      next: () => {
        this.notificationService.success('ARI sent to selected agents');
        this.dialogRef.close({ updated: true });
      },
      error: (err) => {
        this.notificationService.error(err, 'Error sending ARI');
      },
    });
  }

  private sendRawCbor(cborHex: string): void {
    if (!cborHex?.trim()) {
      this.notificationService.error('No CBOR hex to send');
      return;
    }

    const cborCommands = cborHex
      .split(',')
      .map((value) => value.trim())
      .filter((value) => value.length > 0);

    if (cborCommands.length === 0) {
      this.notificationService.error('No valid CBOR commands found');
      return;
    }

    this.sendRawCborRequest(cborCommands).subscribe({
      next: () =>
        this.notificationService.success(
          `${cborCommands.length} CBOR command(s) sent to ${this.agentsInfo.length} agent(s)`
        ),

      error: (err) =>
        this.notificationService.error(err, 'Error sending CBOR'),
    });
  }

  private sendRawCborRequest(cborCommands: string[]) {
    const requests = this.agentsInfo.flatMap((agent) =>
      cborCommands.map((cbor) =>
        this.api.apiSendRawCommand(
          agent.agent_endpoint_uri,
          cbor
        )
      )
    );

    return forkJoin(requests);
  }
}
