<template>
  <div>
    <b-modal id="manageAgentModal"
      ref="manageAgentModal"
      size="xl"
      @hide="closeModal"
      title="Manage Agents"
      hide-footer>
      <div v-if="agents">
        <b-row>
          <b-col cols="3">
            <div class="agent-info">
              <div v-for="agent in agents">
                <b-badge pill
                  variant="primary"> {{ agent.agent_endpoint_uri }} </b-badge>
              </div>
            </div>
            <div v-if="this.ariString">
              <h5>ARI Text:</h5>
              <p style="overflow-wrap: break-word;">{{ ariString }}</p>
            </div>
            <div v-if="this.ariCBOR">
              <h5>ARI CBOR:</h5>
              <p style="overflow-wrap: break-word;">{{ ariCBOR }}</p>
            </div>
            <b-button block
              variant="outline-success"
              :disabled="!this.ready"
              @click="submitTranscodedString">
              <b-spinner v-if="this.loading"
                small
                type="grow"> </b-spinner>
              {{ this.sendButtonText }}
            </b-button>
          </b-col>
          <b-col cols="9">
            <build :cbor="cbor" :agentModal=true @updateResult="updateResults($event)"></build>
          </b-col>
        </b-row>
      </div>
    </b-modal>
  </div>
</template>
<script>
import api from "../../../shared/api.js";
import Build from "../builder/Build.vue";
import toastr from "toastr";
export default {
  name: "AgentsManageModal",
  components: { Build },
  data() {
    return {
      ariString: undefined,
      ariCBOR: undefined,
      sendButtonText: "Send",
      loading: false,
      ready: false,
      transcoderLogId: undefined,
    }
  },
  props: {
    showModal: {
      type: Boolean,
      default: false,
    },
    agents: {
      type: Array,
      default: [],
    },
    cbor: {
      type: String,
      default: undefined
    },
    cbors: {
      type: Array,
      default: []
    }

  },
  watch: {
    showModal(newValue, _) {
      if (newValue === true) {
        this.show();
      }
    }
  },
  methods: {
    show() {
      this.ready = false;
      // if cbors set set cbor to the string version for display
      if(this.cbors.length > 0){
        let cbor_string = this.cbors.map(item => item.uri); 
        this.cbor = cbor_string.join(', ');
      }
      this.$refs['manageAgentModal'].show();
    },
    closeModal() {
      this.$emit("close");
      this.$refs['manageAgentModal'].hide();
      this.ariCBOR = undefined;
      this.ariString = undefined;
    },
    updateResults(result) {
      if(result.startsWith("0x")){
        this.ariCBOR = result;
      }else{
        this.ariString = result;
      }
      this.ready = true;
    },
    submitTranscodedString() {
      this.loading = true;
      this.sendButtonText = "Submitting ARI String";
      //if cbors set send each cbor in array
      if(this.cbors.length > 0){
        this.cbors.forEach(cbor => {
          this.loading = true;
          this.sendButtonText = "Submitting ARI String";
          this.ariCBOR = cbor.cbor;
          this.submitRawCommand2Agents();
        });
      }
      // short circuit submitting command if already cbor 
      else if(this.ariCBOR){
        this.submitRawCommand2Agents();
      }
      else{
        api.methods
          .apiPutTranscodedString(this.ariString)
          .then((response) => {
            this.transcoderLogId = response.data.id;
            this.sendButtonText = "Transcoding ARI String";
            this.queryTranscoderLog();
          })
          .catch((error) => {
            console.error(error);
            toastr.error(error.response.data);
            this.afterError();
          });
      }
    },
    queryTranscoderLog() {
      api.methods
        .apiGetTranscoderLogById(this.transcoderLogId)
        .then((response) => {
          if (response.data.parsed_as == "pending") {
            setTimeout(() => this.queryTranscoderLog(), 8000);
          } else if(response.data.parsed_as == "ERROR") {
            console.log(`Error translating transcoder log ID: ${this.transcoderLogId}! See transcoder log table for details`);
            toastr.error(`Error translating transcoder log ID: ${this.transcoderLogId}! See transcoder log table for details`);
            this.afterError();
           } 
          else {
            this.ariCBOR = response.data.cbor;
            this.submitRawCommand2Agents();
          }
        })
        .catch((error) => {
          console.log(error);
          toastr.error(error.response.data);
          this.afterError();
        });
    },
    afterError(){
      this.loading = false;
      this.sendButtonText = "Submit";
      this.ready = false;
      this.ariCBOR = null;
      this.ariString=null;
      this.closeModal();
    },
    submitRawCommand2Agents() {
      this.sendButtonText = "Sending ARI CBOR to Agent(s)";
      this.agents.forEach((agent) => {
        api.methods
          .apiSendRawCommand(agent.agent_endpoint_uri, this.ariCBOR)
          .then((response) => {
            if (response.status == 200) {
              toastr.success(`Submitted ARI CBOR to agent ${agent.agent_endpoint_uri}`);
            }
          })
          .catch((error) => {
            console.error(error);
            toastr.error(error.response.data);
          })
      });
    this.afterError();
    },
  },
}
</script>
<style scoped>
.agent-info {
  padding: 16px;
  margin-bottom: 16px;
  background-color: grey;
  display: inline-block;
  border-radius: 10px;
  color: black;
  width: 100%;
}

.button-form-center {
  text-align: center;
}
</style>
