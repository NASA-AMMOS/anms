
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
        :value="index">{{ rpt.adm }}.{{ rpt.name }}</b-form-select-option>
    </b-form-select>
    <b-table v-if="!loading && selected != -1"
      id="report-table"
      :fields="tableHeaders"
      :items="tableItems"
      class="spacing-table"
      hover
      bordered
      responsive>
    </b-table>
  </div>
</template>

<script>
import api from '../../../shared/api'

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
      if (this.reports[this.selected] == undefined) {
        this.loading = true;
        let rpt_name = this.rptts[this.selected].name;
        let rpt_adm = this.rptts[this.selected].adm;
        await api.methods.apiEntriesForReport(this.agentName, rpt_adm, rpt_name)
          .then(res => {
            this.processReport(res.data);
            this.reports[this.selected] = this.tableItems;
            this.reportsHeader[this.selected] = this.tableHeaders;
          }).catch(error => {
            // handle error
            console.error("reports error", error);
            console.info("error obj:", error);
          });
      } else{
        this.tableHeaders = this.reportsHeader[this.selected];
        this.tableItems =  this.reports[this.selected];
      }
      
      this.loading = false;
    },
    processReport(report) {
      this.tableHeaders = report.shift();
      for (let item of report) {
        let row = {};
        for (let i = 0; i < this.tableHeaders.length; i++) {
          row[this.tableHeaders[i]] = item[i];
        }
        this.tableItems.push(row);
      }
    }
  },
  computed: {
  },
  mounted() {
    this.loading = true;

    // this.title = this.adm + "." + this.reportName
    this.rptts.forEach((rpt, index) => {
      api.methods.apiEntriesForReport(this.agentName, rpt.adm, rpt.name)
        .then(res => {

          this.reports[index] = res.data
          // this.headers = this.reports.shift()
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
</style>
