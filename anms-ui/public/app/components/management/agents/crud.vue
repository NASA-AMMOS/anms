<template>
  <div>
    <!-- what are the inputs  -->
    <!-- request name -->
    <!-- request input -->
    <p>Operation: </p>
    <select v-model="selected" @change="setParams(selected.command_parameters)">
      <option disabled value="-1">-- Select Operation --</option>
      <option v-for="opt, index in Operations" :key="index" :value="opt">{{ opt.command_name }}</option>
    </select>
    <div v-for="(param) in params" v-bind:key="param.name">
      {{ param.name }}::
      <input v-b-tooltip.hover type="string" name="parms" v-model="param.value" />
    </div>
    <button @click="onClick()">Send Parameter</button>

    <div>
      [{{ results }}]
    </div>
  </div>
</template>

<script>
import { values } from 'lodash'
import api from '../../../shared/api'

export default {
  name: "CRUD",
  props: ["agentId", "Operations"],
  data() {
    return {
      selected: -1,
      headers: [],
      title: "",
      results: "",
      results2: "",
      params: [],
      final_values: {}
    }

  }, methods: {

    setParams(command_parameters) {
      command_parameters.forEach((value) => {
        this.results2 = value;
        this.params.push({ "name": value, "value": "" });
      });

      this.results = command_parameters;
    },
    onClick() {
      this.final_values = {}
      this.params.forEach((param) =>
        this.final_values[param.name] = param.value
      )
      api.methods
        .apiPutCRUD(this.agentId, this.selected.agent_parameter_id, this.final_values)
        .then((response) => {
          this.results = "SENT! "+ response.data + " " + response.statusText ;
          this.selected = -1;
          this.params = []
        })
        .catch((error) => {
          this.results = "ERROR sending " + error
          console.error(error);
        })
    },
  },
  computed: {
  },
  mounted() {
  }
}


</script>
<style scoped></style>