<template>
  <div>
    <center>
      <toggle-button id="tButton"
        v-model="stringMode"
        :labels="{ checked: 'Text Input', unchecked: 'ARI Builder' }"
        :width="100" />
    </center>
    <div>
      <div class="wrapper-next">
        <template v-if="stringMode">
          <label>Enter String to translate:</label>
          <div class="input-group mb-3">
            <input type="text"
              class="form-control"
              placeholder="ari:0x0"
              v-model="cborString"
              v-on:keyup.enter="handleCbor($event.target.value)" />
            <div class="input-group-append">
              <b-button variant="info"
                class="btn btn-outline-secondary"
                type="button"
                @click="handleCbor(cborString)">
                SUBMIT
              </b-button>
            </div>
          </div>
          <p>Current URI = {{ finResultStr }}</p>
        </template>
      </div>

      <template v-if="!stringMode">

        <b-container>
          <h5>ARI Builder</h5>
          <label>
          <input type="checkbox" v-model="isExecutionCheck" onchange="updateNonce"/>
          Execution Set?
        </label>
        <div v-if="isExecutionCheck">
          <label>correlator_nonce:</label>
          <b-form-input 
          size="sm"
          v-model="correlator_nonce"
          @change="updateResults"/>
          </div>
          <v-select v-model="ariKey"
            label="display"
            :options="ARIs" 
            :clearSearchOnSelect="false"></v-select>
          <ParameterView v-if="ariKey"
            :ariKey="ariKey"
            :ACs="ARIs"
            :nonce="correlator_nonce"
            @updateResult="updateResults($event)"></ParameterView>

          <div v-if="ariKey" class="text-center my-3">
            <h5>ARI String</h5>
            <p>{{ finResultStr }}</p>
            <b-button class="my-3"
              variant="outline-success"
              @click="submitAriString">Submit ARI String</b-button>
          </div>
        </b-container>
      </template>
    </div>
    <br />
    <!-- the table for the translated -->
    <div>
      <Transcoder ref="transcoder"></Transcoder>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import ParameterView from "./ParameterView.vue";
import vSelect from "vue-select";
import { mapGetters, mapActions } from "vuex";
import api from "../../../shared/api.js";
import Transcoder from "./transcoder.vue";
import { ToggleButton } from 'vue-js-toggle-button';
import toastr from "toastr";


Vue.component('ToggleButton', ToggleButton)

Vue.config.productionTip = false;


export default {
  name: "Build",
  components: {
    vSelect,
    ParameterView,
    Transcoder,
  },
  data() {
    return {
      query: "",
      aris: [],
      ariKey: undefined,
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
      stringMode: false,
      correlator_nonce: undefined,
      isExecutionCheck: false,
    };
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
        return item.name.indexOf(vm.query.toLowerCase()) !== -1;
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
    updateNonce(){
      this.correlator_nonce = undefined;
    },
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
          ari.name.toLowerCase().includes(search.toLowerCase()) ||
          ari.data_model_name.toLowerCase().includes(search.toLowerCase()) ||
          ari.type_name.toLowerCase().includes(search.toLowerCase())
        ) {
          aris.push(ari);
        }
      });
      loading(false);
      vm.options = aris;
    }, 350),
    handleCbor(inputString) {
      inputString = inputString.trim()
      api.methods
        .apiPutTranscodedString(inputString)
        .then((response) => {
          this.finResultCbor = response.data
          this.results = response.data.status
          toastr.success(`${response.data.status}, 'Transcoder Log Id: ${response.data.id}`);

        })
        .catch((error) => {
          console.error(error);
          this.errored = true;
          this.results = "error translating " + error;
          toastr.error(`${this.results}`);
        })
        .finally(() => (this.loading = false));
      this.finResultStr = inputString;
      let sleep = (time) => new Promise((resolve) => setTimeout(resolve, time));
      // allow time for the ARI to be added to the DB
      sleep(200).then(() => {
        this.$refs.transcoder.reloadTranscoderLog();
      });
    },
    updateResults: function (result) {
      let head = result[0].value.includes("ari") ? "" : "ari://";
      this.finResultStr = head + result[0].value;
    },
    submitAriString() {
      this.handleCbor(this.finResultStr);
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
<style src='vue-select/dist/vue-select.css'>
.a {
  vs-selected-color: #fff;
}
</style>
