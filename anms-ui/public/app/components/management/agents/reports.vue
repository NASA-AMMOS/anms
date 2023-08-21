
<template>
  <div>
    <p>Reports sent:</p>
    <div v-if="loading" class="spinner-border text-primary" role="status">
      <span class="sr-only">Loading...</span>
    </div>
    <select v-if="!loading" v-model="selected" @change="onReportSelect()">
      <option disabled value="-1">-- Select Sent Reports --</option>
      <option v-for="rpt, index in rptts" :key="index" :value="index">{{ rpt.adm }}.{{ rpt.name }}</option>
    </select>
    <b-table v-if="!loading" id="report-table" :items="reports[selected]" hover bordered>
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
      headers: [],
      title: "",
      reports: {},
      loading: true,
    }
  },
  methods: {
    async onReportSelect() {
      this.loading = true;
      
      if (this.reports[this.selected] == undefined) {
        this.loading = true;
        let rpt_name = this.rptts[this.selected].name;
        let rpt_adm = this.rptts[this.selected].adm;
        await api.methods.apiEntriesForReport(this.agentName, rpt_adm, rpt_name)
          .then(res => {
            this.reports[this.selected] = res.data;
            // this.headers = this.reports.shift()
          }).catch(error => {
            // handle error
            console.error("reports error", error);
            console.info("error obj:", error);
          });
        }
      this.loading = false;
    },
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
<style scoped></style>