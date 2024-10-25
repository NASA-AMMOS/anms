<template>
  <div class="user d-flex flex-column flex-fill-100">
    <b-nav id="tour-user-profilenav"
      class="user-tabs"
      tabs>
      <b-nav-item :to="{ name: 'userProfile' }">Profile</b-nav-item>
      <b-nav-item v-if="isAdmin"
        :to="{ name: 'userAdministration' }">Administration</b-nav-item>
    </b-nav>
    <router-view />
  </div>
</template>

<script>

import _ from 'lodash';
import Constants from '@app/shared/constants';

export default {
  name: 'User',
  data() {
    return {
    };
  },
  computed: {
    isAdmin: function () {
      const userRoles = Constants.USER_DETAILS.roles;
      const userPermissions = Constants.USER_DETAILS.permissions;
      let isAdmin = true;// _.intersection(userRoles, ['ROLE_SUPER_ADMIN', 'ROLE_ADMIN']).length >= 1;
      let hasPermissions = _.intersection(userPermissions, ['PERMISSION_ALL', 'PERMISSION_ADD_USER', 'PERMISSION_EDIT_USER']).length >= 1;
      return isAdmin || hasPermissions;
    }
  }
};
</script>

<style lang="scss" scoped>
@import '@/assets/styles/_variables.scss';

.user-tabs {
  // No gutters from the main container since we're don't want a row/column grid gutters
  // For Grids with gutters, re-initialize a new container on the sub-element
  margin-right: -$grid-gutter-width / 2;
  margin-left: -$grid-gutter-width / 2;
}
</style>
