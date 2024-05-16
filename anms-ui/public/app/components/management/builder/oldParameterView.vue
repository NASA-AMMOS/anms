<template>
  <div>
    <b-form-row>
      <b-col>
        <p>Parameters for: {{ ariKey.adm_name }}.{{ ariKey.obj_name }}</p>
        <div v-if="loading"
          class="loader">
          <b-spinner variant="info"
            label="Loading..."
            type="grow"></b-spinner>
        </div>
      </b-col>
    </b-form-row>
    <b-form-row v-for="(parms, indexRow) in computedParmsList"
      :key="indexRow">
      <!-- <b-carousel id='categoryRoulette' controls indicators no-animation :interval='0' img-width="2024" img-height="3880"> -->
      <!-- <b-carousel-slide class=" align-items-center" img-blank  > -->
      <b-col class="border-class"
        v-for="(parm, indexCol) in parms"
        :key="indexCol">

        <component @updateResult="updateResults($event)"
          v-bind:is="parm.type"
          :listComponents="parm.parameter.listComponents"
          :type="parm.parameter.type"
          :types="parm.parameter.types"
          :name="parm.parameter.name"
          :result="parm.parameter.result"
          :index="parm.parameter.index"></component>
      </b-col>

      <!-- </b-carousel-slide> -->
      <!-- </b-carousel> -->
    </b-form-row>
    <b-button variant="info"
      :disabled="this.ariKey.actual || this.ariKey.parm_id == null"
      class
      @click="submitCommand()">
      SUBMIT for {{ ariKey.obj_name }}
    </b-button>
  </div>
</template>

<script>

import Vue from "vue";
// import ari_parameter from "./ariParamter";
// import TypeNameValueCollectionParameter from "./TypeNameValueCollectionParameter.vue";
// import prim_parameter from "./primParameter.vue";
import vSelect from "vue-select";
import parameter_builder from "./ariBuilder"

Vue.config.productionTip = false;
export default {
  name: "parameterBuilderView",
  components: {
    // ari_parameter,
    // TypeNameValueCollectionParameter,
    // prim_parameter,
    vSelect,
  },
  props: ["ariKey", "ACs"],
  watch: {
    ariKey: function (newVal) {
      this.genParms();
    },
  },

  data() {
    return {
      loading: false,
      doneIds: "test1",
      doneMgr: "test2",
      query: "",
      mngs: [],
      parameters: [],
      finResult: [],
      finResultBase: [],
      finResultStr: "",
      description: "",
      types: [],
    };
  },

  mounted() {
    this.genParms();
  },
  computed: {
    computedList: function () {
      var vm = this;

      return vm.ctrls.value.filter(function (item) {
        return item.obj_name.indexOf(vm.query.toLowerCase()) !== -1;
      });
    },
    computedParmsList: function () {
      let holdParm = [];
      let holdArray = [];
      let count = 0;

      this.parameters.forEach(parm => {

        if (parm["type"].name == "build_ari" || parm["type"].name == "build_ari") {
          holdArray.push(holdParm);
          count = 0;
          holdParm = [];
          holdArray.push([parm]);
        } else {
          holdParm.push(parm)
          count = count + 1;
          if (count > 3) {
            holdArray.push(holdParm);
            count = 0;
            holdParm = [];
          }
        }

      });
      holdArray.push(holdParm);
      return holdArray;
    },

  },
  methods: {
    genParms: async function () {
      this.finResultStr = "";
      let distParms = [];
      this.parameters = [];
      console.log(this.ariKey)
      if (this.ariKey.actual || this.ariKey.parm_id == null) {

        distParms = [];
        this.finResult = []
        this.submitCommand();
      } else {
        this.loading = true;
        let result = await parameter_builder.methods.genParms(this.ariKey, this.ACs);
        this.loading = false;
        this.parameters = result[0];
        this.description = result[1];
        this.finResult = result[2];
        this.finResultBase = this.finResult;
      }
    },
    updateResults: function (result) {
      this.finResult[result.index] = result;
      // this.finResult = this.finResult;
    },
    submitCommand: function () {
      let finResult = [];

      if (this.ariKey.actual) {
        this.$emit("updateResult", [{ type: "ARI", value: this.ariKey.display }]);
        this.finResult = this.finResultBase;
      } else {
        this.finResult.forEach((element) => {
          let type = element["type"];
          let value = element["value"];
          let currValue = [];
          switch (type) {
            case "STR":
              finResult.push(JSON.stringify(value));
              break;
            case "BYTESTR":
              finResult.push(JSON.stringify(value));
              break;
            case "BYTE":
              finResult.push(JSON.stringify(value));
              break;
            case "INT":
              finResult.push(JSON.stringify(value).replaceAll('"', ""));
              break;
            case "UINT":
              finResult.push(JSON.stringify(value).replaceAll('"', ""));
              break;
            case "VAST":
              finResult.push(JSON.stringify(value).replaceAll('"', ""));
              break;
            case "UVAST":
              finResult.push(
                JSON.stringify(value).replaceAll('"', "")
              );
              break;
            case "REAL32":
              finResult.push(
                JSON.stringify(value).replaceAll('"', "")
              );
              break;
            case "REAL64":
              finResult.push(
                JSON.stringify(value).replaceAll('"', "")
              );
              break;
            case "TV":
              finResult.push(JSON.stringify(value).replaceAll('"', ""));
              break;
            case "TS":
              finResult.push(JSON.stringify(value).replaceAll('"', ""));
              break;

            case "TNVC": //tnvc
              finResult.push(JSON.stringify(value));
              break;
            case "ARI": //ari
              let head = value.includes("ari:/") ? "" : "ari:/";

              finResult.push(JSON.stringify(head + value).replaceAll('"', ""));
              break;

            case "AC": //ac
              currValue = [];
              value.forEach((ari) => {
                currValue.push(ari.replaceAll('"', "'"));
              });

              finResult.push(JSON.stringify(currValue).replaceAll('"', ""));

              break;

            case "EXPR": //ac
              currValue = [];
              var parts = value.split("%")
              parts[1].split(',').forEach((ari) => {
                currValue.push(ari.replaceAll('"', "'"));
              });

              finResult.push(parts[0] + JSON.stringify(currValue).replaceAll('"', ""));

              break;
          }

        });
        // console.l
        if (this.ariKey.obj_metadata_id != null) {
          this.finResultStr =
            "ari:/IANA:" +
            this.ariKey.adm_name +
            "/" +
            this.ariKey.type_name +
            "." +
            this.ariKey.obj_name +
            "(" +
            finResult +
            ")";
          //   this.finResult = [{"type":"ARI", "value":this.finResultStr}];
          this.$emit("updateResult", [{ type: "ARI", value: this.finResultStr }]);
          this.finResult = this.finResultBase;
        }
      }
    },
  },
};
</script>


<style>
.wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: 100px 100px;
  gap: 10px;
}

.carousel-item {
  height: 600px;
}

.border-class {
  border: thin #62c462 solid;
  margin: 20px;
  padding: 20px;
}
</style>
