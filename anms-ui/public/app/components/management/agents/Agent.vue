<template>
  <div>
    <h1>Agent Details:</h1>
    <div>Registered Agents ID = {{ agentId }}</div>
    <div>Agent ID String: {{ currentAgent.agent_id_string }}</div>
    <div>First Registered: {{ currentAgent.first_registered }}</div>
    <div>Last Registered: {{ currentAgent.last_registered }}</div>
    
    <div>
    <reports 
    :agentName="currentAgent.agent_id_string"
    :rptts="rptt" />
    
    <crud
      :agentId="agentId" :Operations="operations">
    </crud>
  </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import Crud from './crud.vue';
import reports from './reports.vue';

export default {
  name: "Agents",
  components: {
    reports,
    Crud
  },
  data() {
    return {
      currADM: "",
      currReport: "",
      reportOptions: "",
      selected: {},
      rptList:{}

    }
  },
  props: {
    agentId: Number
  },

  mounted() {
    const vm = this;
    vm.setAgentId(vm.agentId);
    vm.reloadAgent();
    console.log(vm.currentAgent)
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
    })
  }
}
</script>

<style scoped>

</style>
