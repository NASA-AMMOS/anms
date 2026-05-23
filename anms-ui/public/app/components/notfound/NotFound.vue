<template>
  <div class="notfound">
    <h1>{{ pageName }}</h1>
    This is not the page you are looking for.
  </div>
</template>
<script>
  import _ from 'lodash';

  export default {
    name: 'Not found',
    data() {
      return {
        pageName: "Page Not Found"
      };
    }
  };
</script>
