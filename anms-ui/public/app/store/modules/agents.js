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
import api from '../../shared/api';
import Vue from "vue";

export default {
  namespaced: true,
  state: {
    agents: [],
    alerts: [],
    agent: {},
    rptt: [],
    operations: [],
    count: 0,
    page: 1,
    pageSize: 10,
    searchString: ''
  },
  getters: {
    currentAgents(state) {
      return state.agents
    },
    currentAgent(state) {
      return state.agent
    },
    newAgentAlerts(state) {
      return state.alerts
    },
    rptt(state) {
      return state.rptt
    },
    operations(state){
      return state.operations
    }
    ,
    count(state) {
      return state.count
    },
    page(state) {
      return state.page
    },
    pageSize(state) {
      return state.pageSize
    },
    searchString(state) {
      return state.searchString
    }
  },
  actions: {
    async reloadAgents({ state, commit }) {
      const params = { 'searchString': state.searchString, 'page': state.page, 'size': state.pageSize }
      api.methods.apiQueryForAgents(params)
        .then(res => {
          commit('agents', res.data.items);
          commit('count', res.data.total);
        })
    },
    addAlert({state}, alert){
    state.alerts.push(alert)

    },
    setPage({ state }, page) {
      Vue.set(state, 'page', page);
    },
    setPageSize({ state }, pageSize) {
      Vue.set(state, 'pageSize', pageSize);
    },
    async reloadAgent({ state, commit }) {
      commit('agent', {})
      api.methods.apiGetAgent(state.agentId)
        .then(res => {

          api.methods.apiEntriesForReportTemplate(res.data.agent_id_string)
            .then(res => {
              commit('rptt', res.data)
            }).catch(error => {
              // handle error
              console.error("get agent rptt error", error);
              console.info("error obj:", error);
              commit('rptt', [])
            });
          api.methods.apiEntriesForOperations(res.data.agent_id_string)
            .then(res => {
              commit('operations', res.data)
            }).catch(error => {
              // handle error
              console.error("get agent CRUD operations error", error);
              console.info("error obj:", error);
              commit('operations', [])
            });
          commit('agent', res.data);
        })
    },
    setAgentId({ state }, agentId) {
      Vue.set(state, 'agentId', agentId);
    },
    setSearchString({ state }, searchString) {
      Vue.set(state, 'searchString', searchString);
    },
    removeAlert( { state }, index ) {
      state.alerts.delete(index);
    }
  },
  mutations: {
    agents(state, agents) {
      state.agents = agents;
    },
    agent(state, agent) {
      state.agent = agent;
    },
    alerts(state, alerts){
      state.alerts = alerts;
    },
    rptt(state, rptt) {
      state.rptt = rptt
    },
    operations(state, operations){
      state.operations = operations
    },
    count(state, count) {
      state.count = count;
    },
    page(state, page) {
      state.page = page;
    },
    pageSize(state, pageSize) {
      state.pageSize = pageSize;
    },
    searchString(state, searchString) {
      state.searchString = searchString;
    }
  }
}
