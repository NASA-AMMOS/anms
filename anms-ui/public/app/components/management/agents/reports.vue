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
        :value="index">{{ rpt.exec_set }}</b-form-select-option>
    </b-form-select>
    <div v-for="(_, index) in tableHeaders" :key="index">
      <b-table sticky-header
      hover
      bordered
      responsive
      v-if="!loading && selected != -1"
      id="report-table" :items="tableItems[index]" :fields="tableHeaders[index]"></b-table>
    </div>
  </div>
</template>

<script>
import api from '../../../shared/api'
import toastr from "toastr";

export default {
  name: "reports",
  props: ["agentName", "rptts", "registered_agents_id"],
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
      let nonce_cbor = this.rptts[this.selected].nonce_cbor;
      nonce_cbor = nonce_cbor;
      await api.methods.apiEntriesForReport(this.registered_agents_id,encodeURIComponent(nonce_cbor))
        .then(res => {
          this.processReport(res.data);
          this.reports[this.selected] = this.tableItems;
          this.reportsHeader[this.selected] = this.tableHeaders;
        }).catch(error => {
          // handle error
          console.error("reports error", error);
          toastr.error("reports error: " + error)
        });
    
      this.loading = false;
    },
    processReport(report) {
      let rpt = [];
      if(this.rptts[this.selected].exec_set in report){
        rpt = report[this.rptts[this.selected].exec_set];
      }else{
        rpt = report[this.rptts[this.selected].nonce_cbor];
      }
      
      
      let currTableItems = [];
      let currTableHeaders = []
      let holdHeader = rpt.shift();
      console.log(rpt[0].length);
      console.log(holdHeader.length);
      console.log(rpt[0].length - holdHeader.length);
      if(rpt[0].length > holdHeader.length){
        for (let i = 0; i <= rpt[0].length - holdHeader.length; i++) {
          holdHeader.push(" ".padStart(i, ' '));
        }
      }
      console.log(holdHeader);
      for (let i = 0; i < holdHeader.length; i++) {
        currTableHeaders.push({"key":holdHeader[i]});
      }

      for (let item of rpt) {
        let row = {};
        for (let i = 0; i < item.length; i++) {
          let curr_item =  item[i];
            row[holdHeader[i]]  = curr_item; 
        }
        console.log(row)
        currTableItems.push(row);
      }
      this.tableHeaders.push(currTableHeaders);
      this.tableItems.push(currTableItems)
    console.log(this.tableItems);
    }
  },
  computed: {
  },
  mounted() {
    this.loading = true;
    this.rptts.forEach((rpt, index) => {
      api.methods.apiEntriesForReport(this.registered_agents_id, rpt.nonce_cbor)
        .then(res => {
          this.reports[index] = res.data
        }).catch(error => {
          // handle error
          console.error("reports error", error);
          console.log("error obj:", error);

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
