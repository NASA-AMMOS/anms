<template>
  <div>
    <b-form-group :label="name + ' (' + type + '):'"
      :label-for="name"
      label-cols-sm="3"
      label-align-sm="right">
      <b-form-input :id="name"
        size="sm"
        v-model="value"
        @change="updateResults"></b-form-input>
    </b-form-group>
  </div>
</template>

<script>
export default {
  name: "prim",
  props: ["type", "name", "index"],
  data() {
    return {
      value: undefined,
      result: { index: this.index, type: "null", value: "null" },
    };
  },
  methods: {
    updateResults() {
      this.result["type"] = this.type;
      this.result["value"] = this.value;
      this.$emit("updateResult", this.result);
    },
  },
};
</script>

<style></style>
