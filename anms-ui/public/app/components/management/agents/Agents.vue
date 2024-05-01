<template>
  <div>
    <b-row>
      <b-col offset="2"
        cols="8">
        <div class="input-group mb-3">
          <input type="text"
            class="form-control"
            placeholder="Search by ID String, First Registered, or Last Registered"
            v-model="searchString"
            @change="handleSearchStringChange($event)"
            v-on:keyup.enter="handlePageChange(1)" />
          <div class="input-group-append">
            <button class="btn btn-outline-secondary"
              type="button"
              @click="handlePageChange(1)">
              Search
            </button>
          </div>
        </div>
        <b-row>
          <b-col>
            <p>Select Agent to view</p>
          </b-col>
          <b-col><button class="btn btn-outline-success float-right mb-2"
              @click="goToManageModal" :disabled="!selectedAgents.length">Manage</button></b-col>
        </b-row>
        <b-table id="agents-table"
          ref="agentsTable"
          :items="currentAgents"
          :fields="fields"
          :per-page="pageSize"
          @row-clicked="goToAgentDetails"
          primary-key="registered_agents_id"
          hover
          bordered>
          <template #head(selected)="data">
            <div style="text-align: center;">
              <b-form-checkbox v-model="selectAll"
                @change="toggleSelectAll">Select All</b-form-checkbox>
            </div>
          </template>
          <template #cell(selected)="{ item }">
            <div style="text-align: center;">
              <b-form-checkbox :checked="item.selected"
                @change="selectAgent($event, item)"></b-form-checkbox>
            </div>
          </template>
        </b-table>
        <div class="d-flex float-right">
          <div class="my-2 mx-3">
            Items per Page:
            <select v-model="pageSize"
              @change="handlePageSizeChange($event)">
              <option v-for="size in pageSizes"
                :key="size"
                :value="size">
                {{ size }}
              </option>
            </select>
          </div>
          <b-pagination v-model="page"
            class="m-0"
            :total-rows="count"
            :per-page="pageSize"
            aria-controls="agents-table"
            @change="handlePageChange">
          </b-pagination>
        </div>
      </b-col>
    </b-row>
    <label for="node">Address of Agent to add:</label>
    <input name="node"
      v-model="node"
      placeholder="ipn:2.2" />
    <p>Agent address is: {{ node }}</p>
    <button @click="onClick(node.trim())">Add Node</button>
    <pre>{{ resultsAdd }}</pre>
    <p></p>
    <p></p>
    <label for="nodeMan">Address of Agent(s) to manage:</label>
    <input v-b-tooltip.hover
      title="comma separated agent addresses"
      type="string"
      name="nodeMan"
      v-model="nodeMan"
      placeholder="ipn:," />
    <p>Addresses are: [{{ nodeMan }}]</p>

    <!-- have to subtract 1 from the node number since index in nmmanger is 0 based -->
    <b-dropdown id="dropdown-1"
      dropright
      text="Manage agent"
      class="m-md-2">
      <b-dropdown-item-button disabled
        @click="onClickDeregister(nodeMan)">De-register</b-dropdown-item-button>
      <b-dropdown-divider></b-dropdown-divider>

      <b-form-group label="TBR Command:"
        label-for="dropdown-form-tbr"
        @submit.stop.prevent>
        <!-- <b-form-group label="TBR Command:" label-for="dropdown-form-interval" @submit.stop.prevent> -->
        <label for="start">Start(seconds from receipt):</label>
        <input id="dropdown-form-TBRSTART"
          v-model="start"
          type="number"
          placeholder="0" />
        <label for="period">Period(seconds):</label>
        <input type="number"
          id="dropdown-form-TBRPeriod"
          v-model="period"
          placeholder="1" />

        <label for="dropdown-form-TBRCount">Rule Count: </label>
        <input id="dropdown-form-TBRCount"
          v-model="countTBR"
          type="number"
          placeholder="60" />
        <b-form-group>
          <label>Available Reports:</label>
          <select v-model="selected">
            <option disabled
              value="">Which Report?</option>
            <option>ltp_agent.endpointReport</option>
            <option>bp_agent.endpoint_report</option>
            <option>bp_agent.full_report</option>
            <option>amp_agent.full_report</option>
          </select>
        </b-form-group>
        <b-dropdown-item-button @click="onClickSendTBR(nodeMan, start, period, countTBR, selected)">Send Time Based
          Rule</b-dropdown-item-button>
      </b-form-group>
      <b-dropdown-divider></b-dropdown-divider>

      <b-dropdown-form>
        <b-form-group label="RAW Command:"
          label-for="dropdown-form-raw"
          @submit.stop.prevent>
          <b-form-input id="dropdown-form-raw"
            v-model="raw"
            size="sm"
            placeholder="0x0"></b-form-input>
          <b-dropdown-item-button @click="onClickSendRawCommand(nodeMan, raw)">Send Raw Command</b-dropdown-item-button>
        </b-form-group>
      </b-dropdown-form>
      <b-dropdown-divider></b-dropdown-divider>
      <b-dropdown-item-button @click="onClickPrintAgentReports(nodeMan)">Print Agent Reports</b-dropdown-item-button>
      <b-dropdown-item-button disabled
        @click="onClickWriteAgentReportstofile(nodeMan)">Write Agent Reports to file
      </b-dropdown-item-button>
      <b-dropdown-item-button @click="onClickClearAgentReports(nodeMan)">Clear Agent Reports
      </b-dropdown-item-button>
      <b-dropdown-item-button @click="onClickClearAgentTables(nodeMan)">Clear Agent Tables
      </b-dropdown-item-button>
      <b-dropdown-divider></b-dropdown-divider>
    </b-dropdown>
    <label>Last Command Sent: {{ DisplayRaw }}</label>
    <div v-if="loading"
      class="loader">
      <b-spinner variant="info"
        label="Loading..."
        type="grow"></b-spinner>
    </div>
    <div v-if="!loading">

      <pre>{{ results }}</pre>
    </div>

    <agent-modal @close="showAgentModal = false"
      :showModal="showAgentModal"
      :agentInfo="agentInfo"></agent-modal>

    <agents-manage-modal @close="showManageModal = false"
      :showModal="showManageModal"
      :agents="selectedAgents"></agents-manage-modal>

    <footer>
      <p>Amp Version: {{ info }}</p>
    </footer>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";

import api from "../../../shared/api.js";

import AgentModal from "./AgentModal.vue";
import AgentsManageModal from "./AgentsManageModal.vue";

export default {
  name: "Agents",
  components: {
    AgentModal,
    AgentsManageModal,
  },
  data() {
    return {
      fields: [
        {
          key: "selected",
          sortable: false,
        },
        {
          key: "agent_id_string",
          sortable: false,
        },
        {
          key: "first_registered",
          sortable: false,
        },
        {
          key: "last_registered",
          sortable: false,
        },
      ],
      nodeMan: null,
      node: null,
      info: null,
      results: "",
      resultsAdd: "",
      data1: { data: "" },
      raw: "",
      loading: true,
      errored: false,
      pageSizes: [5, 10, 20, 50, 100],
      tbrRaw: ``,
      DisplayRaw: "",
      start: 0,
      tbrCount: 0x01,
      countTBR: 60,
      period: 1,
      nodes: "",
      selected: null,
      showAgentModal: false,
      showManageModal: false,
      agentInfo: null,
      selectAll: false,
    };
  },
  props: {
    cbor: String
  },
  mounted() {
    const vm = this;
    vm.reloadAgents();
    this.raw = this.cbor
    api.methods
      .apiAmpVersion()
      .then((response) => {
        vm.info = response.data.amp_version_str;
      })
      .catch(function (error) {
        // handle error
        console.error(error);
        this.info = "failed to reach manager";
      });
  },
  computed: {
    ...mapGetters("agents", {
      currentAgents: "currentAgents",
      count: "count",
      page: "page",
      pageSize: "pageSize",
      searchString: "searchString",
    }),
    selectedAgents() {
      return this.currentAgents.filter((agent) => {
        return agent.selected == true;
      });
    },
  },
  methods: {
    ...mapActions("agents", {
      reloadAgents: "reloadAgents",
      setPage: "setPage",
      setPageSize: "setPageSize",
      setSearchString: "setSearchString",
      updateAgent: "updateAgent",
    }),
    goToAgentDetails(event) {
      this.agentInfo = event;
      this.showAgentModal = true;
    },
    goToManageModal() {
      this.showManageModal = true;
    },
    handlePageChange(value) {
      const vm = this;
      vm.setPage(value);
      vm.reloadAgents();
    },
    handlePageSizeChange(event) {
      const vm = this;
      vm.setPageSize(event.target.value);
      vm.setPage(1);
      vm.reloadAgents();
    },
    handleSearchStringChange(event) {
      const vm = this;
      vm.setSearchString(event.target.value);
    },
    onClick(nodes) {
      let nodeList = nodes.split(",");
      nodeList.forEach((node) => {
        api.methods
          .apiPostAgent(node.trim())
          .then((response) => (this.results = response.status + " " + response.statusText))
          .catch((error) => {
            console.error(error);
            this.errored = true;
            // this.resultsAdd = "error adding node (check address)"
          })
          .finally(() => (this.loading = false));
      });
    },

    onClickSendRawCommand: async function (nodes, raw) {
      let nodeList = nodes.split(",");
      this.DisplayRaw = raw;
      await nodeList.forEach(async (node) => {
        await api.methods
          .apiSendRawCommand(node.trim(), raw)
          .then((response) => {
            this.results = response.data + " " + response.statusText
            this.loading = false
          })
          .catch((error) => {
            console.error(error);
            this.errored = true;
            this.results = "error sending request to node! (check node index) " + error.message;
            this.loading = false
          })
          .finally(() => (this.loading = false));
      });
    },

    onClickPrintAgentReports(nodes) {
      let nodeList = nodes.split(",");
      this.results = []
      nodeList.forEach((node) => {
        api.methods
          .apiPrintAgentReports(node.trim())
          .then((response) => (this.results.push(response.data)))
          .catch((error) => {
            console.error(error);
            this.errored = true;
            this.results = "error sending request to node! (check node index) " + error.message;
          })
          .finally(() => (this.loading = false));
      });
    },

    onClickWriteAgentReportstofile(nodes) {
      let nodeList = nodes.split(",");
      nodeList.forEach((node) => {
        api.methods
          .apiWriteAgentReportstofile(node.trim())
          .then((response) => (this.results = response.status + " " + response.statusText))
          .catch((error) => {
            console.error(error);
            this.errored = true;
            this.results = "error sending request to node! (check node index) " + error.message;
          })
          .finally(() => (this.loading = false));
      });
    },

    onClickClearAgentReports(nodes) {
      let nodeList = nodes.split(",");
      nodeList.forEach((node) => {
        api.methods
          .apiClearAgentReports(node.trim())
          .then((response) => (this.results = response.statusText + " reports cleared"))
          .catch((error) => {
            console.error(error);
            this.errored = true;
            this.results = "error sending request to node! (check node index) " + error.message;
          })
          .finally(() => (this.loading = false));
      });
    },

    onClickClearAgentTables(nodes) {
      let nodeList = nodes.split(",");
      this.DisplayRaw = "clear tables for " + nodes;
      nodeList.forEach((node) => {
        api.methods.apiClearAgentTables(node.trim())
          .then((response) => (this.results = response.statusText + " tables cleared"))
          .catch((error) => {
            console.error(error);
            this.errored = true;
            this.results = "error sending request to node! (check node index) " + error.message;
          })
          .finally(() => (this.loading = false));
      });
    },

    onClickSendTBR: function (nodes, start, period, count, report) {
      if (nodes != null) {
        let nodeList = nodes.split(",");
        nodeList.forEach((node) => {
          this.loading = true
          const res = api.methods.apiSendTBR(
            node.trim(),
            start,
            period,
            count,
            report,
            this.tbrCount
          );

          // localStorage.tbrCount = this.tbrCount;

          let prom = res[0];

          prom.then((response) => {
            this.loading = false
            this.results = response.status + " " + response.statusText
          })
            .catch((error) => {
              console.error(error);
              this.errored = true;
              this.results = "error sending request to node! (check node index) " + error.message;
            })
            .finally(() => (this.loading = false));
          this.DisplayRaw = res[1];
          this.loading = false
        });
      } else {
        this.loading = false;
        this.results = "error sending request to node! Missing Address of agent"
      }
      this.tbrCount = this.tbrCount + 0x01;
    },
    getAgentIndexById(agentId) {
      return this.currentAgents.findIndex(agent => agent.registered_agents_id === agentId);
    },
    selectAgent(event, agent) {
      if (agent && event != agent.selected) {
        let agentUpdated = { ...agent };
        let agentIndex = this.getAgentIndexById(agentUpdated.registered_agents_id);
        agentUpdated.selected = event;
        this.updateAgent({ agentIndex, agent: agentUpdated });
      }
    },
    toggleSelectAll() {
      this.currentAgents.forEach((agent) => { this.selectAgent(this.selectAll, agent) });
    },
  },
};
</script>

<style>
.table-hover tbody tr:hover {
  cursor: pointer;
}
</style>
