<template>
  <div>
    <template v-if="hasAdms">
      <table class="table table-striped table-hover table-bordered table-sm text-center">
        <thead class="table-dark">
          <tr>
            <th class="text-info">enumeration</th>
            <th class="text-info">Name</th>
            <th class="text-info">Namespace</th>
            <th class="text-info">Version</th>
            <th class="text-info">Use Description</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(adm, index) in adms">
            <tr :key="index">
              <td>{{ adm.enumeration }}</td>
              <td v-b-tooltip.hover
                  title="Download ADM YANG" @click="download(adm)" ><b>{{ adm.name }}</b></td>
              <td>{{ adm.namespace }}</td>
              <td>{{ adm.version_name }}</td>
              <td>{{ adm.use_desc }}</td>
            </tr>
          </template>
        </tbody>
      </table>
    </template>
    <template v-if="loading">
      <div class="d-flex justify-content-center mt-3">
        <b-spinner variant="info" label="Loading..." type="grow"></b-spinner>
      </div>
    </template>
    <div class="d-flex justify-content-center mt-3">
      <b-button @click="getAdms" variant="info" size="sm">Get ADMs</b-button>
    </div>
    <div class="input-group mt-3 mb-3 justify-content-center">
      <div class="col-3"></div>
      <b-form-group class="custom-file col-3">
        <b-form-file v-model="file" id="adm" name="adm" accept=".yang"></b-form-file>
      </b-form-group>
      <b-button @click="uploadAdms" variant="info" :disabled="!hasValidFile">Upload ADM yang</b-button>
      <div class="col-3"></div>
    </div>
    <template v-if="hasRequestError">
      <div class="d-flex justify-content-center mb-3">
        <b-badge show variant="danger">{{ requestError }}</b-badge>
      </div>
      <table v-if="hasUploadError" class="table table-striped table-hover table-bordered table-sm text-center">
        <thead class="table-dark">
          <tr>
            <th class="text-danger">Object Type</th>
            <th class="text-danger">Name</th>
            <th class="text-danger">Issue</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(error, index) in uploadErrors">
            <tr :key="index">
              <td>{{ error.obj_type }}</td>
              <td>{{ error.name }}</td>
              <td>{{ error.issue }}</td>
            </tr>
          </template>
        </tbody>
      </table>
    </template>

  </div>

</template>

<script>
import { mapGetters, mapActions } from "vuex";
import toastr from 'toastr';
import api_adm from '@app/shared/api_adm';

const _ = require('lodash');

export default {
  name: "Adms",
  data() {
    return {
      file: null,
      allowUploadTypes: ["application/json"]
    };
  },
  computed: {
    ...mapGetters("adm", {
      adms: "adms",
      loading: "loading",
      requestError: "requestError",
      uploadErrors: "uploadErrors",
      uploadStatus: "uploadStatus"
    }),
    hasRequestError() {
      return this.requestError != "";
    },
    hasUploadError() {
      return this.uploadErrors.length > 0;
    },
    hasAdms() {
      //return !this.loading && this.adms.length > 0;
      return this.adms.length > 0;
    },
    hasValidFile() {
      return (!_.isNull(this.file) && _.includes(this.allowUploadTypes, this.file.type));
    },
  },
  async mounted() {
    if (!this.hasAdms) {
      await this.getAdms();
    }
  },
  methods: {
    ...mapActions("adm", {
      getAdms: "getAdms",
      uploadAdm: "uploadAdm"
    }),
    download(adm){
      let json  = {};
      api_adm.apiGetAdm(adm.enumeration, adm.namespace).then(res => {
        json= res.data;
        const jsonData = json;
        const blob = new Blob([jsonData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = adm.name +".yang";
        link.click();
        URL.revokeObjectURL(url);
      })
      .catch(function (error) {
          console.error("No ADM to downlaod ")
          console.error(error)
          toastr.error(("No ADM to downlaod "))
      });
    },
    async uploadAdms() {
      let json_file = this.file;
      this.file = null;
      await this.uploadAdm(json_file);
      if (!_.isNil(this.requestError) && this.requestError != "") {
        toastr.error(this.requestError);
      }
      else if (!_.isNil(this.uploadStatus) && this.uploadStatus != "") {
        toastr.success(this.uploadStatus);
        await this.getAdms();
      }

      return;
    }
  }

}
</script>

<style scoped>

</style>
