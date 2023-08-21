<template>
  <b-row class="home h-100" align-v="center" align-h="center" style="margin-bottom: 0.35em">
    <b-col cols="12" sm="8" md="6" lg="6" xl="6">
      <div class="text-center">
        <h1 class="display-3 lead">Welcome to AMMOS ANMS</h1>
      </div>
    </b-col>
  </b-row>
</template>

<script>

  import api from '@app/shared/api';
  import _ from 'lodash';

  export default {
    name: 'Home',
    mixins: [api],
    data() {
      return {
        pageName: _.upperFirst(_.camelCase('home-page')),
        apiData: null,
      };
    },
    mounted() {
      this.apiGetHello()
        .then(response => {
          this.apiData = response.data.text + ' at ' + this.$moment.utc().format();
        })
        .catch(err => {
          this.$log.error(err);
        });
    }
  };

</script>

<style lang="scss" scoped>

</style>
