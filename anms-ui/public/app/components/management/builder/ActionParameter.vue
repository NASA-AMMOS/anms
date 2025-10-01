<template>
  <div>
    <label>{{name}}({{ type }}):</label>
    <div>
      <b-form-group>
        <v-select v-model="ariKey"
          label="display"
          :options="listComponents"
          @input="addToList"
          :clearSearchOnSelect="false">
          <template v-slot:list-header="{ search, _ }">
              <b-button size="sm" @click="addARI(search)">Add ARI</b-button>
          </template>
        </v-select>
      </b-form-group>

      <label v-if="ac.length">Selected ARIs:</label>
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

      <div v-for="(curr, index) in keys"
        :key="index">
        <ParameterView :ariKey="curr"
          :ACs="listComponents"
          @updateResult="updateResults($event, index)"></ParameterView>
      </div>
    </div>
  </div>
</template>

<script>
import vSelect from "vue-select";

export default {
  name: "ActionParameter",
  components: {
    ParameterView: () => import("./ParameterView.vue"),
    vSelect,
  },
  props: ["listComponents", "name", "parms", "type", "index", "count"],
  data() {
    return {
      ariKey: undefined,
      ac: [],
      result: { index: this.index, type: "AC", value: [] },
      keys: [],
      currAc: [],
      keysRealIndex: [],
    };
  },
  methods: {
    addARI(newARI ) {
      newARI = newARI.trim();
      this.ariKey = { "display": newARI, "actual": true }
      this.addToList();
    },
    addToList: function () {
      if(this.ac.length >= this.count){
        this.ac.pop();
      }

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
      let head = value.includes("ari") ? "" : "ari://";
      let realIndex = this.keysRealIndex[index];
      this.currAc[realIndex] = head + value;
      this.submitAC();
    },
    submitAC: function () {
      this.result["value"] = this.currAc;
      this.$emit("updateResult", this.result);
    },
    createAC() {
      let currAc = [];
      this.keysRealIndex = [];
      this.keys = [];

      this.ac.forEach((ari, index) => {
        if (ari.actual || Number.isNaN(ari.parm_id)) {
          currAc.push(ari.display);
          this.keysRealIndex.push(index);
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
