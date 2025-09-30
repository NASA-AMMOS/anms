<template>
  <div>
    <template v-if="serviceLoading">
      <div class="d-flex justify-content-center mt-3">
        <b-spinner variant="info"
          label="Loading..."
          type="grow"></b-spinner>
      </div>
    </template>
    <template v-if="!serviceLoading"> 
      <b-row>
        <b-col offset="2"
          cols="8">
          <div class="input-group mb-3">
            <input type="text"
              class="form-control"
              placeholder="Search by ID, Input String, URI, or CBOR"
              v-model="searchString"
              @change="handleSearchStringChange($event)"
              v-on:keyup.enter="handlePageChange(1)" />
            <div class="input-group-append">
              <button class="btn btn-outline-secondary"
                type="button"
                @click="handlePageChange(1)">
                Search
              </button>
              <button class="btn btn-outline-secondary" @click="reloadTranscoderLog()" data-toggle="tooltip" data-placement="top" title="Refresh Transcoder Log Table!"> &#x21bb;</button>
            </div>
          </div>
          <p>Select CBOR(s) to send to Agents tab</p>
          <div class="b-table">
            <b-table scr
              id="transcoder-table"
              striped
              bordered
              no-border-collapse
              :items="currentTranscoderLogs"
              :fields="fields"
              :per-page="pageSize"
              :sort-by.sync="sortField"
              :sort-desc.sync="sortDesc">
              <template #cell(selected)="{ item }">
                <div style="text-align: center;">
                    <b-form-checkbox :checked="item.selected"  @change="selectTranscoderLog($event, item)"></b-form-checkbox>
                </div>
              </template>
          <template #cell(cbor)="{ item }">
                <p v-b-tooltip.hover
                  title="send to agents page"
                  @click="sendTranscoderCode(item.cbor)">
                  {{ item.cbor }}
          </p>
            </template>
          </b-table>
          </div>
            <div class="d-flex float-right">
              <div>
              <button class="btn btn-outline-secondary"
                type="button"
                @click="sendTranscoderCodeSelected()">
                Send to Agents
              </button>
            </div>
              <div class="my-2 mx-3">
                Items per Page:
                <select v-model="pageSize"
                  @change="handlePageSizeChange($event)">
                  <option v-for="size in pageSizes"
                    :key="size"
                    :value="size">
                    {{ size }}
                  </option>
                </select>
              </div>
              
              <b-pagination v-model="page"
                class="m-0"
                :total-rows="count"
                :per-page="pageSize"
                aria-controls="transcoder-table"
                @change="handlePageChange"></b-pagination>
            </div>
          <!-- </div> -->
        </b-col>
        <br/>
      </b-row>
    </template>    
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";

export default {
  name: "Transcoder",
  data() {
    return {
      fields: [
        { key: "selected", label: "", sortable: false}, {key: "transcoder_log_id", sortable: true}, { key: "input_string", sortable: true }, { key: "parsed_as", sortable: true }, { key: "cbor", sortable: false }, { key: "ari", sortable: false }, { key: "uri", sortable: false },
      ],
      nodeMan: null,
      node: null,
      info: null,
      results: "",
      resultsAdd: "",
      raw: "",
      loading: true,
      errored: false,
      pageSizes: [5, 10, 20, 50, 100],
      sortField: "",
      sortDesc: false,
      selected_cbors:[]
    };
  },
  mounted() {
    const vm = this;
    vm.selected_cbors = [];
    vm.reloadTranscoderLog();
  },
  computed: {
    ...mapGetters("transcoder", {
      currentTranscoderLogs: "currentTranscoderLogs",
      count: "count",
      page: "page",
      pageSize: "pageSize",
      searchString: "searchString",
      serviceLoading: "loading",
    }),
  selectedLogs() {
      return this.currentTranscoderLogs.filter((log) => {
        return log.selected;
      });
    },
  },
  methods: {
    ...mapActions("transcoder", {
      reloadTranscoderLog: "reloadTranscoderLog",
      setPage: "setPage",
      setPageSize: "setPageSize",
      setSearchString: "setSearchString",
      updateEntry: "updateEntry",
    }),
    sendTranscoderCode(cbor) {
      this.$router.push({
        name: "Agents CBOR",
        params: { cbor: cbor },
      });
    },
    getLogIndexById(logId) {
      return this.currentTranscoderLogs.findIndex(log => log.transcoder_log_id === logId);
    },
    selectTranscoderLog(event, entry) {
      if (entry && event != entry.selected) {
        let entryUpdated = { ...entry };
        let entryIndex = this.getLogIndexById(entryUpdated.transcoder_log_id);
        entryUpdated.selected = event;
        this.updateEntry({ entryIndex, entry: entryUpdated });
        if(event){ // event true means add to list 
          this.selected_cbors.push(entry)
        }else{ // else it needs to be removed from list 
          this.selected_cbors = this.selected_cbors.filter(obj => ![entryUpdated.transcoder_log_id].includes(obj.transcoder_log_id));
        }

      }
    },
    sendTranscoderCodeSelected(){
      this.$router.push({
        name: "Agents CBORs",
        params: { cbors: this.selected_cbors },
      });
    },
    handlePageChange(value) {
      const vm = this;
      vm.setPage(value);
      vm.reloadTranscoderLog();
    },
    handlePageSizeChange(event) {
      const vm = this;
      vm.setPageSize(event.target.value);
      handlePageChange(1);
      reloadTranscoderLog();
    },
    handleSearchStringChange(event) {
      const vm = this;
      vm.setSearchString(event.target.value);
    },
  },
};
</script>

<style>
.b-table {
  max-height: calc(90vh - 300px);
  overflow-y: auto;
}

.page-item.active .page-link {
  border-color: var(--success);
  color: var(--success)
}
</style>

<!-- TODO changing from page to page is brokeski -->