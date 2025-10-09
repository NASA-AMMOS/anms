<template>
  <div>
    <h5>Reports sent:</h5>
    <div v-if="loading"
      class="spinner-border text-primary"
      role="status">
      <span class="sr-only">Loading...</span>
    </div>
    <v-select 
        :options="rptts" 
        label="exec_set"
        v-model="selected"
        @option:selected="onReportSelect()"></v-select>
    <div v-for="(_, index) in tableItems" :key="index">
      <b-table id="report-table" :items="tableHeaders[index]" thead-class="d-none">{{  }}</b-table>
      <div class="scrollable-div">
        <b-table 
        striped
        responsive
        v-if="!loading && selected != -1"
        id="report-table" :items="tableItems[index]"
        thead-class="d-none" />
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../../shared/api'
import toastr from "toastr";
import vSelect from "vue-select";

export default {
  name: "reports",
  components: {
    vSelect
  },
  props: ["agentName", "rptts", "registered_agents_id"],
  data() {
    return {
      selected: undefined,
      test: "",
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
      let nonce_cbor = this.selected.nonce_cbor;
    
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
      if(this.selected.exec_set in report){
        rpt = report[this.selected.exec_set];
      }else{
        rpt = report[this.selected.nonce_cbor];
      }
      let currTableItems = [];
      let holdHeader = rpt.shift();
      for (let item of rpt) {
        let row = {};
        for (let i = 0; i < item.length; i++) {
          let curr_item =  item[i];
          row[i]  = curr_item; 
        }
        currTableItems.push(row);
      }
      this.tableHeaders.push([holdHeader]);
      this.tableItems.push(currTableItems)
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
.scrollable-div {
  max-height: 600px; /* Set a maximum height for the div */
  overflow-y: auto; /* Add a vertical scrollbar when content exceeds max-height */
  /* overflow-y: scroll; /* Always show a vertical scrollbar */
}
</style>
