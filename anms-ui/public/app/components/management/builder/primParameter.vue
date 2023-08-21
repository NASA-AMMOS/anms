<template>
  <div>
    <div class="form-group" :class="{ 'form-group--error': $v.res.$error }">
      <label class="form__label">{{ name }}({{ type }}): </label>
      <input class="form__input" v-model.trim="$v.res.$model"  @input="updateResults()"/>
    </div>
      <div class="error" v-if="$v.res.$invalid">please enter a valid {{type}}</div>
  </div>
</template>

<script>
import {integer, decimal, minValue, helpers } from 'vuelidate/lib/validators'
import Vue from 'vue';
import Vuelidate from 'vuelidate';
Vue.use(Vuelidate);
const ariRegex = helpers.regex('ariRegex',/^ari:\/[a-zA-z]+\.[a-zA-z]\w*$/);
export default {
  name: "prim",
  props: ["type", "name", "index"],
  data() {
    return {
    
      res: "",
      isInt: false,
      isDec: false,
      isUnsigned: true, 
      result: { index: this.index, type: "null", value: "null" },
    };
  },
  validations() {  
      switch (this.type) {
        case "INT":
        case "VAST":
          return{res:{integer}}
        case "UINT":
        case "UVAST":
        case "TV":
        case "TS":
          return{res:{integer, minValue:minValue(0)}}
        case "REAL32":
        case "REAL64":
          return{res:{decimal}}
        case "ARI":
          return{res: {ariRegex}}
      }
      return{res:{}}
    },
  methods: {
    
    updateResults() {
      if(!this.$v.$invalid){
        this.result["type"] = this.type;
        this.result["value"] = this.$v.res.$model;
        this.$emit("updateResult", this.result);
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
</style>