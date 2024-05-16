<template>
  <div>
    <h5>ARI Builder</h5>
    <v-select v-model="ariKey"
      label="display"
      :options="ARIs"></v-select>

    <ParameterView v-if="ariKey"
      :ariKey="ariKey"
      :ACs="ARIs"
      @updateResult="updateResults($event)"></ParameterView>
  </div>
</template>
<script>
import { mapGetters } from "vuex";
import vSelect from "vue-select";
import ParameterView from "./ParameterView.vue";

export default {
  name: "Build",
  components: {
    vSelect,
    ParameterView,
  },
  props: {},
  data() {
    return {
      ariKey: undefined,
      parameters: undefined,
      finResultStr: undefined,
    }
  },
  computed: {
    ...mapGetters("build", {
      ARIs: "ARIs",
    })
  },
  methods: {
    updateResults: function (result) {
      let head = result[0].value.includes("ari") ? "" : "ari:/";
      this.finResultStr = head + result[0].value;
      this.$emit("updateResult", this.finResultStr);
    },
  }
}
</script>
<style scoped>
> > > {
  --vs-dropdown-bg: #32383e;
  --vs-search-input-color: #52575c;
  --vs-dropdown-option--active-bg: #62c462;
}
</style>
