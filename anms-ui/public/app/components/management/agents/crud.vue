<template>
  <div>
    <!-- what are the inputs  -->
    <!-- request name -->
    <!-- request input -->
    <p>Operation: </p>
    <b-form-select v-model="selected"
      @change="setParams(selected.command_parameters)"
      size="md"
      class="select-max-width">
      <b-form-select-option disabled
        value="-1">-- Select Operation --</b-form-select-option>
      <b-form-select-option v-for="opt, index in Operations"
        :key="index"
        :value="opt">{{ opt.command_name }}</b-form-select-option>
    </b-form-select>
    <b-form class="form-spacing">
      <b-form-group v-for="(param) in params">
        <b-form-input class="capitalize"
          :id="param.name"
          v-model="param.value"
          :placeholder="param.name">
        </b-form-input>
      </b-form-group>
      <b-button @click="onClick()">Send Parameter</b-button>
    </b-form>

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
          this.results = "SENT! " + response.data + " " + response.statusText;
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
<style scoped>
.select-max-width {
  max-width: 600px;
}

.form-spacing {
  margin: 16px 0;
}

.capitalize::-webkit-input-placeholder { /* Chrome/Opera/Safari */
  text-transform: capitalize;
}
.capitalize::-moz-placeholder { /* Firefox 19+ */
  text-transform: capitalize;
}
.capitalize:-ms-input-placeholder { /* IE 10+ */
  text-transform: capitalize;
}
.capitalize:-moz-placeholder { /* Firefox 18- */
  text-transform: capitalize;
}
</style>
