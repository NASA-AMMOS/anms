<template>
  <div>
    <h5>ARI Builder</h5>
    <v-select v-model="ariKey"
      label="display"
      :options="ARIs"
      @input="generateParameters"></v-select>

    <parameter-view v-if="ariKey" :ariKey="ariKey" :ACs="ARIs"></parameter-view>
  </div>
</template>
<script>
import { mapActions, mapGetters } from "vuex";
import vSelect from "vue-select";
import parameter_builder from "../builder/ariBuilder";
import ParameterView from "./ParameterView.vue";
export default {
  name: "Build",
  components: { vSelect,
    ParameterView
  },
  props: {},
  data() {
    return {
      ariKey: undefined,
      parameters: undefined,
    }
  },
  computed: {
    ...mapGetters("build", {
      ARIs: "ARIs",
    })
  },
  methods: {
    generateParameters(ariKey) {
      parameter_builder.methods.genParms(ariKey, this.ARIs).then(response => {
        console.log(response);
        this.parameters = response[0];
      });
    }
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
