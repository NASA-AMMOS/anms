<!-- for spawning options for paramets -->
<template>
  <div>
    <!-- add parameters  -->
    <!-- for gen report  -->
    <!-- need for AC -->

    <div>
      <label>{{ name }}({{ type }}):</label>
      <b-form-group v-if="type == 'EXPR'">
        <label>EXPR Type:</label>
        <select v-model="exprType">
          <option disabled value="">Which Type?</option>
          <option>BYTE</option>
          <option>INT</option>
          <option>UINT</option>
          <option>VAST</option>
          <option>UVAST</option>
          <option>REAL32</option>
          <option>REAL64</option>
          <option>STRING</option>
          <option>BOOL</option>
        </select>
      </b-form-group>
      <v-multiselect-listbox
        v-if="type == 'EXPR'"
        v-model="ac"
        :options="createExpressionList(listComponents)"
        :reduce-display-property="
          (option) => (option.actual ? 'actual:' : 'formal:') + option.display
        "
        :reduce-value-property="
          (option) =>
            option.obj_metadata_id +
            '&' +
            option.obj_name +
            '&' +
            option.adm_name +
            '&' +
            option.type_name +
            '&' +
            option.namespace_id +
            '&' +
            option.obj_id +
            '&' +
            option.parm_id +
            '&' +
            option.actual +
            '&' +
            option.display +
            '&' +
            option.param_names +
            '&' +
            option.param_types
        "
      >
      </v-multiselect-listbox>
      <v-multiselect-listbox
        v-if="type != 'EXPR'"
        v-model="ac"
        :options="listComponents"
        :reduce-display-property="
          (option) => (option.actual ? 'actual:' : 'formal:') + option.display
        "
        :reduce-value-property="
          (option) =>
            option.obj_metadata_id +
            '&' +
            option.obj_name +
            '&' +
            option.adm_name +
            '&' +
            option.type_name +
            '&' +
            option.namespace_id +
            '&' +
            option.obj_id +
            '&' +
            option.parm_id +
            '&' +
            option.actual +
            '&' +
            option.display +
            '&' +
            option.param_names +
            '&' +
            option.param_types
        "
      >
      </v-multiselect-listbox>
      <!-- {{ac}} -->
    </div>
    <b-button @click="createAC()">Create AC</b-button>

    <!-- creating parameters for each entry in the AC -->
    <div v-for="(curr, index) in keys" :key="index">
      <ParameterView
        @updateResult="updateResults($event, index)"
        :ariKey="curr"
        :ACs="listComponents"
      >
      </ParameterView>
    </div>
    <b-button :disabled="!ready" @click="submitAC()">Submit AC</b-button>
  </div>
</template>

<script>
import Vue from "vue";
import vMultiselectListbox from "vue-multiselect-listbox";
import ParameterView from "./parameterView.vue";
Vue.component("v-multiselect-listbox", vMultiselectListbox);

export default {
  name: "build_ari",
  components: { ParameterView },
  props: ["listComponents", "name", "parms", "type", "index"],
  data() {
    return {
      ready: false,
      buttonON: false,
      selected: "A",
      ac: [],
      finResult: [],
      parameters: [],
      finResultStr: "",
      loading: false,
      result: { "index": index, type: "AC", value: [] },
      currKey: "",
      keys: [],
      currAc: [],
      currAcReady: [],
      keysRealIndex: [],
      exprType:null,
    };
  },
  filters: {},
  methods: {
    //   Literal, Constant, Externally Defined Data, or
    //  Variable.  An operator MUST be an ARI of type Operator
    createExpressionList: function (ARIs) {
      let typeOptions = ["LIT", "CONST", "EDD", "VAR", "OPER"];
      let results = [];
      ARIs.forEach((ari) => {
        if (typeOptions.includes(ari.type_name.toUpperCase())) {
          results.push(ari);
        }
      });
      return results;
    },

    updateResults: function (result, index) {

      let value = result[0].value;
      let head = value.includes("ari") ? "" : "ari:/";
      let realIndex = this.keysRealIndex[index];
      // let head = "ari:/";

      this.currAc[realIndex] = head + value;
      this.currAcReady[realIndex] = true;

      this.ready = true;
      this.currAcReady.findIndex((element) => {
        if (element == false) {
          this.ready = false;
        }
      });
    },
    submitAC: function () {
      if (this.type == "EXPR") {
        this.result["type"] = "EXPR"
        this.result["value"] = "(" + this.exprType +")%" + this.currAc;
      } else {
        this.result["value"] = this.currAc;
      }
      this.result["index"] = this.index
      this.currAcReady = [];
      this.keysRealIndex = [];
      this.keys = [];

      this.$emit("updateResult", this.result);
    },

    // have to go through the AC and
    async createAC() {
      let res = [];
      this.ready = true;
      let currAc = [];
      this.currAcReady = [];
      this.keysRealIndex = [];
      this.parameters = [];
      this.keys = [];

      this.ac.forEach((element, index) => {
        let parts = element.split("&");
        let ari = {
          obj_metadata_id: parseInt(parts[0]),
          obj_name: parts[1],
          adm_name: parts[2],
          type_name: parts[3],
          namespace_id: parseInt(parts[4]),
          obj_id: parseInt(parts[5]),
          parm_id: parseInt(parts[6]),
          actual: parts[7] == "true",
          display: parts[8],
          param_names: parts[9].split(","),
          param_types: parts[10].split(","),
        };

        this.finResultStr = "";
        var distParms = [];
        if (ari.actual || Number.isNaN(ari.parm_id)) {
          distParms = [];
          currAc.push(ari.display);
          this.currAcReady.push(true);
        } else {
          this.keys.push(ari);
          this.keysRealIndex.push(index);
          this.ready = false;
          this.currAcReady.push(false);
          currAc.push(ari.display);
        }
      });

      this.currAc = currAc;
    },
  },
};
</script>

<style src='vue-multiselect-listbox/dist/vue-multi-select-listbox.css'>
</style>
<style>
.wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: 100px 100px;
  gap: 10px;
}
</style>
