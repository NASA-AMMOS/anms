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
            </div>
          </div>
          <div class="b-table">
            <p>Select CBOR to send to Agents tab</p>
            <b-table scr
              id="transcoder-table"
              :items="currentTranscoderLogs"
              :fields="fields"
              :per-page="pageSize"
              hover
              bordered
              :sort-by.sync="sortField"
              :sort-desc.sync="sortDesc">
              <template #cell(cbor)="{ item }">
                <h5 v-b-tooltip.hover
                  title="send to agents page"
                  @click="sendTranscoderCode(item.cbor)">
                  {{ item.cbor }}
                </h5>
              </template>
            </b-table>
            <div class="d-flex float-right">
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
          </div>
        </b-col>
      </b-row>
    </template>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import { status_refresh_rate } from '@app/shared/constants';

export default {
  name: "Transcoder",
  data() {
    return {
      fields: [
        { key: "transcoder_log_id", sortable: true }, { key: "input_string", sortable: true }, { key: "parsed_as", sortable: true }, { key: "cbor", sortable: false }, { key: "ari", sortable: false }, { key: "uri", sortable: false },
      ],
      nodeMan: null,
      node: null,
      info: null,
      results: "",
      resultsAdd: "",
      data1: { data: "" },
      raw: "",
      loading: true,
      errored: false,
      pageSizes: [5, 10, 20, 50, 100],
      selected: null,
      transcoderWorkerId: "",
      sortField: "",
      sortDesc: false,
    };
  },
  mounted() {
    const vm = this;
    vm.reloadTranscoderLog();
    vm.transcoderWorkerId = setInterval(() => {
      console.log("Calling schedule transcoder Log refresh in App");
      vm.reloadTranscoderLog();
    }, status_refresh_rate);
  },
  beforeDestroy() {
    console.log("Clearing interval with id:", this.transcoderWorkerId);
    clearInterval(this.transcoderWorkerId);
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
  },
  methods: {
    ...mapActions("transcoder", {
      reloadTranscoderLog: "reloadTranscoderLog",
      setPage: "setPage",
      setPageSize: "setPageSize",
      setSearchString: "setSearchString",
    }),
    sendTranscoderCode(cbor) {
      this.$router.push({
        name: "Agents CBOR",
        params: { cbor: cbor },
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
      // vm.setPage(1);
      // vm.reloadTranscoderLog();
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
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

.page-item.active .page-link {
  border-color: var(--success);
  color: var(--success)
}
</style>
