<template>
  <div>
    <h5>ARI Builder</h5>
    <center>
      <toggle-button id="tButton" v-model="stringMode" :labels="{ checked: 'Text Input', unchecked: 'ARI Builder' }"
        :width="100" />
    </center>
    <div>
      <div class="wrapper-next">
        <template v-if="stringMode">
          <label>Enter Text To Translate:</label>
          <div class="input-group mb-3">
            <input type="text" class="form-control" placeholder="0x0" v-model="cborString"
              v-on:keyup.enter="handleCbor($event.target.value)" />
            <div class="input-group-append">
              <b-button variant="info" class="btn btn-outline-secondary" type="button" @click="handleCbor(cborString)">
                SUBMIT
              </b-button>
            </div>
          </div>
        </template>
      </div>
      <template v-if="!stringMode">
        <label>
          <input type="checkbox" v-model="isExecutionCheck"/>
          Execution Set?
        </label>
        <div v-if="isExecutionCheck">
          <!-- <label>correlator_nonce:</label> -->
          <b-form-input 
          size="sm"
          v-model="correlator_nonce"
          @change="updateResults"/>
          </div>
        <v-select v-model="ariKey" label="display" :options="ARIs" ></v-select>
        <ParameterView v-if="ariKey" :ariKey="ariKey" :ACs="ARIs" :nonce="correlator_nonce" @updateResult="updateResults($event)"></ParameterView>
      </template>
    </div>
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
  props:{
    cbor: {
      type: String,
      default: undefined
    },
    agentModal:{
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      ariKey: undefined,
      parameters: undefined,
      finResultStr: undefined,
      stringMode: false,
      cborString: "",
      correlator_nonce: undefined,
      isExecutionCheck: false,
    }
  },
  mounted(){
    this.cborString = this.cbor;
  },
  computed: {
    ...mapGetters("build", {
      ARIs: "ARIs",
    })
  },
  methods: {
    handleCbor(inputString) {
      this.finResultStr = inputString.trim()
      this.$emit("updateResult", this.finResultStr);
    },
    updateResults: function (result) {
      let head = result[0].value.includes("ari") ? "" : "ari:";
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
