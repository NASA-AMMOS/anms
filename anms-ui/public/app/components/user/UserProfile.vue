<template>
  <div>

    <div class="d-flex justify-content-center mt-3" v-if="loading">
      <b-spinner variant="info" label="Loading..." type="grow"></b-spinner>
    </div>
    <div class="d-flex justify-content-center mt-3" v-if="hasError">
      <b-badge show variant="danger" v-if="notFoundProfile">Your profile is not created</b-badge>
      <b-badge show variant="danger" v-else>{{ errorMsg }} {{ errorCode }}</b-badge>
    </div>
    <!-- <b-row class="mt-3" v-if="!hasProfile">
    <b-button  @click="getProfile" variant="info" size="sm">Get User Profile (Debug Only)</b-button>
  </b-row> -->

    <b-row class="mt-3" v-if="hasProfile || notFoundProfile">

      <b-col cols="12">
        <b-form @submit.prevent="onSubmit">

          <b-modal id="change-password-modal" ref="changePasswordModal" title="Change Password" ok-only
            ok-title="Submit" :ok-disabled="passwordChangeModal.submitDisabled" @hidden="resetPasswordModal"
            @ok="submitPasswordModal">
            <b-form-group label="Current Password" label-for="user-current-password-input">
              <b-form-input id="user-old-password-input" v-model="passwordChangeModal.currentPassword" type="password"
                placeholder="Enter Current Password" autocomplete="current-password" required />
            </b-form-group>
            <b-form-group :state="passwordChangeModal.passwordState" label="Password" label-for="user-password-input"
              invalid-feedback="Password is required and must have at least 8 characters.">
              <b-input-group>
                <b-form-input id="user-password-input" v-model="passwordChangeModal.password"
                  :type="passwordChangeModal.passwordRenderType" :state="passwordChangeModal.passwordState"
                  placeholder="Enter New Password (longer than 7 characters)" required autocomplete="new-password"
                  @input="verifyPasswordsMatch" />
                <b-input-group-append>
                  <b-button variant="light" @click="togglePasswordView">
                    <span v-show="passwordChangeModal.passwordRenderType === 'password'" class="fa fa-eye"></span>
                    <span v-show="passwordChangeModal.passwordRenderType !== 'password'" class="fa fa-eye-slash"></span>
                  </b-button>
                </b-input-group-append>
              </b-input-group>
            </b-form-group>
            <b-form-group :state="passwordChangeModal.passwordRepeatState" label="Repeat Password"
              label-for="user-password-repeat-input"
              invalid-feedback="Repeated Password is required and must match above password.">
              <b-form-input id="user-password-repeat-input" v-model="passwordChangeModal.passwordRepeat"
                :type="passwordChangeModal.passwordRenderType" :state="passwordChangeModal.passwordRepeatState"
                :disabled="passwordChangeModal.password === null" placeholder="Enter Password Again" required
                autocomplete="new-password" @input="verifyPasswordsMatch" />
            </b-form-group>
          </b-modal>

          <b-form-group label="Username" label-for="user-profile-username" class="tour-user-formelems">
            <b-form-input id="user-profile-username" v-model="formData.username" type="text" readonly />
            <b-badge show variant="danger" v-if="hasConflict('username')">{{ conflictFields["username"] }} already
              exists
            </b-badge>
          </b-form-group>

          <b-form-group label="Email" label-for="user-profile-email" class="tour-user-formelems">
            <b-form-input id="user-profile-email" v-model="formData.email" type="email" />
            <b-badge show variant="danger" v-if="hasConflict('email')">{{ conflictFields["email"] }} already exists
            </b-badge>
          </b-form-group>

          <b-form-group label="First Name" label-for="user-profile-first-name" class="tour-user-formelems">
            <b-form-input id="user-profile-first-name" v-model="formData.first_name" type="text" />
          </b-form-group>

          <b-form-group label="Last Name" label-for="user-profile-last-name" class="tour-user-formelems">
            <b-form-input id="user-profile-last-name" v-model="formData.last_name" type="text" />
          </b-form-group>

          <!-- <b-button id="tour-user-changepass" v-b-modal.change-password-modal type="button" variant="warning" size="sm" style="margin-bottom: 1rem">Change Password</b-button> -->

          <b-form-group label="Member Since" label-for="user-profile-created-date" class="tour-user-formelems">
            <b-form-input id="user-profile-created-date" v-model="createdDate" type="text" readonly />
          </b-form-group>

          <div class="text-right">
            <b-button v-if="hasProfile" id="tour-user-submit" type="submit" variant="success" :disabled="isNotUpdatable || isNotValidFormData">
              Update</b-button>
            <b-button v-if="notFoundProfile" id="tour-user-submit" type="submit" variant="success" :disabled="isNotValidFormData">Create</b-button>
          </div>


        </b-form>
      </b-col>

    </b-row>
  </div>
</template>

<script>

import _ from 'lodash';
import api from '@app/shared/api';
import Constants from '@app/shared/constants';
import toastr from 'toastr';
import { mapActions, mapGetters, mapMutations } from 'vuex';

//const userDetailsCopy = _.cloneDeep(Constants.USER_DETAILS);
const defaultPasswordResetForm = {
  submitDisabled: true,
  currentPassword: null,
  password: null,
  passwordState: null,
  passwordRepeat: null,
  passwordRepeatState: null,
  passwordRenderType: 'password'
};

export default {
  name: 'UserProfile',
  mixins: [api],
  data() {
    return {
      formData: {
        username: Constants.USER_NAME_REMOTE
      },
      conflictFields: {},
      //hasDetails: _.size(userDetailsCopy.details) > 0,
      //createdDate: this.$moment(userDetailsCopy.createdAt).fromNow(true),
      passwordChangeModal: Object.assign({}, defaultPasswordResetForm)
    };
  },
  computed: {
    ...mapGetters("user", {
      userDetails: "userDetails",
      errorMsg: "errorMsg",
      errorCode: "errorCode",
      loading: "loading"
    }),
    createdDate() {
      //if (this.userDetails.createdAt);
      let createdMoment = this.$moment(this.userDetails.created_at);
      if (createdMoment.isValid)
        return createdMoment.fromNow(true);
      else
        return "Unknown";
    },
    hasError() {
      return this.errorMsg != "";
    },
    notFoundProfile() {
      return this.errorCode == 404;
    },
    hasProfile() {
      return !this.loading && this.userDetails.username == Constants.USER_NAME_REMOTE;
    },
    isNotUpdatable() {
      return _.isEqual(this.userDetails, this.formData);
    },
    isNotValidFormData() {
      return _.isEmpty(this.formData.first_name)
            || _.isEmpty(this.formData.last_name);
    }
  },
  mounted() {
    this.getProfile();
  },
  watch: {
    userDetails(oldDetails, newDetails){
      this.updateFormData();
    }
  },
  methods: {
    ...mapActions("user", {
      getUserDetails: "getUserDetails",
      updateNewProfile: "updateNewProfile"
    }),
    ...mapMutations("user", {
      commitUserDetails: "userDetails",
      commitErrorCode: "errorCode"
    }),
    updateFormData() {
      this.formData = _.cloneDeep(this.userDetails);
    },
    hasConflict(field) {
      return this.conflictFields[field] !== undefined;
    },
    setConflict(values) {
      this.conflictFields = {
        ...values
      }
    },
    foo(event) {
      alert(event.target.val);
    },
    async getProfile() {
      await this.getUserDetails(Constants.USER_NAME_REMOTE);
    },
    getDetail(key) {
      return this.userDetails[key];
    },
    toPascal(text) {
      return _.upperFirst(_.camelCase(text));
    },
    //Form actions
    async onSubmit() {
      if (this.notFoundProfile) {
        console.info("Creating User Profile");
        this.createProfile();
        return;
      }
      console.info("Updating User Profile");
      const vm = this;
      const finalPut = {
        email: _.get(this.formData, 'email'),
        first_name: _.get(this.formData, 'first_name'),
        last_name: _.get(this.formData, 'last_name'),
      };
      try {
        const res = await this.apiUpdateUserProfile(Constants.USER_NAME_REMOTE, finalPut);
        if (res.status >= 200 && res.status < 300) {
          vm.setConflict({});
          toastr.success('Updated Successfully.');
          vm.commitUserDetails(finalPut);
        } else {
          toastr.warning(res.statusText);
        }
      } catch (error) {
        vm.$log.error("updating user profile error: ", error);
        const response = error.response;
        if (response) {
          vm.$log.error("updating user profile response: ", error.response);
          let errorMsg = `${error.response.statusText}`;
          toastr.error(errorMsg);
          if (response.status == 409) {
            const conflict_values = error.response.data;
            vm.setConflict(conflict_values);
          }
        }
      }
    },
    async createProfile() {
      const vm = this;
      const finalPut = {
        username: _.get(this.formData, 'username'),
        email: _.get(this.formData, 'email'),
        first_name: _.get(this.formData, 'first_name'),
        last_name: _.get(this.formData, 'last_name'),
      };
      try {
        const res = await this.apiCreateUserProfile(finalPut);
        if (res.status == 201) {
         
          const createdProfile = {
            username: _.get(res.data, 'username'),
            email: _.get(res.data, 'email'),
            first_name: _.get(res.data, 'first_name'),
            last_name: _.get(res.data, 'last_name'),
            created_at: _.get(res.data, 'created_at')
          };
          vm.$log.info("Created profile: ", createdProfile);
          toastr.success(`${createdProfile.username} is successfully Created.`);
          vm.setConflict({});
          vm.updateNewProfile(createdProfile);
        } else {
          toastr.warning(res.statusText);
        }
      } catch (error) {
        vm.$log.error("creating user profile error: ", error);
        const response = error.response;
        if (response) {
          vm.$log.error("creating user profile response: ", error.response);
          let errorMsg = `${error.response.statusText}`;
          toastr.error(errorMsg);
          if (response.status == 409) {
            const conflict_values = error.response.data;
            vm.setConflict(conflict_values);
          }
        }
      }
    },
    togglePasswordView() {
      if (this.passwordChangeModal.passwordRenderType === 'password') {
        this.passwordChangeModal.passwordRenderType = 'text';
      } else {
        this.passwordChangeModal.passwordRenderType = 'password';
      }
    },
    verifyPasswordsMatch() {
      const validPass = _.isString(this.passwordChangeModal.password) && _.size(this.passwordChangeModal.password) > 7;
      const validPassRpt = _.isString(this.passwordChangeModal.passwordRepeat) && _.size(this.passwordChangeModal.passwordRepeat) > 7;
      const isEdgeCase = validPass && validPassRpt && this.passwordChangeModal.password === '' && this.passwordChangeModal.passwordRepeat === '';
      if (isEdgeCase) {
        this.passwordChangeModal.passwordState = false;
        this.passwordChangeModal.passwordRepeatState = false;
        return;
      }
      if (validPass && validPassRpt && (this.passwordChangeModal.password === this.passwordChangeModal.passwordRepeat)) {
        this.updatePasswordChangeModalState(true);
      } else {
        this.updatePasswordChangeModalState(false);
      }
    },
    updatePasswordChangeModalState(state) {
      this.passwordChangeModal.passwordState = state;
      this.passwordChangeModal.passwordRepeatState = state;
      this.passwordChangeModal.submitDisabled = !state;
    },
    resetPasswordModal() {
      this.passwordChangeModal = Object.assign({}, defaultPasswordResetForm);
    },
    submitPasswordModal(evt) {
      const vm = this;
      evt.preventDefault(); // prevent modal from closing
      this.apiChangePassword(this.userDetails.id, this.passwordChangeModal)
        .then((res) => {
          toastr.success('Successfully change password');
          vm.$refs.changePasswordModal.hide();
        })
        .catch(err => {
          toastr.error('Failed to change password');
        });

    }
  }
};
</script>

<style lang="scss" scoped>

</style>
