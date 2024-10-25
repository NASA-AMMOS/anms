  <template>
    <b-row class="mt-3">
      <b-col cols="12">

        <br />

        <div class="users">

          <b-modal id="modal-add-or-update-user"
            ref="addOrUpdateUserModal"
            :title="userModal.title"
            @hidden="resetUserModal"
            @ok.prevent="handleUserSubmit">
            <form ref="addOrUpdateUserForm"
              @submit.stop.prevent="handleUserSubmit">
              <b-form-group :state="isUpdateModal ? null : userModal.formState.username"
                label="Username"
                label-for="user-name-input"
                invalid-feedback="Username is required">
                <b-form-input id="user-name-input"
                  v-model="userModal.form.username"
                  :state="isUpdateModal ? null : userModal.formState.username"
                  :disabled="isUpdateModal"
                  required
                  autocomplete="username" />
              </b-form-group>
              <b-form-group :state="userModal.formState.firstName"
                label="First Name"
                label-for="first-name-input"
                invalid-feedback="First name is required">
                <b-form-input id="first-name-input"
                  v-model="userModal.form.firstName"
                  :state="userModal.formState.firstName"
                  required />
              </b-form-group>
              <b-form-group :state="userModal.formState.lastName"
                label="Last Name"
                label-for="last-name-input"
                invalid-feedback="Last name is required">
                <b-form-input id="last-name-input"
                  v-model="userModal.form.lastName"
                  :state="userModal.formState.lastName"
                  required />
              </b-form-group>
              <b-form-group :state="userModal.formState.email"
                label="Email"
                label-for="email-input"
                invalid-feedback="Email address is required">
                <b-form-input id="email-input"
                  v-model="userModal.form.email"
                  :state="userModal.formState.email"
                  required />
              </b-form-group>
              <b-form-group :state="userModal.formState.organization"
                label="Organization"
                label-for="user-organization-input"
                invalid-feedback="Organization is required">
                <b-form-input id="user-organization-input"
                  v-model="userModal.form.organization"
                  :state="userModal.formState.organization"
                  required />
              </b-form-group>
              <b-form-group :state="userModal.formState.roles"
                label="Roles"
                label-for="user-roles-input"
                invalid-feedback="At least one role is required">
                <b-form-select id="user-roles-input"
                  v-model="userModal.form.roles"
                  :options="userRoles"
                  multiple
                  :select-size="4"
                  required />
              </b-form-group>
              <b-form-group :state="userModal.formState.permissions"
                label="Permissions"
                label-for="user-permissions-input">
                <b-form-select id="user-permissions-input"
                  v-model="userModal.form.permissions"
                  :options="userPermissions"
                  multiple
                  :select-size="4" />
              </b-form-group>
              <b-form-group>
                <b-button size="sm"
                  @click="userModal.form.permissions = []">Clear Permissions</b-button>
              </b-form-group>
              <div v-if="userModal.title === 'Add New User'">
                <b-form-group label="Password"
                  label-for="user-password-input"
                  :state="userModal.formState.password"
                  invalid-feedback="Password is required, must match repeat, and be longer than 7 characters">
                  <b-input-group>
                    <b-form-input id="user-password-input"
                      v-model="userModal.form.password"
                      :type="userModal.passwordRenderType"
                      :state="userModal.formState.password"
                      required
                      autocomplete="new-password"
                      @input="verifyPasswords" />
                    <b-input-group-append>
                      <b-button variant="light"
                        @click="togglePasswordView">
                        <span v-show="userModal.passwordRenderType === 'password'"
                          class="fa fa-eye"></span>
                        <span v-show="userModal.passwordRenderType !== 'password'"
                          class="fa fa-eye-slash"></span>
                      </b-button>
                    </b-input-group-append>
                  </b-input-group>
                </b-form-group>
                <b-form-group :state="userModal.formState.passwordRepeat"
                  label="Repeat Password"
                  label-for="user-password-repeat-input"
                  invalid-feedback="Repeated Password is required and must match above password.">
                  <b-form-input id="user-password-repeat-input"
                    v-model="userModal.form.passwordRepeat"
                    :type="userModal.passwordRenderType"
                    :state="userModal.formState.passwordRepeat"
                    :disabled="userModal.form.password === null"
                    required
                    autocomplete="new-password"
                    @input="verifyPasswords" />
                </b-form-group>
              </div>
            </form>
            <template #modal-footer="{ ok, cancel }">
              <!-- Emulate built in modal footer ok and cancel button actions -->
              <b-button size="lg"
                variant="success"
                @click="ok()">
                OK
              </b-button>
              <b-button size="lg"
                variant="danger"
                @click="cancel()">
                Cancel
              </b-button>
            </template>
          </b-modal>

          <div id="tour-user-admin-add-users"
            class="float-left">
            <b-button variant="primary"
              size="sm"
              @click="openUserModal(modalActions.ADD, null)">
              <span class="fa fa-plus"></span>
              <span>&nbsp;</span>
              <span>Users</span>
            </b-button>
          </div>

          <div id="tour-useradmin-toggledisabledusers"
            class="float-right">
            <b-button v-if="usersSelected.length > 0"
              v-b-modal.modal-assign-user
              style="margin-right: 0.35em"
              size="sm">Assign
              Users</b-button>
            <b-button v-else
              style="margin-right: 0.35em"
              disabled
              size="sm">Assign Users</b-button>
            <b-button v-if="!showDisabledUsers"
              size="sm"
              :disabled="!hasDisabledUsers"
              @click="toggleDisplayedUsers">
              Show Disabled
            </b-button>
            <b-button v-else
              size="sm"
              @click="toggleDisplayedUsers">
              Hide Disabled
            </b-button>
          </div>

          <div class="clearfix"
            style="margin-bottom: 0.35em"></div>

          <b-table ref="userTable"
            id="tour-useradmin-userstable"
            class="user-mgmt-table"
            responsive
            striped
            hover
            :fields="userFields"
            :items="displayedUsers"
            selectable
            select-mode="range"
            selected-variant="outline-light"
            @row-selected="userRowSelected">
            <template v-slot:cell(actions)="data">
              <b-button size="sm"
                style="margin-right: 0.35em"
                @click="openUserModal(modalActions.EDIT, data.item.id)">
                Edit User
              </b-button>
              <b-button v-if="data.item.isEnabled"
                variant="danger"
                size="sm"
                style="margin-right: 0.35em"
                :disabled="isFinalAdmin(data.item.roles)"
                @click="disableUser(data.item.id)">
                Disable
              </b-button>
              <b-button v-else
                variant="success"
                size="sm"
                style="margin-right: 0.35em"
                @click="enableUser(data.item.id)">
                Enable
              </b-button>
              <b-button type="button"
                :variant="data.item.isMfaEnabled ? 'danger' : 'warning'"
                size="sm"
                style="margin-right: 0.35em"
                @click="toggleMFAStatus(data.item)">
                <span v-text="data.item.isMfaEnabled ? 'Disable MFA' : 'Enable MFA'"></span>
              </b-button>
            </template>
          </b-table>

        </div>

      </b-col>
    </b-row>
  </template>

<script>

import _, { size } from 'lodash';
import toastr from 'toastr';
import moment from 'moment';
import api from '@app/shared/api';

// Constants
const IS_ENABLED_FIELD = 'isEnabled';

// Preliminary State Variables
const modalActions = {
  ADD: 'add',
  EDIT: 'update',
  CLONE: 'clone'
};

const SYSTEM_ROLES = [
  { value: 0, text: 'ROLE_SUPER_ADMIN' },
  { value: 1, text: 'ROLE_ADMIN' },
  { value: 2, text: 'ROLE_USER' }
];

const SYSTEM_PERMISSIONS = [
  { value: 0, text: 'PERMISSION_ALL' },
  { value: 100, text: 'PERMISSION_ADD_USER' },
  { value: 200, text: 'PERMISSION_EDIT_USER' },
  { value: 300, text: 'PERMISSION_VIEW_USER' }
];

const userModalFields = {
  title: null,
  passwordRenderType: 'password',
  form: {
    id: null,
    username: null,
    firstName: null,
    lastName: null,
    password: null,
    passwordRepeat: null,
    email: null,
    organization: null,
    roles: [],
    permissions: []
  },
  formState: {
    id: null,
    username: null,
    firstName: null,
    lastName: null,
    password: null,
    passwordRepeat: null,
    email: null,
    organization: null,
    roles: [],
    permissions: []
  }
};
const userTableFields = [
  { key: 'username', sortable: true },
  { key: 'firstName', sortable: true },
  { key: 'lastName', sortable: true },
  { key: 'email', sortable: true },
  { key: 'organization', sortable: true },
  'actions'
];

export default {
  name: 'UserAdmin',
  mixins: [api],
  data() {
    return {

      users: [],
      displayedUsers: [],
      hasDisabledUsers: false,
      showDisabledUsers: false,

      usersSelected: [],

      isUpdateModal: false,
      isCloneModal: false,
      modalActions: modalActions,
      userModal: _.cloneDeep(userModalFields),
      userRoles: SYSTEM_ROLES,
      userPermissions: SYSTEM_PERMISSIONS,

      userFields: userTableFields,
    };
  },
  computed: {
  },
  created() {

    const vm = this;

    toastr.options = { closeButton: true };

    const initUsers = vm.getUsers();

    Promise.all([
      initUsers
    ]);

  },
  mounted() {
  },
  methods: {

    // <editor-fold desc="Users">

    getUsers() {
      const vm = this;
      return vm.apiGetUsers()
        .then(res => {
          _.forEach(res.data, (user) => {
            user.organization = _.get(user, 'details.organization', null);
          });
          vm.users = res.data;
          vm.displayedUsers = (vm.showDisabledUsers === true) ? vm.users : _.filter(vm.users, IS_ENABLED_FIELD);
          vm.hasDisabledUsers = _.size(vm.users) > _.size(_.filter(vm.users, IS_ENABLED_FIELD));
          return res;
        })
        .catch(err => {
          vm.$log.error(err);
          return err;
        });
    },

    userRowSelected(items) {
      const vm = this;
      const defaultRole = _.head(vm.projectRoles);
      _.forEach(items, function (user) {
        user.groupRole = defaultRole.id;
      });
      vm.usersSelected = items;
    },

    toggleDisplayedUsers() {
      const vm = this;
      vm.showDisabledUsers = !vm.showDisabledUsers;
      vm.displayedUsers = (vm.showDisabledUsers === true) ? vm.users : _.filter(vm.users, IS_ENABLED_FIELD);
    },

    openUserModal(action = modalActions.ADD, userId = null) {
      const vm = this;
      if (action === modalActions.ADD) {
        vm.isUpdateModal = false;
        vm.isCloneModal = false;
        vm.userModal.title = 'Add New User';
      } else if (action === modalActions.EDIT) { // populates modal with current object's values
        vm.isUpdateModal = true;
        vm.isCloneModal = false;
        vm.userModal.title = 'Edit User';
        const userObj = _.find(vm.users, { id: userId });
        _.forEach(vm.userModal.form, (v, k) => {
          vm.userModal.form[k] = userObj[k];
          vm.userModal.formState[k] = true;
        });
      }
      vm.$bvModal.show('modal-add-or-update-user');
    },

    resetUserModal() {
      this.userModal = _.cloneDeep(userModalFields);
    },

    enableUser(userId) {
      const vm = this;
      const userObj = _.find(vm.users, { id: userId });
      if (!userObj) {
        return;
      }
      // eslint-disable-next-line template-curly-spacing
      return vm.$bvModal.msgBoxConfirm(`Are you sure you want to enable user ${userObj.username}?`, {
        title: 'Enable User',
        buttonSize: 'sm',
        okVariant: 'warning',
        okTitle: 'Yes',
        cancelTitle: 'No',
        headerClass: 'p-2 border-bottom-0',
        footerClass: 'p-2 border-top-0',
        centered: true
      })
        .then((confirm) => {
          // eslint-disable-next-line prefer-promise-reject-errors
          return confirm ? Promise.resolve() : Promise.reject('User Canceled');
        })
        .then(() => {
          return vm.apiEnableUser(userId);
        })
        .then(() => {
          return vm.getUsers();
        })
        .catch(err => {
          vm.$log.error(err);
          return err;
        });
    },

    disableUser(userId) {
      const vm = this;
      const userObj = _.find(vm.users, { id: userId });
      if (!userObj) {
        return;
      }
      // eslint-disable-next-line template-curly-spacing
      return vm.$bvModal.msgBoxConfirm(`Are you sure you want to disable user ${userObj.username}?`, {
        title: 'Disable User',
        buttonSize: 'sm',
        okVariant: 'danger',
        okTitle: 'Yes',
        cancelTitle: 'No',
        headerClass: 'p-2 border-bottom-0',
        footerClass: 'p-2 border-top-0',
        centered: true
      })
        .then((confirm) => {
          // eslint-disable-next-line prefer-promise-reject-errors
          return confirm ? Promise.resolve() : Promise.reject('User Canceled');
        })
        .then(() => {
          return vm.apiDisableUser(userId);
        })
        .then(() => {
          return vm.getUsers();
        })
        .catch((err) => {
          vm.$log.error(err);
          return err;
        });
    },

    handleUserSubmit() {

      const vm = this;

      // Exit when the form isn't valid
      const isFormValid = vm.$refs.addOrUpdateUserForm.checkValidity();
      if (!isFormValid) {
        _.forEach(vm.userModal.form, (v, k) => {
          vm.userModal.formState[k] = !_.isEmpty(v);
        });
        return;
      }

      // Create Payload
      const userId = vm.userModal.form.id; // copy the id
      const payloadObj = _.clone(vm.userModal.form);
      delete payloadObj.id;

      // Submit Request
      let promise;
      if (userId === null) {
        // Add
        promise = vm.apiPostUser(payloadObj)
          .then(() => {
            toastr.success('Created User', 'Success');
            return vm.getUsers();
          })
          .catch(err => {
            vm.$log.error(err);
            toastr.error('Error Saving User', 'Error');
            return err;
          });
      } else {
        // Edit
        promise = vm.apiPutUser(userId, payloadObj)
          .then(() => {
            toastr.success('Updated User', 'Success');
            return vm.getUsers();
          })
          .catch(err => {
            vm.$log.error(err);
            toastr.error('Error Updating User', 'Error');
            return err;
          });
      }

      // Hide modal manually
      promise.finally(() => {
        vm.$refs.addOrUpdateUserModal.hide();
      });

    },

    getUserFirstAndLastName(userId) {
      const vm = this;
      const currentUser = _.find(vm.users, { id: userId });
      return currentUser.firstName + ' ' + currentUser.lastName + ' ';
    },

    isFinalAdmin(userRole) {
      const vm = this;
      if (_.head(userRole) === 0) {
        const adminFilter = _.filter(vm.displayedUsers, { roles: 0 });
        if (adminFilter.length < 2) {
          return true;
        }
      }
      return false;
    },

    toggleMFAStatus(userObj) {
      const vm = this;
      const isMfaEnabled = _.get(userObj, 'isMfaEnabled', false);
      if (!_.isBoolean(isMfaEnabled)) {
        return;
      }
      const newMfaValue = !isMfaEnabled; // new value will be opposite of what it's at.
      // eslint-disable-next-line template-curly-spacing
      const shouldToggle = window.confirm(`Are you sure you want to turn MFA ${isMfaEnabled ? 'off' : 'on'} for ${userObj.username}?`);
      if (shouldToggle !== true) {
        return;
      }
      return this.apiToggleUserMfa(userObj.id, !isMfaEnabled)
        .then(() => {
          toastr.success('Successfully changed MFA status.', 'Success');
          userObj.isMfaEnabled = newMfaValue;
          return newMfaValue;
        })
        .then(() => {
          return vm.getUsers();
        })
        .catch((err) => {
          vm.$log.error(err);
          toastr.error('Failed to toggle MFA status.', 'Error');
          return err;
        });
    },

    // </editor-fold>

    // <editor-fold desc="Password Management">

    togglePasswordView() {
      if (this.userModal.passwordRenderType === 'password') {
        this.userModal.passwordRenderType = 'text';
      } else {
        this.userModal.passwordRenderType = 'password';
      }
    },

    verifyPasswords() {
      const validPass = _.isString(this.userModal.form.password) && size(this.userModal.form.password) > 7;
      const validPassRpt = _.isString(this.userModal.form.passwordRepeat) && size(this.userModal.form.passwordRepeat) > 7;
      const validAndMatch = validPass && validPassRpt ? this.userModal.form.password === this.userModal.form.passwordRepeat : false;
      const isEdgeCase = validPass && validPassRpt && this.userModal.form.password === '' && this.userModal.form.passwordRepeat === '';
      if (isEdgeCase || !validAndMatch) {
        this.userModal.formState.password = false;
        this.userModal.formState.passwordRepeat = false;
      } else {
        this.userModal.formState.password = true;
        this.userModal.formState.passwordRepeat = true;
      }
    }

    // </editor-fold>

  }
};

</script>

<style lang="scss" scoped>
@import '@/assets/styles/_variables.scss';

// Inspired by `button-outline-variant` mixin, tables.scss and .table-bordered
.user-mgmt-table {

  // Prevents border (below) from adding scrollbars due to size
  padding-left: $table-border-width;
  padding-right: $table-border-width;

  @each $theme-color, $theme-color-value in $theme-colors {

    &::v-deep .table-outline-#{$theme-color} {

      $color: $theme-color-value;
      $color-hover: color-yiq($color);
      $active-background: $color;
      $active-border: $color;

      color: $color;
      border: $table-border-width solid $color;
      border-width: 2 * $table-border-width;

      >td {
        border-top: $table-border-width solid $color;
        border-bottom: $table-border-width solid $color;
      }

      &:first-child td {
        // https://www.w3.org/TR/CSS2/tables.html#border-conflict-resolution
        border-top: $table-border-width double $color;
        border-top-width: 2 * $table-border-width; // re-declare due to conflict resolution algorithm
      }

      @include hover {
        // color:            $color-hover;
        // background-color: $active-background;
        border-color: $active-border;
      }

      &:focus,
      &.focus {
        box-shadow: 0 0 0 $btn-focus-width rgba($color, .5);
      }

      &.disabled,
      &:disabled {
        color: $color;
        background-color: transparent;
      }

    }

  }

}
</style>
