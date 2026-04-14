import {
  MAT_DIALOG_DATA,
  MatDialogActions,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle
} from '@angular/material/dialog';
import {AgentsService} from '../../../../store/modules/agents.service';
import {MatButton} from '@angular/material/button';
import {Component, Inject, inject, OnInit} from '@angular/core';
import {ReportOption, Reports} from '../reports/reports';
import {Crud, Operation} from '../crud/crud';

export interface AgentInfo {
  agent_endpoint_uri: string;
  registered_agents_id: string;
  first_registered: string;
  last_registered: string;
  selected?: boolean;
}

@Component({
  selector: 'app-agent-modal',
  templateUrl: 'agent-modal.html',
  imports: [
    MatDialogContent,
    MatDialogActions,
    MatButton,
    MatDialogTitle,
    Reports,
    Crud,
  ],
  styleUrls: ['agent-modal.css']
})
export class AgentModal implements OnInit {
  protected agentsService = inject(AgentsService);

  protected agentInfo: AgentInfo;

  protected rptt: ReportOption[] = [];
  protected operations: Operation[] = [];

  constructor(
    private dialogRef: MatDialogRef<AgentModal>,
    @Inject(MAT_DIALOG_DATA) public data: AgentInfo,
  ) {
    this.agentInfo = data;
  }

  ngOnInit(): void {
    if (this.agentInfo?.registered_agents_id != null) {
      this.agentsService.setAgentId(this.agentInfo.registered_agents_id);
      this.agentsService.reloadAgent();
    }

    this.rptt = this.agentsService.rptt();
    this.operations = this.agentsService.operations();
  }

  close(): void {
    this.dialogRef.close();
  }
}
