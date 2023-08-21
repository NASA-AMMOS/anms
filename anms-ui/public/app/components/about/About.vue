<template>
  <div class="about">
    <h1>{{ pageName }}</h1>
  </div>
</template>
<script>
  import _ from 'lodash';

  export default {
    name: 'About',
    data() {
      return {
        pageName: _.upperFirst(_.camelCase('about-page'))
      };
    }
  };
</script>
