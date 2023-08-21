/*
 * Copyright (c) 2023 The Johns Hopkins University Applied Physics
 * Laboratory LLC.
 *
 * This file is part of the Asynchronous Network Managment System (ANMS).
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *     http://www.apache.org/licenses/LICENSE-2.0
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * This work was performed for the Jet Propulsion Laboratory, California
 * Institute of Technology, sponsored by the United States Government under
 * the prime contract 80NM0018D0004 between the Caltech and NASA under
 * subcontract 1658085.
 */
import axios from 'axios';
import Constants from '@app/shared/constants';

const adm_url = Constants.BASE_API_URL + 'core/adms';
const createAuthenticationHeader = () => {
    return {
      Authorization: 'Bearer ' + Constants.USER_DETAILS.token
    };
};

//Main API
const apiGetAdms = () => {
    return axios.get(adm_url, {headers: {accept: 'application/json'}})
};
const apiGetAdm = (admEnum) => {
    return axios.get(adm_url+"/"+admEnum )
};

const apiUpdateAdm = async (file) => {
    const auth_headers = createAuthenticationHeader();
    const formData = new FormData();
    formData.append('adm', file);
    const headers = {
        ...auth_headers,
        'Content-Type': 'multipart/form-data'
    };
    return axios.post(adm_url,
        formData,
        {
            headers
        }
    );
};

export default {
    apiGetAdms,
    apiGetAdm,
    apiUpdateAdm
};
