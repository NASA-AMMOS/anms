<template>
  <div>
    <b-card bg-variant="dark"
      class="my-3 border-grey">
      <b-form-group :label="ariKey.data_model_name + '/' + ariKey.name"
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
            :key="index"
            @updateResult="updateResults($event)"></component>
        </div>
      </b-form-group>
      <b-form-group>
        <div v-for="(parameter, index) in exprParameters">
          <component v-bind:is="parameter.type"
            :listComponents="ACs"
            :type="parameter.parameter.type"
            :types="parameter.parameter.types"
            :name="parameter.parameter.name"
            :result="parameter.parameter.result"
            :index="parameter.parameter.index"
            :key="index"
            @updateResult="updateResults($event)"></component>
        </div>
        <div v-for="(parameter, index) in actionParameters">
          <component v-bind:is="parameter.type"
            :listComponents="ACs"
            :type="parameter.parameter.type"
            :types="parameter.parameter.types"
            :name="parameter.parameter.name"
            :result="parameter.parameter.result"
            :index="parameter.parameter.index"
            :key="index"
            :count="parameter.parameter.count"
            @updateResult="updateResults($event)"></component>
        </div>
      </b-form-group>
    </b-card>
  </div>
</template>

<script>
import vSelect from "vue-select";
import parameter_builder from "./ariBuilder"

export default {
  name: "ParameterView",
  components: {
    vSelect,
  },
  props: ["ariKey", "ACs", "nonce"],
  data() {
    return {
      parameters: [],
      finResult: [],
      finResultBase: [],
      finResultStr: "",
      description: "",
      primParameters: [],
      actionParameters: [],
      exprParameters: [],
    };
  },
  mounted() {
    this.generateParameters();
    this.$emit("updateResult", [{ type: "ARI", value: this.ariKey.display }]);
    this.finResult = this.finResultBase;

  },
  methods: {
    generateParameters() {
      parameter_builder.methods.genParms(this.ariKey, this.ARIs).then(response => {
        this.parameters = response[0];
        this.description = response[1];
        this.finResult = response[2];
        this.finResultBase = this.finResult;
        this.primParameters = this.getParametersByType("prim");
        this.exprParameters = this.getParametersByType("ExpressionParameter");
        this.actionParameters = this.getParametersByType("ActionParameter");
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
    updateResults(result) {
      this.finResult[result.index] = result;
      this.submitCommand();
    },
    submitCommand() {
    
      let testResult = [];
      if (this.ariKey.actual) {
        this.$emit("updateResult", [{ type: "OBJECT", value: this.ariKey.display }]);
        this.finResult = this.finResultBase;
      } else {
        this.finResult.forEach((element) => {
          let type = element["type"];
          let value = element["value"];
          let currValue = [];
          switch (type) {
            case "TEXTSTR":
              testResult.push(JSON.stringify(value));
              break;
            case "BYTESTR":
              testResult.push(JSON.stringify(value));
              break;
            case "BYTE":
              testResult.push(JSON.stringify(value));
              break;
            case "INT":
              testResult.push(JSON.stringify(value).replaceAll('"', ""));
              break;
            case "UINT":
              testResult.push(JSON.stringify(value).replaceAll('"', ""));
              break;
            case "VAST":
              testResult.push(JSON.stringify(value).replaceAll('"', ""));
              break;
            case "UVAST":
              testResult.push(
                JSON.stringify(value).replaceAll('"', "")
              );
              break;
            case "REAL32":
              testResult.push(
                JSON.stringify(value).replaceAll('"', "")
              );
              break;
            case "REAL64":
              testResult.push(
                JSON.stringify(value).replaceAll('"', "")
              );
              break;
            case "TP":
              testResult.push(JSON.stringify(value).replaceAll('"', ""));
              break;
            case "TD":
              testResult.push(JSON.stringify(value).replaceAll('"', ""));
              break;
            case "OBJECT": //ari
              let head = value.includes("ari:/") ? "" : "ari://";

              testResult.push(JSON.stringify(head + value).replaceAll('"', ""));
              break;
            case "AC": //ac
            let curr_str=  ""  
            currValue = [];
              value.forEach((ari) => {
                currValue.push(ari.replaceAll('"', ""));
              });
              if(currValue.length = 1 ){
                testResult.push(currValue[0])
              }else{
                testResult.push("/AC/("+currValue.join(",")+")");
              }
              break;

            case "EXPR": //ac
              currValue = [];
              var parts = value.split("%")
              parts[1].split(',').forEach((ari) => {
                currValue.push(ari.replaceAll('"', "'"));
              });

              testResult.push(parts[0] + JSON.stringify(currValue).replaceAll('"', ""));

              break;
            default:
            if (type.includes("TYPEDEF")){
              testResult.push(value[0]);
            }else{
              
              testResult.push((value));}
            
            break;
          }
        });

        if (this.ariKey.obj_metadata_id != null) {
          this.finResultStr =
            "ari://" +
            this.ariKey.namespace +
            "/" +
            this.ariKey.data_model_name +
            "/" +
            this.ariKey.type_name +
            "/" +
            this.ariKey.name +
            "(" +
            testResult +
            ")";
             // if using in agentModal adding 	ari:/EXECSET/ portion 
          if(typeof this.nonce !== 'undefined'){
            // correlator_nonc
            // TODO currently random mayube make it increment or a choice
            // let nonce = Math.floor(Math.random() * 99999) + 1;
            this.finResultStr = 	"ari:/EXECSET/n=" + this.nonce + ";(" + this.finResultStr +")";
          }
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