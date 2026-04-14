import {AfterViewInit, Component, inject} from '@angular/core';
import {AgentsService} from '../../../store/modules/agents.service';
import {ApiService} from '../../../shared/api.service';
import {FormsModule} from '@angular/forms';
import * as toastr from 'toastr';
import {MatPaginator, PageEvent} from '@angular/material/paginator';
import {MatDialog} from '@angular/material/dialog';
import {AgentInfo, AgentModal} from './agent-modal/agent-modal';

@Component({
  selector: 'app-agents',
  imports: [
    FormsModule,
    MatPaginator
  ],
  templateUrl: './agents.html',
  styleUrl: './agents.css',
})
export class Agents implements AfterViewInit {
  protected agentsService = inject(AgentsService);
  protected apiService = inject(ApiService);
  protected dialog = inject(MatDialog);

  protected info: string = '';
  protected selectAll: boolean = false;
  protected node: any;
  protected pageSizes = [10, 20, 50, 100];


  ngAfterViewInit(): void {
    this.agentsService.reloadAgents();
    this.apiService.apiAmpVersion().subscribe(
      {
        next: (response: any) => {
          if (response.build_date != null) {
            this.info = response.build_date + " " + response.build_time;
          }
        },
        error: (err: any) => {
          console.error(err);
          this.info = "failed to reach manager";
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

  protected toggleSelectAll() {
    this.agentsService.currentAgents().forEach((agent) => {
      this.selectAgent(this.selectAll, agent);
    });
  }

  protected selectAgent(event: any, agent: any) {
    if (agent && event != agent.selected) {
      let agentUpdated = {...agent};
      let agentIndex = this.getAgentIndexById(agentUpdated.registered_agents_id);
      agentUpdated.selected = event;
      this.agentsService.updateAgent(agentIndex, agentUpdated);
    }
  }

  protected onClick(nodes: string) {
    let nodeList = nodes.split(",");
    nodeList.forEach((node) => {
      this.apiService
        .apiPostAgent(node.trim())
        .subscribe({next: (response) => {
          const results = response.status + " " + response.statusText;
          toastr.success(results);
        },
          error: (err: any) => {
            console.error(err);
            toastr.error("Failed to add agent to node: " + node);
          }
        });
    });
  }

  protected selectedAgents() {
    return this.agentsService.currentAgents().filter((agent) => {
      return agent.selected == true;
    });
  }

  protected goToAgentDetails(agentInfo: AgentInfo) {
    const dialogRef = this.dialog.open(AgentModal, {
      width: '80vw',
      maxWidth: '1000px',
      data: agentInfo
    });

    dialogRef.afterClosed().subscribe(() => {
    });
  }

  protected goToManageModal() {
    // this.showManageModal = true;
  }

  private getAgentIndexById(agentId: any) {
    return this.agentsService.currentAgents().findIndex(agent => agent.registered_agents_id === agentId);
  }
}
