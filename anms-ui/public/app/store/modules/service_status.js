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
import {service_info} from '@app/shared/constants';
import _ from 'lodash';

export default {
  namespaced: true,
  state: {
    errorServices: {},
    normalServices: {},
    updateError: "",
    loading: true,
    alerts: [],
    alertIds: [],
  },
  getters: {
    alerts(state){
      return state.alerts
    },
    errorServices(state){
      return state.errorServices
    },
    normalServices(state){
      return state.normalServices
    },
    updateError(state){
      return state.updateError
    },
    loading(state) {
      return state.loading
    }
  },
  actions: {
    async updateStatus({ state, commit }){
      commit('loading', true);
      commit('updateError', "");
      let sleep = (time) => new Promise((resolve) => setTimeout(resolve, time));

      api.methods.apiGetAlerts().then(res => {
        console.log("updateAlert response", res.data);
        commit('updateAlerts',res.data)

        // TODO rethink tracking alerts for multiple accounts
        // _.forEach(res.data, (alert) => {
        //   if( !state.alertIds.includes(alert.id)){
        //   commit('updateAlerts',alert)
        //   commit('updateAlertIds',alert.id)
        //  }
        // });
      });

      api.methods.apiGetServiceStatus().then(res => {
        console.log("updateStatus response", res.data);
        let jsonStatus = {};
        try{
          jsonStatus = JSON.parse(res.data); //?Asomehow axios does not parse the Json response
        } catch (e){
          console.error(e)
          jsonStatus = {};
        }

        console.log("updateStatus called", jsonStatus);
        //Filter out status
        let errorServices = {};
        let normalServices = {};

        _.forEach(service_info.names, (name) => {
          if (jsonStatus[name] === undefined) {
            errorServices[name] = service_info.error_status[0];
          }
          else if (!service_info.normal_status.includes(jsonStatus[name])) {
            errorServices[name] = jsonStatus[name];
          }
          else {
            normalServices[name] = jsonStatus[name];
          }
        });
        console.log("normal services: ", normalServices);
        console.log("error services: ", errorServices);

        sleep(1000).then(() => {
          commit('normalServices', normalServices);
          commit('errorServices', errorServices);
          commit('loading', false);
        })

      })
      .catch(function (error) {
        // handle error
        console.error("update status error", error);
        console.info("error obj:", error);
        sleep(1000).then(() => {
          commit('normalServices', {});
          commit('errorServices', {});
          commit('updateError', error);
          commit('loading', false);
        })

      });
    },
    setAlert({ state, commit}, index ){
      api.methods.apiAcknowledgeAlerts(index);
      // commit('removeAlert', index);
    },
  },
  mutations: {
    updateAlerts(state, alert){
      state.alerts = alert;
    },
    updateAlertIds(state, alertId){
      state.alertIds.push(alertId);
    },
    removeAlert(state, index){
      // set hidden to true
      // let current_alert = state.alerts[index]
      // current_alert.visible = false
      // state.alerts[index] = current_alert;
    },
    errorServices(state, errorServices){
      state.errorServices = errorServices;
    },
    normalServices(state, normalServices){
      state.normalServices = normalServices;
    },
    updateError(state, updateError){
      state.updateError = updateError;
    },
    loading(state, loading) {
      state.loading = loading;
    }
  }
}
