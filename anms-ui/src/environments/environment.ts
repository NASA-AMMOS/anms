export const environment = {
  UI_VERSION: 'unknown', // NOTE: Auto-updated at build-time by modify_version.sh
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
