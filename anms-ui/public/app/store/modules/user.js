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
import _ from 'lodash';

export default {
  namespaced: true,
  state: {
    userDetails: {
      username: "",
      email: "",
      first_name: "",
      last_name: "",
      created_at: ""
    },
    errorMsg: "",
    errorCode: 0,
    loading: false,
  },
  getters: {
    userDetails(state){
      return state.userDetails;
    },
    errorMsg(state) {
      return state.errorMsg;
    },
    errorCode(state) {
      return state.errorCode;
    },
    loading(state) {
      return state.loading;
    }
  },
  actions: {
    async getUserDetails({ state, commit }, userName){
      commit('loading', true);
      commit("errorMsg", "");
      commit("errorCode", 0);
      console.info("getUserDetails calling with username: ", userName);
      let sleep = (time) => new Promise((resolve) => setTimeout(resolve, time));
      api.methods.apiGetUserByUsername(userName).then(res => {
        console.info("getUserDetails response", res);
        if (res.data != null ) {
          sleep(1000).then(() => {
            commit('userDetails', res.data);
            commit('loading', false);
          });
        } else {
          throw `Userprofile of ${userName} does not exist in the database`;
        }
      })
      .catch(function (error) {
        // handle error
        console.error("getUserDetails error", error);
        let errMsg = `${error.response.statusText} - ${error.response.data} `;
        sleep(1000).then(() => {
          commit('loading', false);
          commit("errorMsg", errMsg);
          commit("errorCode", error.response.status);
        });
      });
    },
    async updateNewProfile({ state, commit}, newProfile) {
      commit('userDetails', newProfile);
      commit("errorMsg", "");
      commit("errorCode", 0);
    }
  },
  mutations: {
    userDetails(state, info){
      state.userDetails = {
        ...state.userDetails,
        ...info
      };
    },
    errorMsg(state, errorMsg){
      state.errorMsg = errorMsg;
    },
    errorCode(state, errorCode){
      state.errorCode = errorCode;
    },
    loading(state, loading){
      state.loading = loading;
    }
  }
}
