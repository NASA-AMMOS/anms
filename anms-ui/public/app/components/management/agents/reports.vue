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
        label="ari"
        v-model="selected"
        @option:selected="onReportSelect()"></v-select>
    <b-table striped responsive :items="reports"></b-table>
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
      reports: [],
      reportsHeader: [{ key: 'reference_time', label: 'Time', sortable: true },
        { key: 'mgr_time', label: 'mgr_time', sortable: true },
        { key: 'rpt_set_nonce', label: 'rpt_set_nonce' }
      ],
      loading: true,
    }
  },
  methods: {
    async onReportSelect() {
      this.loading = true;
      this.tableHeaders = [];
      this.tableItems = [];
      this.loading = true;
      let report_source = this.selected.cbor;
      this.reports= [];
      await api.methods.apiEntriesForReport(this.registered_agents_id,report_source)
        .then(res => {
          
          this.reports = res.data;
        }).catch(error => {
          // handle error
          console.error("reports error", error);
          toastr.error("reports error: " + error)
        });
    
      this.loading = false;
    },
  },
  computed: {
  },
  mounted() {
    this.loading = true;
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
