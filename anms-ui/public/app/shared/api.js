/*
 * Copyright (c) 2023 The Johns Hopkins University Applied Physics
 * Laboratory LLC.
 *
 * This file is part of the Asynchronous Network Management System (ANMS).
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *     http://www.apache.org/licenses/LICENSE-2.0
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * This work was performed for the Jet Propulsion Laboratory, California
 * Institute of Technology, sponsored by the United States Government under
 * the prime contract 80NM0018D0004 between the Caltech and NASA under
 * subcontract 1658085.
 */
import Constants from '@app/shared/constants';
import axios from 'axios';
export default {
  data() {
    return {
    }
  },
  methods: {
    createAuthenticationHeader() {
      return {
        Authorization: 'Bearer ' + Constants.USER_DETAILS.token
      };
    },

    apiGetHello() {
      return axios.get(Constants.BASE_API_URL + 'hello');
    },

    apiGetUsers() {
      return axios.get(Constants.BASE_API_URL + 'users', {
        headers: this.createAuthenticationHeader()
      });
    },

    apiGetUserById(userId) {
      const id = encodeURIComponent(userId) ? encodeURIComponent(userId) : userId;
      return axios.get(Constants.BASE_API_URL + 'users/' + id, {
        headers: this.createAuthenticationHeader()
      });
    },

    apiGetUserByUsername(userName) {
      const name = encodeURIComponent(userName) ? encodeURIComponent(userName) : userName;
      console.info("name: ", name);
      return axios.get(Constants.BASE_API_URL + 'users/' + name, {
        headers: this.createAuthenticationHeader()
      });
    },

    apiCreateUserProfile(payload) {
      return axios.post(Constants.BASE_API_URL + 'users',
        { data: payload },
        {
          headers: this.createAuthenticationHeader()
        });
    },

    apiUpdateUserProfile(userName, payload) {
      return axios.put(Constants.BASE_API_URL + 'users/' + encodeURIComponent(userName),
        { data: payload },
        {
          headers: this.createAuthenticationHeader()
        })
    },

    apiPutUserProfile(userId, payload) {
      return axios.put(Constants.BASE_API_URL + 'users/' + encodeURIComponent(userId) + '/profile',
        { data: payload },
        {
          headers: this.createAuthenticationHeader()
        });
    },

    apiChangePassword(userId, payload) {
      return axios.post(Constants.BASE_API_URL + 'users/' + encodeURIComponent(userId) + '/password',
        { data: payload },
        {
          headers: this.createAuthenticationHeader()
        });
    },

    apiEnableUser(userId) {
      return axios.patch(Constants.BASE_API_URL + 'users/enable/' + encodeURIComponent(userId),
        {},
        {
          headers: this.createAuthenticationHeader()
        });
    },

    apiDisableUser(userId) {
      return axios.patch(Constants.BASE_API_URL + 'users/disable/' + encodeURIComponent(userId),
        {},
        {
          headers: this.createAuthenticationHeader()
        });
    },

    apiToggleUserMfa(userId, newValue) {
      return axios.patch(Constants.BASE_API_URL + 'users/mfa/' + encodeURIComponent(userId),
        { newState: newValue },
        {
          headers: this.createAuthenticationHeader()
        });
    },

    // agents api
    apiQueryForAgents(payload) {
      let params = {};
      if (payload.page) {
        params['page'] = encodeURIComponent(payload.page);
      }
      if (payload.size) {
        params['size'] = encodeURIComponent(payload.size);
      }
      if (payload.searchString === '') {
        return axios.get(Constants.BASE_API_URL + 'agents', { params: params });
      } else {
        const searchString = encodeURIComponent(payload.searchString);
        return axios.get(Constants.BASE_API_URL + `agents/search/${searchString}`, { params: params });
      }
    },

    apiGetAgent(agentId){
      return axios.get(Constants.BASE_API_URL +  `agents/id/${agentId}`)
    },

    // ari all
    apiQueryForARIs() {
      return axios.get(Constants.BASE_API_URL + 'build/ari/all');
    },

    // ari by id
    apiQueryForARIById(meta_id, obj_id) {
      return axios.get(Constants.BASE_API_URL + `build/ari/id/${meta_id}/${obj_id}`);
    },

    apiAmpVersion() {
      return axios.get(Constants.BASE_API_URL + 'nm/version');

    },

    apiDeregister(nodeEID) {
      return axios.get(Constants.BASE_API_URL+'nm/agents', nodeEID)
    },

    apiEntriesForReport(obj_agent_id, correlator_nonce) {
      return axios.get(Constants.BASE_API_URL+`report/entries/table/${obj_agent_id}/${correlator_nonce}`)
    },

    apiEntriesForReportTemplate(agentId){
      return axios.get(Constants.BASE_API_URL+`report/entry/name/${agentId}`)
    },

    apiEntriesForOperations(agentId){ // get the names of crude operations
      return axios.get(Constants.BASE_API_URL+`agents/parameter/name/${agentId}`)
    },

    apiPutCRUD(agentId, optId, params){
      return axios.put(Constants.BASE_API_URL+`agents/parameter/send/${agentId}/${optId}`,params)
    },

    apiBuildControl(nodeEID) {
      return axios.put(Constants.BASE_API_URL+'nm/agents', nodeEID)
        ,{ headers: {}, }
    },

    apiSendRawCommand(nodeEID, command) {
      return axios.put(Constants.BASE_API_URL+'nm/agents/eid/' + nodeEID + '/hex', {"data":command})
    },

    apiPrintAgentReports(nodeEID) {
      return axios.get(Constants.BASE_API_URL+'nm/agents/eid/' + nodeEID + '/reports/json')
    },

    apiClearAgentReports(nodeEID) {
      return axios.put(Constants.BASE_API_URL+'nm/agents/eid/' + nodeEID + '/clear_reports')
    },

    apiClearAgentTables(nodeEID) {
      return axios.put(Constants.BASE_API_URL+'nm/agents/eid/' + nodeEID + '/clear_tables')
    },

    apiWriteAgentReportstofile(nodeEID) {
      return axios.get(Constants.BASE_API_URL+'nm/agents', nodeEID)
    },

    apiPostAgent(node) {
      return axios.post(Constants.BASE_API_URL+'nm/agents', {'data':node})
    },

    apiGetAgents() {
      return axios.get(Constants.BASE_API_URL+'nm/agents/')
    },

    apiGetDbStatus() {
      console.log("Called getDbStatus!!!", Constants.BASE_API_URL);
      return axios.get(Constants.BASE_API_URL + 'sys_status/db_status')
    },

    apiGetAlerts() {
      return axios.get(Constants.BASE_API_URL +'alerts/incoming', {headers: {accept: 'application/json'}})
    },

    apiAcknowledgeAlerts(index) {
      return axios.put(Constants.BASE_API_URL +'alerts/acknowledge/'+index)
    },

    apiGetServiceStatus() {
      return axios.get(Constants.BASE_API_URL +'core/service_status', {headers: {accept: 'application/json'}})
    },

    apiPutTranscodedHex(cbor){
      return axios.put(Constants.BASE_API_URL+'transcoder/ui/incoming/'+ cbor +'/hex')
    },

    apiPutTranscodedString(ari){
      return axios.put(Constants.BASE_API_URL+'transcoder/ui/incoming/str', {"ari":ari})
    },

    apiGetTranscoderLogById(id) {
      return axios.get(Constants.BASE_API_URL+`transcoder/ui/log/id/${id}`);
    },

    apiQueryForTranscoderLog(payload) {
      let params = {};
      if (payload.page) {
        params['page'] = encodeURIComponent(payload.page);
      }
      if (payload.size) {
        params['size'] = encodeURIComponent(payload.size);
      }
      if (payload.searchString === '') {
        return axios.get(Constants.BASE_API_URL + 'transcoder/ui/log', { params: params });
      } else {
        const searchString = encodeURIComponent(payload.searchString);
        return axios.get(Constants.BASE_API_URL + `transcoder/ui/log/search/${searchString}`, { params: params });
      }
    },
  }
};
