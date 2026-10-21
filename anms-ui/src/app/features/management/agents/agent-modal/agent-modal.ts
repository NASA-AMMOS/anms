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
  standalone: true,
  styleUrls: ['agent-modal.css']
})
export class AgentModal implements OnInit {
  protected agentsService = inject(AgentsService);

  protected agentInfo: AgentInfo;

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
  }

  close(): void {
    this.dialogRef.close();
  }
}
