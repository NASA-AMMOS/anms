<template>
  <div>
    <b-modal id="buildModal"
      ref="buildModal"
      size="xl"
      @hide="closeModal"
      title="Manage Agents"
      hide-footer
      scrollable>
      <div v-if="agents">
        <b-row>
          <b-col cols="3">
            <div class="agent-info">
              <div v-for="agent in agents">
                <b-badge pill
                  variant="primary"> {{ agent.agent_id_string }} </b-badge>
              </div>
            </div>
          </b-col>
          <b-col cols="9">
            <build></build>

                <!-- <label>Available Reports:</label>
                    <select v-model="selected">
                      <option disabled
                        value="">Which Report?</option>
                      <option>ltp_agent.endpointReport</option>
                      <option>bp_agent.endpoint_report</option>
                      <option>bp_agent.full_report</option>
                      <option>amp_agent.full_report</option>
                    </select>
                  </b-form-group>
                  <b-dropdown-item-button @click="onClickSendTBR(nodeMan, start, period, countTBR, selected)">Send Time
                    Based
                    Rule</b-dropdown-item-button>
                </b-form-group> -->
          </b-col>
        </b-row>
      </div>
    </b-modal>
  </div>
</template>
<script>
import { mapActions, mapGetters } from "vuex";
import api from "../../../shared/api.js";
import Build from "../builder/Build.vue";
export default {
  name: "AgentsManageModal",
  components: { Build },
  data() {
    return {
      startTime: null,
      period: null,
      reportCount: null,
      raw: null,
    }
  },
  props: {
    showModal: {
      type: Boolean,
      default: false,
    },
    agents: {
      type: Array,
      default: [],
    },
  },
  watch: {
    showModal(newValue, _) {
      const vm = this;
      if (newValue === true) {
        this.show();
      }
    }
  },
  computed: {},
  methods: {
    show() {
      this.$refs['buildModal'].show();
    },
    closeModal() {
      this.$emit("close");
    },
    sendTBR() {
      this.agents.forEach((agent) => {
        const response = api.methods.apiSendTBR(agent.agent_id_string, this.startTime, this.period, this.reportCount, null,)
      });
    },
    sendRawCommand() {

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
  },
}
</script>
<style scoped>
.agent-info {
  padding: 16px;
  margin-bottom: 16px;
  background-color: grey;
  display: inline-block;
  border-radius: 10px;
  color: black;
  width: 100%;
}

.button-form-center {
  text-align: center;

}
</style>
