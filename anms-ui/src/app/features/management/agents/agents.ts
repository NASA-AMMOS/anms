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
import {AgentsService} from '../../../store/modules/agents.service';
import {ApiService} from '../../../shared/api.service';
import {NotificationService } from '../../../shared/notification.service';
import {FormsModule} from '@angular/forms';
import {MatPaginator, PageEvent} from '@angular/material/paginator';
import {MatDialog} from '@angular/material/dialog';
import { MatTableModule} from '@angular/material/table';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatPaginatorModule } from '@angular/material/paginator';
import {AgentInfo, AgentModal} from './agent-modal/agent-modal';
import {SelectionModel} from '@angular/cdk/collections';
import {ManageAgentsDialog} from './manage-agents-dialog/manage-agents-dialog';
import {CommandHandoffService} from '../../../shared/command-handoff.service';

@Component({
  selector: 'app-agents',
  standalone: true,
  imports: [
    FormsModule,
    MatPaginator,
    MatTableModule,
    MatCheckboxModule,
    MatPaginatorModule
  ],
  templateUrl: './agents.html',
  styleUrl: './agents.css',
})
export class Agents implements AfterViewInit {
  protected agentsService = inject(AgentsService);
  protected apiService = inject(ApiService);
  protected notificationService = inject(NotificationService);
  protected dialog = inject(MatDialog);
  private commandHandoffService = inject(CommandHandoffService);

  protected info: string = '';
  protected node: any;
  protected pageSizes = [10, 20, 50, 100];
  protected selection = new SelectionModel<any>(true, []); // true = multi-select


  ngAfterViewInit(): void {
    this.agentsService.reloadAgents();
    this.apiService.apiAmpVersion().subscribe(
      {
        next: (response: any) => {
          if (response.amp_version != null) {
            this.info = response.amp_version + ", " + response.ari_version;
          }
        },
        error: (err: any) => {
          console.error(err);
          this.notificationService.error("failed to reach manager");
        }
      });
  }

  protected handleSearchStringChange($event: any) {
    this.agentsService.setSearchString($event.target.value);
  }

  protected handlePageEvent(pageEvent: PageEvent, paginator: MatPaginator) {
    if(this.agentsService.getPageSize() !== pageEvent.pageSize) {
      this.agentsService.setPageSize(pageEvent.pageSize);
      this.agentsService.setPage(1);
      paginator.firstPage()
    } else {
      this.agentsService.setPage(pageEvent.pageIndex + 1);
    }

    this.agentsService.reloadAgents();
  }


  protected toggleAgent(agent: any) {
    this.selection.toggle(agent);
  }

  protected isAllSelected() {
    return this.selection.selected.length === this.agentsService.currentAgents().length;
  }

  protected toggleAll() {
    if (this.isAllSelected()) {
      this.selection.clear();
    } else {
      this.selection.select(...this.agentsService.currentAgents());
    }
  }

  protected onClick(nodes: string) {
    let nodeList = nodes.split(",");
    nodeList.forEach((node) => {
      this.apiService
        .apiPostAgent(node.trim())
        .subscribe({next: (_) => {
          this.notificationService.success(`Agent added to node: ${node}`);
        },
          error: (err: any) => {
            console.error(err);
            this.notificationService.error("Failed to add agent to node: "+node);
          }
        });
    });
  }


  protected goToAgentDetails(agentInfo: AgentInfo) {
    const dialogRef = this.dialog.open(AgentModal, {
      width: '80vw',
      maxWidth: '1000px',
      data: agentInfo
    });
  }

  protected goToManageDialog() {
    const selectedAgents: AgentInfo[] = this.selection.selected;
    const dialogRef = this.dialog.open(ManageAgentsDialog, {
      width: '80vw',
      maxWidth: '1000px',
      data: {
        agents: selectedAgents,
        cborCommands: this.commandHandoffService.cborCommands(),
      },
      panelClass: 'custom-dialog'
    });

  }

  onAgentRowKeydown(event: KeyboardEvent, agent: AgentInfo): void {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      this.goToAgentDetails(agent);
    }
  }
}
