<template>
  <div v-cloak id="vue-app" class="d-flex flex-column h-100">
    <b-navbar toggleable="lg" type="light" variant="light" class="chronolens-navbar">
      <b-navbar-brand :to="{name:'home'}">AMMOS ANMS</b-navbar-brand>
      <b-navbar-brand :to="{name:'home'}">Version - {{uiversion}}</b-navbar-brand>
      <b-navbar-toggle target="nav-collapse"/>
      <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav class="ml-auto">
          <b-nav-item id="tour-app-usernavbutton" :to="{name: 'user'}">{{ userNameRemote }} <font-awesome-icon icon="fa-solid fa-user" /></b-nav-item>
          <b-nav-item id="tour-app-logoutnavbutton" :href="logoutResource">Logout <font-awesome-icon icon="fa-solid fa-arrow-right-from-bracket" />  </b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
    <b-container fluid class="d-flex flex-column flex-fill-100">
      <div>
        <b-row>
          <b-col cols="4" align="center" offset="4">
            <b-button-group size="sm" pills class="my-3">
              <b-button variant="outline-success" @click="$router.push('/monitor')">Monitor</b-button>
              <b-button variant="outline-success" @click="$router.push('/agents')">Agents</b-button>
              <!-- <b-button variant="outline-success" @click="$router.push('/messaging')">Messaging</b-button> -->
              <b-button variant="outline-success" @click="$router.push('/build')">Build</b-button>
              <b-button variant="outline-success" @click="$router.push('/status')">
                <template v-if="serviceError">
                  <span class="text-danger">Status</span>
                  <b-badge  v-if="hasUpdateError"  show variant="danger">error</b-badge>
                  <b-badge  v-else  show variant="danger">{{numberErrorServices}}</b-badge>
                  <b-spinner v-if="serviceLoading" variant="info" label="Loading..." type="grow" small></b-spinner>
                </template>
                <template v-else>
                  <span>Status</span>
                  <b-spinner v-if="serviceLoading" variant="info" label="Loading..." type="grow" small></b-spinner>
                  <b-badge  v-else  show variant="success">Good</b-badge>
                </template>
              </b-button>
              <b-button variant="outline-success" @click="$router.push('/adms')">Adms</b-button>
            </b-button-group>
          </b-col>
        </b-row>
      </div>
      <router-view/>
    </b-container>
    <div  v-for="(alert, index) in alerts" :key="index">
        <b-alert @dismissed="removeAlertAndUpdate(index)" :show="alert.visible" :variant="alert.type"  dismissible>ALERT#{{alert.id}}: {{alert.msg}}</b-alert>
      </div>
  </div>
</template>

<script>

  import Constants, {uiversion} from '@app/shared/constants';
  import api from '../shared/api';
  import _ from "lodash";
  import { mapGetters, mapActions } from "vuex";
  import {status_refresh_rate} from '@app/shared/constants';
  
  export default {
    mixins: [api],
    data() {
      return {
        version: 'v' + Constants.BASE_VERSION,
        uiversion: uiversion,
        logoutResource: '/authn/dologout.html',
        userName: Constants.USER_DETAILS.firstName + ' ' + Constants.USER_DETAILS.lastName,
        userNameRemote: Constants.USER_NAME_REMOTE,
        viewAdmin: _.intersection(Constants.USER_DETAILS.roles, ['ROLE_SUPER_ADMIN', 'ROLE_ADMIN']).length >= 1,
        showStubbedTabs: false,
        statusWorkerId: "",
        ariWorkerId: "",
        alerts:[]
      };
    },
    computed: {
      ...mapGetters("service_status", {
        updateError: "updateError",
        errorServices: "errorServices",
        normalServices: "normalServices",
        serviceLoading: "loading",
        alerts: "alerts"
      }),
      ...mapGetters("agents", {
        newAgentAlerts: "newAgentAlerts",
      }),
      ...mapGetters("build", {
      ARIs: "ARIs",
      count: "count",
      searchString: "searchString",
    }),
      hasUpdateError() {
        return this.updateError !== "";
      },
      serviceError() {
        return Object.keys(this.errorServices).length > 0 || this.hasUpdateError;
      },
      numberErrorServices() {
        return Object.keys(this.errorServices).length;
      }
    },
    mounted() {
      console.log("Environment variables: ", process.env);
      this.updateServiceStatus();
      this.statusWorkerId = setInterval(() => {
        console.log("Calling schedule status refresh in App");
        this.updateServiceStatus();
      }, status_refresh_rate);

      this.reloadARIs();
      this.ariWorkerId = setInterval(() => {
        console.log("Calling schedule ARI refresh in App");
        this.reloadARIs();
    }, status_refresh_rate);
    },
    beforeDestroy() {
      console.log("Clearing interval with id:", this.statusWorkerId);
      clearInterval(this.statusWorkerId);

      console.log("Clearing interval with id:", this.ariWorkerId);
      clearInterval(this.ariWorkerId);
    },
    methods: {
      removeAlertAndUpdate(index){
        this.removeAlert(index);
      },

      // removeAlert(index){
      //   this.alerts.delete(index);
      // },
      ...mapActions("service_status", {
        updateServiceStatus: "updateStatus",
        removeAlert: "setAlert"
      }),
      // ...mapActions("agents", {
      //   removeAlert: "removeAlert"
      // }),
      ...mapActions("build", {
      reloadARIs: "reloadARIs",
    }),

    },
    sockets: {
      connect: function () {
        const message = "Websocket connected.";
        console.debug(message);
        toastr.info(message);
      },
      disconnect: function () {
        const message = "Websocket disconnected. Please check your connection to the server.";
        console.debug(message);
        toastr.error(message);
      },
    },
    watch:{}
  };

</script>

<style lang="scss" type="text/scss">

  // Variables/Mixins Import
  @import '~@assets/styles/variables';
  // Global Layout Styles
  @import '~@assets/styles/base';

  // Import Bootstrap and theme
  // Web Font Path Issue: https://github.com/thomaspark/bootswatch/issues/55#issuecomment-298093182
  $web-font-path: 'data:text/css;base64,';
  @import '~bootstrap/scss/bootstrap';
  @import '~bootswatch/dist/darkly/bootswatch';
  // Bootstrap Vue Lib
  @import '~bootstrap-vue/src/index.scss';
  

  // Font Awesome Lib
  $fa-font-path:  '~@fortawesome/fontawesome-free/webfonts';
  @import '~@fortawesome/fontawesome-free/scss/fontawesome.scss';
  @import '~@fortawesome/fontawesome-free/scss/solid.scss';
  @import '~@fortawesome/fontawesome-free/scss/brands.scss';
  // Toastr Lib
  @import '~toastr/toastr';

  .status-error {
    color: red
  }
  .status-normal {
    color: green
  }
</style>
