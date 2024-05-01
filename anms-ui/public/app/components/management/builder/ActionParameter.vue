<template>
  <div>
    <label>Actions:</label>
    <div>
      <b-form-group>
        <v-select v-model="ariKey"
          label="display"
          :options="listComponents"
          @input="addToList">
          <template v-slot:no-options="{ search, searching }">
            <template v-if="searching">
              <b-button @click="addARI(search)">Add ARI</b-button>
            </template>
          </template>
        </v-select>
      </b-form-group>

      <label v-if="ac.length">Selected Actions:</label>
      <b-list-group>
        <b-list-group-item v-for="(curr, index) in ac"
          :key="index">
          <b-row>
            <b-col>{{ curr.display }}</b-col>
            <b-col cols="1">
              <b-button class="button-icon"
                @click="removeFrom($event, index)"><i class="fas fa-times"></i></b-button>
            </b-col>
          </b-row>
        </b-list-group-item>
      </b-list-group>

      <div v-for="(curr, index) in keys" :key="index">
        <parameter-view :ariKey="curr" :ACs="listComponents"></parameter-view>
      </div>
    </div>
  </div>

</template>

<script>
import ParameterView from "./ParameterView.vue";
import vSelect from "vue-select";


export default {
  name: "ActionParameter",
  components: { ParameterView, vSelect, },
  props: ["listComponents", "name", "parms", "type", "index"],
  data() {
    return {
      ariKey: undefined,
      ready: false,
      ac: [],
      finResult: [],
      parameters: [],
      finResultStr: "",
      result: { index: this.index, type: "AC", value: [] },
      keys: [],
      currAc: [],
      currAcReady: [],
      keysRealIndex: [],
      exprType: null,
    };
  },
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
    addARI(newARI) {
      this.ariKey = { "display": newARI, "actual": true }
      this.addToList();
    },
    addToList: function () {
      if (this.ariKey != null) {
        this.ac.push(this.ariKey)
      }
      this.ariKey = null;
      this.createAC();
    },
    removeFrom: function (result, index) {
      this.ac.splice(index, 1)
      this.createAC();
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
        this.result["value"] = "(" + this.exprType + ")%" + this.currAc;
      } else {
        this.result["value"] = this.currAc;
      }

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

      this.ac.forEach((ari, index) => {
        this.finResultStr = "";
        if (ari.actual || Number.isNaN(ari.parm_id)) {
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
<style scoped>
.v-select.v-text-field input {
  color: black;
}

.button-icon {
  padding: 4px 8px;
}
</style>
