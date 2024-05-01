<template>
  <div>
    <label>{{ name }} (Type Name Value Collection):</label>

    <b-row class="px-1 py-1">
      <b-col cols="3">Type:</b-col>
      <b-col cols="4">Name:</b-col>
      <b-col cols="4">Value:</b-col>
      <b-col cols="1"></b-col>
    </b-row>

    <b-row>
      <b-col cols="3">
        <b-form-select id="type"
          size="sm"
          v-model="TNVCType"
          placeholder="Type"
          :options="types"></b-form-select>
      </b-col>
      <b-col cols="4">
        <b-form-input id="name"
          size="sm"
          v-model="TNVCName"></b-form-input>
      </b-col>
      <b-col cols="4">
        <b-form-input id="value"
          size="sm"
          v-model="TNVCValue"></b-form-input>
      </b-col>
      <b-col cols="1">
        <b-button class="button-icon"
          @click="addNewTnvc(TNVCType, TNVCName, TNVCValue)"><i class="fas fa-plus"></i></b-button>
      </b-col>
    </b-row>

    <b-list-group class="my-2">
      <b-list-group-item v-for="(TNVC, index) in TNVCs"
        :key="index">
        <b-row>
          <b-col cols="3">{{ TNVC.Type }}</b-col>
          <b-col cols="4">{{ TNVC.Name }}</b-col>
          <b-col cols="4">{{ TNVC.Value }}</b-col>
          <b-col cols="1">
            <b-button class="button-icon"
              @click="removeTNVC($event, index)"><i class="fas fa-times"></i></b-button>
          </b-col>
        </b-row>
      </b-list-group-item>
    </b-list-group>

  </div>
</template>

<script>

export default {
  name: "TypeNameValueCollectionParameter",
  props: ["name", "type", "types", "index"],
  data() {
    return {
      TNVCType: undefined,
      TNVCName: undefined,
      TNVCValue: undefined,
      message: 'TNVC:',
      result: [],
      final: { "index": this.index, "type": "TNVC", "value": [] },
      TNVCs: [],
    }
  },
  methods: {
    addNewTnvc(type, name, value) {
      type = type.trim();
      name = name.trim();
      value = value.trim();
      if (value == "") {
        // only care about if the V in TNVC is used
        // "value" overloaded term here means the value of the return object which would be an empty array
        this.final["value"] = this.result
        this.$emit('updateResult', this.final)

      } else {
        var new_tnv = value
        this.result.push(new_tnv);
        this.final["value"] = this.result
        // every time a new  entry is added the final TNVC list is updated
        this.$emit('updateResult', this.final)
      }
      this.TNVCs.push({ "Type": this.TNVCType.trim(), "Name": this.TNVCName.trim(), "Value": this.TNVCValue.trim() });
      this.clearInputs();

    },
    removeTNVC(index) {
      this.TNVCs.splice(index, 1);
    },
    clearInputs() {
      this.TNVCType = undefined;
      this.TNVCName = undefined;
      this.TNVCValue = undefined;
    }
  }
}
</script>

<style scoped>
.button-icon {
  padding: 4px 8px;
}
</style>
