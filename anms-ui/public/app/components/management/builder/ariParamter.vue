<!-- for spawning options for paramets -->
<template>
  <div>
    <!-- add parameters  -->
    <!-- for gen report  -->
    <!-- need for AC -->
    <label>{{ name }}({{ type }}):</label>
    <b-form-group v-if="type == 'EXPR'">
      <label>EXPR Type:</label>
      <select id="exprType" v-model="exprType">
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
      <b-tooltip target="exprType">Expression object encapsulates a typed postfix expression in
        which each operator MUST be of type OPER and each operand MUST be the
        typed result of an operator or one of EDD, VAR, LIT, or CONST </b-tooltip>
    </b-form-group>

    <div>
      <b-row>
        <b-col cols="5">
          <label>
            Select ARI
          </label>
          <v-select id="selectAC" class="select-style" @search="onSearch" @input="addToList" v-model="ariKey"
            :options="paginated" :filterable="false" :get-option-label="(option) => option.display" small-chips>
            <li slot="list-footer" class="pagination">
              <button @click="submitNew">Submit new ARI</button>
              <button :disabled="!hasPrevPage" @click="offset -= limit">Prev</button>
              <button :disabled="!hasNextPage" @click="offset += limit">Next</button>
            </li>
          </v-select>
          <b-tooltip target="selectAC">Select ARI to add to AC</b-tooltip>
        </b-col>
        <b-col>
          <label>Current ARIs </label>
          <b-form-select id="removeAC" class="select-style" v-model="removeKey" :select-size="5">
            <b-form-select-option v-for="(curr, index) in ac" :key="index" @click="removeFrom($event, index)">
              {{ index }}-{{ curr.display }}
            </b-form-select-option>
          </b-form-select>
          <b-tooltip target="removeAC">Select ARI to remove from AC</b-tooltip>
        </b-col>
      </b-row>
      <b-row align-h="center">
        <b-button v-b-tooltip.hover title="Finalize list and generate parameters" @click="createAC()">
          Create AC
        </b-button>
      </b-row>
      <b-row align-h="center">
      <label>AC:</label>  
        {{ currAc }}
      </b-row>
    </div>
    <div class="test" v-for="(curr, index) in keys" :key="index">
      <ParameterView @updateResult="updateResults($event, index)" :ariKey="curr" :ACs="listComponents">
      </ParameterView>
    </div>
    <b-button v-b-tooltip.hover title="Send AC to be converted" :disabled="!ready" @click="submitAC()">
          Submit AC
        </b-button>
  </div>

</template>

<script>
import Vue from "vue";
import vMultiselectListbox from "vue-multiselect-listbox";
import ParameterView from "./parameterView.vue";
Vue.component("v-multiselect-listbox", vMultiselectListbox);
import vSelect from "vue-select";


export default {
  name: "build_ari",
  components: { ParameterView, vSelect, },
  props: ["listComponents", "name", "parms", "type", "index"],
  data() {
    return {
      removeKey: {},
      ariKey: {},
      ready: false,
      buttonON: false,
      selected: "A",
      ac: [],
      finResult: [],
      parameters: [],
      finResultStr: "",
      loading: false,
      result: { index: this.index, type: "AC", value: [] },
      currKey: "",
      keys: [],
      currAc: [],
      currAcReady: [],
      keysRealIndex: [],
      exprType: null,
      search: '',
      offset: 0,
      limit: 5,
      inputAri:"",
      lastKey:{}
    };
  },
  mounted() {
  },
  filters: {},
  computed: {
    filtered() {
      return this.computedAC.filter((ari) =>
        ari.display.toLocaleLowerCase().includes(this.search.toLocaleLowerCase())
      )
    },
    paginated() {
      return this.filtered.slice(this.offset, this.limit + this.offset)
    },
    hasNextPage() {
      const nextOffset = this.offset + this.limit
      return Boolean(
        this.filtered.slice(nextOffset, this.limit + nextOffset).length
      )
    },
    hasPrevPage() {
      const prevOffset = this.offset - this.limit
      return Boolean(
        this.filtered.slice(prevOffset, this.limit + prevOffset).length
      )
    },
    computedAC() {
      if (this.type == 'EXPR') {
        return this.createExpressionList(this.listComponents)
      }
      else {
        return this.listComponents
      }
    }
  },
  methods: {
    submitNew(){
      let inputAri = {"display": this.search,"actual":true}
      this.ac.push(inputAri)
      // this.lastKey = this.ariKey 
      this.ariKey = null
      this.search = ""
    },
    onSearch(query) {
      this.search = query
      this.offset = 0
      if(this.filtered.length == 0){
      }
    },

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
    addToList: function () {
      if (this.ariKey != null) {
        this.ac.push(this.ariKey)
      }
      this.lastKey = this.ariKey 
      this.ariKey = null
    },
    removeFrom: function (result, index) {
      this.ac.splice(index, 1)
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
<style>
.pagination {
  display: flex;
  margin: 0.25rem 0.25rem 0;
}

.pagination button {
  flex-grow: 1;
}

.pagination button:hover {
  cursor: pointer;
}

.select-style {
  background: #fff;
  color: black;
}

.wrapper {
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: 100px 100px;
  gap: 10px;
  display: block;
}

.wrapper-next {
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: 100px 100px;
  gap: 10px;

}

.v-select.v-text-field input {
  color: black;
}

.test {
  z-index: 3;
}
</style>
<!-- <style  src='vue-select/dist/vue-select.css'>
.a {
  vs-selected-color: #fff;
}
</style> -->

