<template>
  <div>
    <label>Expression (Postfix Notation):</label>

    <b-form-group label="Return Type:"
      label-for="returnType"
      label-cols="3"
      label-align="right">
      <b-form-select id="returnType"
        size="sm"
        v-model="selectedExpressionReturnType"
        :options="expressionReturnTypes"
        @change="submitAC"></b-form-select>
    </b-form-group>

    <b-form-group label="Operations:"
      label-for="operationSelection"
      label-cols="3"
      label-align="right">
      <v-select id="operationSelection"
        v-model="ariKey"
        label="display"
        :options="filteredExpressionList"
        @input="addToList"></v-select>
    </b-form-group>

    <b-list-group class="mb-3">
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

  </div>
</template>

<script>
import ParameterView from "./ParameterView.vue";
import vSelect from "vue-select";

export default {
  name: "ExpressionParameter",
  components: { ParameterView, vSelect, },
  props: ["listComponents", "name", "parms", "type", "index"],
  data() {
    return {
      expressionReturnTypes: ["BYTE", "INT", "UINT", "VAST", "UVAST", "REAL32", "REAL64", "STRING", "BOOL"],
      selectedExpressionReturnType: undefined,
      expressionList: [],
      ariKey: undefined,
      ac: [],
      result: { index: this.index, type: "AC", value: [] },
      keys: [],
      currAc: [],
      keysRealIndex: [],
    };
  },
  filters: {},
  computed: {
    filteredExpressionList() {
      let typeOptions = ["LIT", "CONST", "EDD", "VAR", "OPER"];
      let results = [];
      this.listComponents.forEach((ari) => {
        if (typeOptions.includes(ari.type_name.toUpperCase())) {
          results.push(ari);
        }
      });
      return results;
    }
  },
  methods: {
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
    submitAC: function () {
      if (this.type == "EXPR") {
        this.result["type"] = "EXPR"
        this.result["value"] = "(" + this.selectedExpressionReturnType + ")%" + this.currAc;
      } else {
        this.result["value"] = this.currAc;
      }

      this.keysRealIndex = [];
      this.keys = [];

      this.$emit("updateResult", this.result);
    },

    // have to go through the AC and
    async createAC() {
      let currAc = [];
      this.keysRealIndex = [];
      this.keys = [];

      this.ac.forEach((ari, index) => {
        if (ari.actual || Number.isNaN(ari.parm_id)) {
          currAc.push(ari.display);
        } else {
          this.keys.push(ari);
          this.keysRealIndex.push(index);
          currAc.push(ari.display);
        }
      });

      this.currAc = currAc;
      this.submitAC();
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
