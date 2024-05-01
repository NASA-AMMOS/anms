<template>
  <div>
    <b-card bg-variant="dark" class="my-3 border-grey">
      <b-form-group :label="ariKey.adm_name + '/' + ariKey.obj_name"
        label-cols-lg="3"
        label-size="md"
        label-class="font-weight-bold pt-0 label-color"
        class="mb-0">
        <div v-for="(parameter, index) in primParameters">
          <component v-bind:is="parameter.type"
            :listComponents="parameter.parameter.listComponents"
            :type="parameter.parameter.type"
            :types="parameter.parameter.types"
            :name="parameter.parameter.name"
            :result="parameter.parameter.result"
            :index="parameter.parameter.index"
            :key="index"></component>
        </div>
      </b-form-group>
      <b-form-group>
        <div v-for="(parameter, index) in tnvcParameters">
          <component v-bind:is="parameter.type"
            :listComponents="parameter.parameter.listComponents"
            :type="parameter.parameter.type"
            :types="parameter.parameter.types"
            :name="parameter.parameter.name"
            :result="parameter.parameter.result"
            :index="parameter.parameter.index"
            :key="index"></component>
        </div>
        <div v-for="(parameter, index) in exprParameters">
          <component v-bind:is="parameter.type"
            :listComponents="ACs"
            :type="parameter.parameter.type"
            :types="parameter.parameter.types"
            :name="parameter.parameter.name"
            :result="parameter.parameter.result"
            :index="parameter.parameter.index"
            :key="index"></component>
        </div>
        <div v-for="(parameter, index) in actions">
          <component v-bind:is="parameter.type"
            :listComponents="ACs"
            :type="parameter.parameter.type"
            :types="parameter.parameter.types"
            :name="parameter.parameter.name"
            :result="parameter.parameter.result"
            :index="parameter.parameter.index"
            :key="index"></component>
        </div>
      </b-form-group>
    </b-card>

    <!-- <b-form-row>
      <b-col>
        <p>Parameters for: {{ ariKey.adm_name }}.{{ ariKey.obj_name }}</p>
        <div v-if="loading" class="loader">
          <b-spinner variant="info" label="Loading..." type="grow"></b-spinner>
        </div>
      </b-col>
    </b-form-row>
    <b-form-row  v-for="(parms, indexRow) in computedParmsList" :key="indexRow">
      <b-col class="border-class" v-for="(parm, indexCol) in parms" :key="indexCol">

        <component @updateResult="updateResults($event)" v-bind:is="parm.type"
          :listComponents="parm.parameter.listComponents" :type="parm.parameter.type" :types="parm.parameter.types"
          :name="parm.parameter.name" :result="parm.parameter.result" :index="parm.parameter.index"></component>
      </b-col>
    </b-form-row>
    <b-button variant="info" :disabled="this.ariKey.actual || this.ariKey.parm_id == null" class
      @click="submitCommand()">
      SUBMIT for {{ ariKey.obj_name }}
    </b-button> -->
  </div>
</template>

<script>

import Vue from "vue";
import vSelect from "vue-select";
import parameter_builder from "./ariBuilder"

Vue.config.productionTip = false;
export default {
  name: "ParameterView",
  components: {
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
      primParameters: [],
      actions: [],
      tnvcParameters: [],
      exprParameters: [],
    };
  },

  mounted() {
    this.generateParameters();
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
    generateParameters() {
      parameter_builder.methods.genParms(this.ariKey, this.ARIs).then(response => {
        this.parameters = response[0];
        this.primParameters = this.getParametersByType("prim");
        this.tnvcParameters = this.getParametersByType("TypeNameValueCollectionParameter");
        this.exprParameters = this.getParametersByType("ExpressionParameter");
        this.actions = this.getParametersByType("ActionParameter");
      });
    },
    getParametersByType(type) {
      let parametersByType = [];
      for (let parameter of this.parameters) {
        if (parameter.type.name == type) {
          parametersByType.push(parameter);
        }
      }
      return parametersByType;
    },


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


<style scoped>
.label-color {
  color: white;
}

.card.border-grey {
  border-color: grey;
}
</style>
