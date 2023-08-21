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
import { reactive } from 'vue'

export default {
  namespaced: true,
  state: {
    ARIs:[],
    keyARI:{},
    count: 0,
    searchString: '',
    loading: true,
  },

  getters: {
    ARIs(state){
      return state.ARIs
    },
    currentKeyARI(state){
      return state.keyARI
    },
    count(state){
      return state.count
    },
    searchString(state){
      return state.searchString
    },
    loading(state){
      return state.loading
    },
  },
  actions: {
    async reloadARIs({ state, commit }){
      await api.methods.apiQueryForARIs()
        .then(res => {
          
          commit('ARIs', res.data);
          commit('count' , res.data.total);
          commit('loading', false)
        })
    },
    setSearchString({state}, searchString){
      Vue.set(state, 'searchString', searchString);
    }
  },
  mutations: {
    ARIs(state, ARIs){
      state.ARIs = ARIs;
    },
    keyARI(state, keyARI){
      state.agent = keyARI;
    },
    count(state, count){
      state.count = count;
    },
    searchString(state, searchString){
      state.searchString = searchString;
    },
    loading(state, loading){
      state.loading = loading;
    }
  }
}
