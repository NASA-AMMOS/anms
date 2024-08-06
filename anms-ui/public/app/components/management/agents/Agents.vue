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
              @click="goToManageModal"
              :disabled="!selectedAgents.length">Manage</button></b-col>
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
        <b-row>
          <b-col>
            <b-input-group prepend="Agent Address">
              <b-form-input v-model="node"></b-form-input>
              <b-input-group-append>
                <b-button variant="outline-success"
                  @click="onClick(node.trim())">Add</b-button>
              </b-input-group-append>
            </b-input-group>
          </b-col>
          <b-col>
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
      </b-col>
    </b-row>

    <agent-modal @close="showAgentModal = false"
      :showModal="showAgentModal"
      :agentInfo="agentInfo"></agent-modal>

    <agents-manage-modal @close="showManageModal = false"
      :showModal="showManageModal"
      :agents="selectedAgents"
      :cbor="cbor"></agents-manage-modal>

    <footer class="footer">
      <p><a :href="info.split(' - ')[1]" target="_blank">Amp Version: {{ info.split(" - ")[0] }}</a></p>
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
      node: null,
      info: null,
      results: "",
      pageSizes: [10, 20, 50, 100],
      nodes: "",
      selected: null,
      showAgentModal: false,
      showManageModal: false,
      agentInfo: null,
      selectAll: false,
    };
  },
  props: {
    cbor: {
      type: String,
      default: undefined
    }
  },
  mounted() {
    const vm = this;
    vm.reloadAgents();
    api.methods
      .apiAmpVersion()
      .then((response) => {
        vm.info = response.data.amp_version_str;
      })
      .catch(function (error) {
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
          });
      });
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

.footer {
  position: fixed;
  bottom: 0;
}
</style>
