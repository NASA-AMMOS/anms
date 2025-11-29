<template>
  <div class="help">
    <h1>Asynchronous Network Management System (ANMS) documentation</h1>
    <ul>
      <li><a href="https://github.com/NASA-AMMOS/anms/">Github</a></li>
      <li><a href="https://nasa-ammos.github.io/anms-docs/product-guide/html/index.html">Product Guide</a></li>
      <li><a href="https://nasa-ammos.github.io/anms-docs/user-guide/html/index.html">User Guide</a></li>
    </ul>

    <h1>Developer Resources</h1>
    <li><a :href="apiDocsUrl">ANMS REST API Docs</a></li>
    <li><a href="/grafana">Grafana</a> - This powers the 'Monitor' tab. Tip: Press the 'Esc' key in the Monitor tab after clicking within the display to exit Kiosk mode and access the full UI interface.</li>
    <li><a href="/adminer">Adminer (DB Management)</a> (if ANMS is configured with 'dev' profile</li>
    <ul>
    </ul>
    
    NOTE: This page is a placeholder. If you have suggestions to improve this page, or ANMS in general, share it with us on github.
  </div>
</template>
<script>
  import _ from 'lodash';

  export default {
    name: 'Help',
    data() {
      return {
        pageName: _.upperFirst(_.camelCase('help-page'))
      };
    },
  computed: {
    apiDocsUrl() {
      return `http://${window.location.hostname}:5555/docs`;
    }
  }
  };
</script>
