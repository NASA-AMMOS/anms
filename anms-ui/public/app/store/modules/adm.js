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
import api_adm from '@app/shared/api_adm';
import Vue from "vue";
import _ from 'lodash';

export default {
  namespaced: true,
  state: {
    adms: [],
    requestError: "",
    uploadErrors: [],
    uploadStatus: "",
    loading: true
  },
  getters: {
    adms(state){
      return state.adms
    },
    requestError(state){
      return state.requestError
    },
    uploadErrors(state){
      return state.uploadErrors
    },
    uploadStatus(state){
      return state.uploadStatus
    },
    loading(state) {
      return state.loading
    }
  },
  actions: {
    async getAdms({ state, commit }){
      commit('loading', true);
      commit('requestError', "");
      let sleep = (time) => new Promise((resolve) => setTimeout(resolve, time));
      api_adm.apiGetAdms().then(res => {
        if (_.isNil(res.data)) {
          throw new Error('Receiving no data from request')
        }
        sleep(1000).then(() => {
          commit('adms', res.data);
          commit('loading', false);
        })  
      })
      .catch(function (error) {
        sleep(1000).then(() => {
          commit('adms', []);
          commit('requestError', error);
          commit('loading', false);
        })
       
      });
    },
    async uploadAdm({ state, commit }, adm_file){
      //commit('loading', true);
      commit('requestError', "");
      commit('uploadErrors', []);
      //let sleep = (time) => new Promise((resolve) => setTimeout(resolve, time));
      await api_adm.apiUpdateAdm(adm_file).then(response => {
        let message = "";
        if (_.isNil(response.data)) {
          throw new Error('Receiving no data from request')
        }
        if (_.isNil(response) || _.isNil(response.data) || _.isNil(response.data.message)) {
          message = "Update success";
        } else {
          message = response.data.message;
        }
        commit('uploadStatus', message);
      })
      .catch(function (error) {
        const response = error.response
        let status = 500;
        let message = "";
        let errors = []; 
        if (_.isNil(response) || _.isNil(response.data) || _.isNil(response.data.message) || _.isNil(response.data.error_details)) {
          message = "Internal server error"
        } else {
          status = response.status;
          message = response.data.message;
          errors = response.data.error_details;
        }
        commit('requestError', `${status}: ${message}`);
        commit('uploadErrors', errors);
      });
    }
  },
  mutations: {
    adms(state, adms){
      state.adms = adms;
    },
    requestError(state, requestError){
      state.requestError = requestError;
    },
    uploadErrors(state, uploadErrors){
      state.uploadErrors = uploadErrors;
    },
    uploadStatus(state, uploadStatus){
      state.uploadStatus = uploadStatus;
    },
    loading(state, loading) {
      state.loading = loading;
    }
  }
}
