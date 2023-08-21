<template>
  <div>
    <template v-if="hasUpdateError">
      <div class="d-flex justify-content-center mb-3">
        <b-badge  show variant="danger">{{updateError}}</b-badge>
      </div>
    </template>


   
    <template v-if="hasData">
          <table class="table table-striped table-hover table-bordered table-sm text-center">
          <thead class="table-dark">
            <tr>
              <th class="text-info">Service Name</th>
              <th class="text-info">Status</th>
            </tr>
          </thead>
          <tbody>
            <template  v-if="serviceError" v-for="name in sortedErrorServices">
              <tr>
                <td>{{name}}</td> 
                <td class="text-danger">{{errorServices[name]}}</td>
              </tr>
            </template>
            <template v-for="name in sortedNormalServices">
              <tr>
                <td>{{name}}</td> 
                <td class="text-success">{{normalServices[name]}}</td>
              </tr>
            </template>
          </tbody>
        </table>
    </template>
    <template v-if="serviceLoading">
      <div class="d-flex justify-content-center mt-3">
        <b-spinner variant="info" label="Loading..." type="grow"></b-spinner>
      </div>
    </template>
    <div class="d-flex justify-content-center mt-3">
          <b-button @click="updateServiceStatus" variant="info" size="sm">Check Service Status</b-button>
    </div>
  </div>
  
</template>

<script>
import { mapGetters, mapActions } from "vuex";

export default {
  name: "Status",
  data() {
    return {
    };
  },
  computed: {
      ...mapGetters("service_status", {
        updateError: "updateError",
        serviceLoading: "loading",
        errorServices: "errorServices",
        normalServices: "normalServices"
      }),
      hasUpdateError() {
        return this.updateError !== "";
      },
      hasData() {
        return this.sortedNormalServices.length > 0 || this.sortedErrorServices.length > 0;
      },
      serviceError() {
        return Object.keys(this.errorServices).length > 0;
      },
      sortedNormalServices() {
        console.log("sorting:" , this.normalServices);
        return Object.keys(this.normalServices).sort();
      },
      sortedErrorServices() {
        return Object.keys(this.errorServices).sort();
      }
  },
  methods: {
    ...mapActions("service_status", {
        updateServiceStatus: "updateStatus"
      })
  }

}
</script>

<style scoped>
</style>
