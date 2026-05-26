export const environment = {
  UI_VERSION: '2.0.0-11-g80a27c5', // FIXME: hardcoded for now, where should this be populated from? and should version bump?
  VUE_APP_STATUS_REFRESH_RATE: 60000, // milliseconds

  BASE_API_URL: 'http://anms-test:8080',

  SERVICE_INFO: {
    names: [
      "adminer","anms-core","authnz","amp-manager",
      "postgres","redis","grafana","grafana-image-renderer"
    ],
    normal_status: ["running","healthy"],
    error_status: ["not-running","unhealthy"]
  }
};
