import {computed, inject, Injectable, signal} from '@angular/core';
import {ApiService} from '../../shared/api.service';
import {first} from 'rxjs';
import {AgentInfo} from '../../features/management/agents/agent-modal/agent-modal';
import {ReportOption} from '../../features/management/agents/reports/reports';

@Injectable({
  providedIn: 'root',
})
export class AgentsService {
  private api = inject(ApiService);

  // --- Signals for state ---
  agents = signal<AgentInfo[]>([]);
  alerts = signal<any[]>([]);
  agent = signal<any>({});
  rptt = signal<ReportOption[]>([]);
  operations = signal<any[]>([]);
  count = signal<number>(0);
  page = signal<number>(1);
  pageSize = signal<number>(10);
  searchString = signal<string>('');
  agentId = signal<string | undefined>(undefined);

  // --- Computed values (getters) ---
  currentAgents = computed(() => this.agents());
  currentAgent = computed(() => this.agent());
  newAgentAlerts = computed(() => this.alerts());
  getRptt = computed(() => this.rptt());
  getOperations = computed(() => this.operations());
  getCount = computed(() => this.count());
  getPage = computed(() => this.page());
  getPageSize = computed(() => this.pageSize());
  getSearchString = computed(() => this.searchString());

  constructor() {}

  // --- Actions ---

  reloadAgents() {
    const params = {
      searchString: this.searchString(),
      page: this.page(),
      size: this.pageSize()
    };

    this.api.apiQueryForAgents(params)
      .pipe(first())
      .subscribe(res => {
        const agents = res.items.map((agent: any) => ({
          ...agent,
          selected: false
        }));
        this.agents.set(agents);
        this.count.set(res.total);
      });
  }

  addAlert(alert: any) {
    this.alerts.update((alerts: any) => alerts.push(alert));
  }

  setPage(page: number) {
    this.page.set(page);
  }

  setPageSize(pageSize: number) {
    this.pageSize.set(pageSize);
  }

  reloadAgent() {

    this.agent.set({});
    const agentId = this.agentId();
    if (!agentId) return;

    this.api.apiGetAgent(agentId).pipe(first()).subscribe(res => {
      const registered_agents_id = res.registered_agents_id;
      this.api.apiEntriesForReportTemplate(registered_agents_id).pipe(first()).subscribe({
        next: rres => {
          this.rptt.set(rres);
        },
        error: err => {
          console.error("get agent rptt error", err);
          this.rptt.set([]);
        }
      });


      this.api.apiEntriesForOperations(registered_agents_id).pipe(first()).subscribe({
        next: ores => this.operations.set(ores),
        error: err => {
          console.error("get agent CRUD operations error", err);
          this.operations.set([]);
        }
      });
      this.agent.set(res);
    });
  }

  setAgentId(agentId: string) {
    this.agentId.set(agentId);
  }

  updateAgent(agentIndex: number, agent: any) {
    this.agents.update((arr: any) => {
      arr[agentIndex] = agent;
      return arr;
    });
  }

  setSearchString(str: string) {
    this.searchString.set(str);
  }

  removeAlert(index: number) {
    this.alerts.update(arr => arr.splice(index, 1));
  }

  // -- Optionally, a way to set all agents at once (like mutation) --
  setAgents(agents: any[]) { this.agents.set(agents); }
  setAgent(agent: any) { this.agent.set(agent); }
  setAlerts(alerts: any[]) { this.alerts.set(alerts); }
  setRptt(rptt: any[]) { this.rptt.set(rptt); }
  setOperations(operations: any[]) { this.operations.set(operations); }
  setCount(count: number) { this.count.set(count); }
  setPageNumber(page: number) { this.page.set(page); }
  setPageSizeNumber(pageSize: number) { this.pageSize.set(pageSize); }
  setSearchStringValue(searchString: string) { this.searchString.set(searchString); }
}
