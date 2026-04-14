import {environment} from '../../environments/environment';

export const Constants = {
  uiversion: environment.VUE_APP_UI_VERSION,
  status_refresh_rate: environment.VUE_APP_STATUS_REFRESH_RATE, //ms -the rate of updating services' status
  service_info: environment.SERVICE_INFO,
  // FIXME: see index.html on how these are initialized
  BASE_API_URL: 'http://anms-test:8040',
  USER_DETAILS: {
    token: ''
  }
}
