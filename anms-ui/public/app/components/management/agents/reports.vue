
<template>
  <div>
    <h5>Reports sent:</h5>
    <div v-if="loading"
      class="spinner-border text-primary"
      role="status">
      <span class="sr-only">Loading...</span>
    </div>
    <b-form-select v-if="!loading"
      v-model="selected"
      @change="onReportSelect()"
      size="md"
      class="select-max-width">
      <b-form-select-option disabled
        value="-1">-- Select Sent Reports --</b-form-select-option>
      <b-form-select-option v-for="rpt, index in rptts"
        :key="index"
        :value="index">{{ rpt }}</b-form-select-option>
    </b-form-select>
    <b-table sticky-header
      hover
      bordered
      responsive
      v-if="!loading && selected != -1"
      id="report-table"
      :fields="tableHeaders"
      :items="tableItems"
      >
    </b-table>
  </div>
</template>

<script>
import api from '../../../shared/api'
import toastr from "toastr";

export default {
  name: "reports",
  props: ["agentName", "rptts"],
  data() {
    return {
      selected: -1,
      tableHeaders: [],
      tableItems: [],
      title: "",
      reports: {},
      reportsHeader: {},
      loading: true,
    }
  },
  methods: {
    async onReportSelect() {
      this.loading = true;
      this.tableHeaders = [];
      this.tableItems = [];
      this.loading = true;
      let correlator_nonce = this.rptts[this.selected].correlator_nonce;
      correlator_nonce = correlator_nonce;
      // let rpt_adm = this.rptts[this.selected].adm;
      await api.methods.apiEntriesForReport(this.agentName, correlator_nonce)
        .then(res => {
          this.processReport(res.data);
          this.reports[this.selected] = this.tableItems;
          this.reportsHeader[this.selected] = this.tableHeaders;
        }).catch(error => {
          // handle error
          console.error("reports error", error);
          console.info("error obj:", error);
          toastr.error("reports error: " + error)
        });
    
      this.loading = false;
    },
    processReport(report) {
      let holdHeader = report.shift();
      this.tableHeaders = [];
      for (let i = 0; i < holdHeader.length; i++) {
        this.tableHeaders.push({"key":holdHeader[i]});
        }
      for (let item of report) {
        let row = {};
        for (let i = 0; i < holdHeader.length; i++) {
          row[holdHeader[i]] = item[i];
        }
        this.tableItems.push(row);
      }
    }
  },
  computed: {
  },
  mounted() {
    this.loading = true;
    this.rptts.forEach((rpt, index) => {
      api.methods.apiEntriesForReport(this.agentName, rpt.correlator_nonce)
        .then(res => {
          this.reports[index] = res.data
        }).catch(error => {
          // handle error
          console.error("reports error", error);
          console.info("error obj:", error);

        });
    });
    this.loading = false;
  },
}


</script>
<style scoped>
.spacing-table {
  margin: 16px 0;
}

.select-max-width {
  max-width: 600px;
}
.b-table-sticky-header > .table.b-table > thead > tr > th {
  position: sticky !important;
}
</style>
