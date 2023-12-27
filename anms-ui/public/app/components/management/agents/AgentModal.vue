<template>
  <div>
    <b-modal id="agentModal"
      ref="agentModal"
      size="xl"
      ok-only
      @hide="closeModal"
      title="'Agent Details:' agentInfo.agent_id_string">
      <div v-if="agentInfo">
        <div>Registered Agents ID = {{ agentInfo.registered_agents_id }}</div>
        <div>First Registered: {{ agentInfo.first_registered }}</div>
        <div>Last Registered: {{ agentInfo.last_registered }}</div>

        <reports :agentName="agentInfo.agent_id_string"
          :rptts="rptt" />

        <crud :agentId="agentInfo.registered_agents_id"
          :Operations="operations">
        </crud>
      </div>
    </b-modal>
  </div>
</template>
<script>
import { mapActions, mapGetters } from "vuex";
import Crud from './crud.vue';
import reports from './reports.vue';
export default {
  name: "AgentModal",
  components: {
    Crud, reports
  },
  data() {
    return {
      currADM: "",
      currReport: "",
      reportOptions: "",
      selected: {},
      rptList: {},
    }
  },
  props: {
    showModal: {
      type: Boolean,
      default: false,
    },
    agentInfo: {
      type: Object,
      default: null,
    }
  },
  watch: {
    showModal(newValue, _) {
      const vm = this;
      vm.setAgentId(vm.agentInfo.registered_agents_id);
      vm.reloadAgent();
      if (newValue === true) {
        this.show();
      }
    }
  },
  computed: {
    ...mapGetters("agents", {
      currentAgent: "currentAgent",
      rptt: "rptt",
      operations: "operations",

    }),
  },
  methods: {
    ...mapActions("agents", {
      reloadAgent: "reloadAgent",
      setAgentId: "setAgentId"
    }),
    show() {
      this.$refs['agentModal'].show();
    },
    closeModal() {
      this.$emit("close");
    }
  },
}
</script>
<style>
</style>
