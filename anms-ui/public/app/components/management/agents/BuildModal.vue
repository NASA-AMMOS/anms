<template>
  <div>
    <b-modal id="buildModal"
      ref="buildModal"
      size="xl"
      ok-only
      @hide="closeModal"
      title="Build">
      <div v-if="agents">
        <h3>Managed Agents:</h3>
        <ul>
          <li v-for="agent in agents">{{ agent.agent_id_string }}</li>
        </ul>
      </div>
    </b-modal>
  </div>
</template>
<script>
import { mapActions, mapGetters } from "vuex";
export default {
  name: "BuildModal",
  components: {},
  data() {
    return {}
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
    }
  },
}
</script>
<style scoped>
</style>
