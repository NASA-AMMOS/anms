export const environment = {
  VUE_APP_UI_VERSION: "VUE_APP_UI_VERSION_TEMPLATE",
  VUE_APP_STATUS_REFRESH_RATE: 60000, // milliseconds
  SERVICE_INFO: {
    names: [
      "adminer","anms-core","authnz","amp-manager",
      "postgres","redis","grafana","grafana-image-renderer"
    ],
    normal_status: ["running","healthy"],
    error_status: ["not-running","unhealthy"]
  }
};
