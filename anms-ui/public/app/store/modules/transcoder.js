/*
 * Copyright (c) 2023 The Johns Hopkins University Applied Physics
 * Laboratory LLC.
 *
 * This file is part of the Asynchronous Network Managment System (ANMS).
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
    TranscoderLogs:[],
    TranscoderLog:{},
    count: 0,
    page: 1,
    pageSize: 10,
    searchString: '',
    loading: true,
  },
  getters: {
    currentTranscoderLogs(state){
      return state.TranscoderLogs
    },
    currentTranscoderLog(state){
      return state.TranscoderLog
    },
    count(state){
      return state.count
    },
    page(state){
      return state.page
    },
    pageSize(state){
      return state.pageSize
    },
    searchString(state){
      return state.searchString
    },
    loading(state) {
      return state.loading
    }
  },
  actions: {
    async reloadTranscoderLog({ state, commit }){
      commit('loading', true);
      const params = { 'searchString': state.searchString, 'page': state.page, 'size': state.pageSize }
      api.methods.apiQueryForTranscoderLog(params)
        .then(res => {
          commit('TranscoderLogs', res.data.items);
          commit('count' , res.data.total);
                     
            commit('loading', false);
          
        }).catch( error => {
          // handle error
          console.error("Transcoder error", error);
          console.info("error obj:", error);
          
            commit('loading', false);
        });
    },
    setPage({state}, page){
      Vue.set(state, 'page', page);
    },
    setPageSize({state}, pageSize){
      Vue.set(state, 'pageSize', pageSize);
    },
    setTranscoderId({state}, transcoderLogId){
      Vue.set(state, 'transcoderLogId', transcoderLogId);
    },
    setSearchString({state}, searchString){
      Vue.set(state, 'searchString', searchString);
    }
  },
  mutations: {
    TranscoderLogs(state, TranscoderLogs){
      state.TranscoderLogs = TranscoderLogs;
    },
    TranscoderLog(state, TranscoderLog){
      state.TranscoderLog = TranscoderLog;
    },
    count(state, count){
      state.count = count;
    },
    page(state, page){
      state.page = page;
    },
    pageSize(state, pageSize){
      state.pageSize = pageSize;
    },
    searchString(state, searchString){
      state.searchString = searchString;
    },
    loading(state, loading) {
      state.loading = loading;
    }
  }
}
