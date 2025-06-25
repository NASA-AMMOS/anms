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
                  variant="primary"> {{ agent.agent_id_string }} </b-badge>
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
              :disabled="this.loading"
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
        // submitRawCommand2Agents();
        
      }else{
        this.ariString = result;
        // submitTranscodedString();
      }
      
    },
    submitTranscodedString() {
      this.loading = true;
      this.sendButtonText = "Submitting ARI String";
      // short circuit submitting command if already cbor 
      if(this.ariCBOR){
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
            this.loading = false;
            this.closeModal();
            this.ariCBOR = null;
            this.ariString=null;
           } 
          else {
            this.ariCBOR = response.data.cbor;
            this.submitRawCommand2Agents();
          }
        })
        .catch((error) => {
          console.log(error);
          toastr.error(error.response.data);
        });
    },
    submitRawCommand2Agents() {
      this.sendButtonText = "Sending ARI CBOR to Agent(s)";
      this.agents.forEach((agent) => {
        api.methods
          .apiSendRawCommand(agent.agent_id_string, this.ariCBOR)
          .then((response) => {
            if (response.status == 200) {
              toastr.success(`Submitted ARI CBOR to agent ${agent.agent_id_string}`);
            }
          })
          .catch((error) => {
            console.error(error);
            toastr.error(error.response.data);
          })
      });
      this.loading = false;
      this.closeModal();
      this.ariCBOR = null;
      this.ariString=null;
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
