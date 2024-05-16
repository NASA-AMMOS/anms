<template>
  <div>
    <center>
      Input Style(String Input/ARI Builder)<br>
      <toggle-button id="tButton" v-model="stringMode" :value="true"
        :labels="{ checked: 'String Input', unchecked: 'ARI Builder' }" :width="100" />
    </center>
    <div >
      <div class="wrapper-next">
        <template v-if="stringMode">
          <label>Enter String to translate:</label>
          <div class="input-group mb-3">
            <input type="text" class="form-control" placeholder="ari:0x0" v-model="cborString" v-on:keyup.enter="handleCbor($event.target.value)" />
            <div class="input-group-append">
              <b-button variant="info" class="btn btn-outline-secondary" type="button" @click="handleCbor(cborString)">
                SUBMIT
              </b-button>
            </div>
          </div>
          <p>Current URI = {{ finResultStr }}</p>
        </template>
      </div>

      <template v-if="!stringMode">
        <label>Search for an Ari:</label>
        <div v-if="loading" class="loader">
          <b-spinner variant="info" label="Loading..." type="grow"></b-spinner>
        </div>
        <v-select v-if="!loading" @search="onSearch" @input="genParms" v-model="ariKey" style="background: #fff"
          class="a" :options="ARIs" :get-option-label="(option) => option.display">
        </v-select>
        <p>{{ description }}</p>
        <p>Current URI = {{ finResultStr }}</p>


        <div  align="center">
          <ParameterView @updateResult="updateResults($event, index)" @v-if="selected" :ariKey="ariKey" :ACs="ARIs">
          </ParameterView>
        </div>
      </template>
    </div>
    <br/>
    <!-- the table for the translated -->
    <div>
    <Transcoder ref="transcoder"></Transcoder>
    </div>

  </div>
</template>

<script>
import Vue from "vue";
import { reactive } from "vue";
import TypeNameValueCollectionParameter from "./TypeNameValueCollectionParameter.vue";
import prim_parameter from "./primParameter.vue";
import ParameterView from "./oldParameterView.vue";
import vSelect from "vue-select";
import { mapGetters, mapActions } from "vuex";
import api from "../../../shared/api.js";
import Transcoder from "./transcoder.vue";
import { ToggleButton } from 'vue-js-toggle-button'

Vue.component('ToggleButton', ToggleButton)

Vue.config.productionTip = false;


export default {
  name: "Build",
  components: {
    TypeNameValueCollectionParameter,
    prim_parameter,
    vSelect,
    ParameterView,
    Transcoder,
  },
  data() {
    return {
      // loading: false,
      query: "",
      aris: [],
      ariKey: {},
      options: [],
      mngs: [],
      parameters: null,
      finResult: [],
      finResultStr: "",
      finResultCbor: "",
      description: "",
      selected: false,
      cborString: "",
      checkbox: false,
      stringMode: true,
    };
  },
  async mounted() {

  },
  computed: {
    ...mapGetters("build", {
      ARIs: "ARIs",
      count: "count",
      searchString: "searchString",
      loading: "loading"
    })
    ,
    computedList: function () {
      let vm = this;
      return vm.ctrls.value.filter(function (item) {
        return item.obj_name.indexOf(vm.query.toLowerCase()) !== -1;
      });
    },
    computedParmsList: function () {
      return this.parameters;
    },
  },
  methods: {

    ...mapActions("build", {
      reloadARIs: "reloadARIs",
      setSearchString: "setSearchString"
    }),


    onSearch(search, loading) {
      if (search.length) {
        loading(true);
      }
      this.search(loading, search, this);
    },
    search: _.debounce((loading, search, vm) => {
      let aris = [];
      vm.ARIs.forEach((ari) => {
        if (
          ari.obj_name.toLowerCase().includes(search.toLowerCase()) ||
          ari.adm_name.toLowerCase().includes(search.toLowerCase()) ||
          ari.type_name.toLowerCase().includes(search.toLowerCase())
        ) {
          aris.push(ari);
        }
      });
      loading(false);
      vm.options = aris;
    }, 350),

    genParms: async function () {
      this.selected = true;
      this.finResultStr = "";
      return;
    },
    handleCbor(inputString) {
      inputString = inputString.trim()
      api.methods
        .apiPutTranscodedString(inputString)
        .then((response) => {
          this.finResultCbor = response.data
        })
        .catch((error) => {
          console.error(error);
          this.errored = true;
          this.results = "error translating " + error;
        })
        .finally(() => (this.loading = false));
        this.finResultStr = inputString;
        this.$refs.transcoder.reloadTranscoderLog();
    },
    updateResults: function (result, index) {
      let head = result[0].value.includes("ari") ? "" : "ari:/";

      this.finResultStr = head + result[0].value;

      api.methods
        .apiPutTranscodedString(this.finResultStr)
        .then((response) => {

          this.finResultCbor = response.data
        })
        .catch((error) => {
          console.error(error);
          this.errored = true;
          this.results = "error translating " + error;
        })
        .finally(() => (this.loading = false));
      wait
      this.$refs.transcoder.reloadTranscoderLog();
      return;
    },
  },
};
</script>

<style>
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
</style>
<style  src='vue-select/dist/vue-select.css'>
.a {
  vs-selected-color: #fff;
}
</style
