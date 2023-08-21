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
import Vue from "vue";
import ari_parameter from "./ariParamter";
import tnvc_parameter from "./tnvcParameter";
import prim_parameter from "./primParameter.vue";
import api from "../../../shared/api.js";
import collect from "collect.js";
import vSelect from "vue-select";


export default {
    components: {
        ari_parameter,
        tnvc_parameter,
        prim_parameter,
        vSelect,
    },
    data: function () {
        return {
            parameters: null,
            finResult: [],
        }
    },
    methods: {
        genNames: async function (ACs, resolve) {
            let aris = []
            let promisesFormal = []
            let formalAris = []
            let promisesActual = []
            let actualAris = []
            let results = "";

            ACs.forEach((ari) => {
                results = "";
                if (ari.parm_id == null) {
                    results =
                        "ari:/IANA:"+ari.adm_name + "/" + ari.type_name + "." + ari.obj_name + "()";
                    aris.push(Object.assign({}, ari, { display: results }));
                } else {
                    if (ari.actual == false) {
                        let parms = "";
                        formalAris.push(ari)
                        promisesFormal.push(api.methods
                            .apiGetFormalParmID(ari.parm_id))

                    } else {
                        let parms = "";
                        let parametersPromise = []
                        //first get parms
                        actualAris.push(ari)
                        promisesActual.push(
                            api.methods
                                .apiGetActualParmID(ari.parm_id))
                    }
                }
                //then get formal parms for blue print
            });
            await Promise.all(promisesFormal).then((responses) => {

                responses.forEach((response, index) => {
                    let ari = formalAris[index]
                    let parms = response.data.parm_type_name;
                    results =
                        "ari:/IANA:"+ari.adm_name +
                        "/" +
                        ari.type_name +
                        "." +
                        ari.obj_name +
                        "(" +
                        parms +
                        ")";
                    aris.push(Object.assign({}, ari, { display: results }));
                })
            });

            await Promise.all(promisesActual).then((responses) => {

                responses.forEach((response, index) => {
                    let ari = actualAris.pop()
                    var actual_parm;
                    var formal_parm;
                    var a_parm_values = [];
                    actual_parm = response.data;
                    api.methods
                        .apiGetFormalParmID(actual_parm.fp_spec_id)
                        .then((response) => {
                            formal_parm = response.data;

                            let names = formal_parm.parm_type_name.split(",");

                            let fp_values =
                                actual_parm.fp_values == null
                                    ? []
                                    : actual_parm.fp_values.split(",");
                            let obj_values =
                                actual_parm.obj_values == null
                                    ? []
                                    : actual_parm.obj_values.split(",");
                            let str_values =
                                actual_parm.str_values == null
                                    ? []
                                    : actual_parm.str_values.split(",");
                            let int_values =
                                actual_parm.int_values == null
                                    ? []
                                    : actual_parm.int_values.split(",");
                            let uint_values =
                                actual_parm.uint_values == null
                                    ? []
                                    : actual_parm.uint_values.split(",");
                            let vast_values =
                                actual_parm.vast_values == null
                                    ? []
                                    : actual_parm.vast_values.split(",");
                            let uvast_values =
                                actual_parm.uvast_values == null
                                    ? []
                                    : actual_parm.uvast_values.split(",");
                            let real32_values =
                                actual_parm.real32_values == null
                                    ? []
                                    : actual_parm.real32_values.split(",");
                            let real64_values =
                                actual_parm.real64_values == null
                                    ? []
                                    : actual_parm.real64_values.split(",");

                            for (let i = 0; i < formal_parm.num_parms; i++) {
                                switch (names[i].toUpperCase()) {
                                    case "STR":
                                        if (fp_values != null) {
                                            //todo refrence name
                                            a_parm_values.push("REF." + fp_values.pop());
                                        } else if (obj_values != null) {
                                            a_parm_values.push("STR." + api.methods.getLitValue(obj_values.pop()));
                                        }
                                        else {
                                            a_parm_values.push("STR." + str_values.pop());
                                        }
                                        break;
                                    case "INT":
                                        if (fp_values != null) {
                                            //todo refrence name
                                            a_parm_values.push("REF." + fp_values.pop());
                                        } else if (obj_values != null) {
                                            a_parm_values.push("INT." + api.methods.getLitValue(obj_values.pop()));
                                        }
                                        else {
                                            a_parm_values.push("INT." + int_values.pop());
                                        }
                                        break;
                                    case "UINT":
                                        if (fp_values != null) {
                                            //todo refrence name
                                            a_parm_values.push("REF." + fp_values.pop());
                                        } else if (obj_values != null) {
                                            a_parm_values.push("UINT." + api.methods.getLitValue(obj_values.pop()));
                                        }
                                        else {
                                            a_parm_values.push("UINT." + uint_values.pop());
                                        }
                                        break;
                                    case "VAST": if (fp_values != null) {
                                        //todo refrence name
                                        a_parm_values.push("REF." + fp_values.pop());
                                    } else if (obj_values != null) {
                                        a_parm_values.push("VAST." + api.methods.getLitValue(obj_values.pop()));
                                    }
                                    else {
                                        a_parm_values.push("VAST." + vast_values.pop());
                                    }
                                        break;
                                    case "UVAST": if (fp_values != null) {
                                        //todo refrence name
                                        a_parm_values.push("REF." + fp_values.pop());
                                    } else if (obj_values != null) {
                                        a_parm_values.push("UVAST." + api.methods.getLitValue(obj_values.pop()));
                                    }
                                    else {
                                        a_parm_values.push("UVAST." + uvast_values.pop());
                                    }
                                        break;
                                    case "REAL32": if (fp_values != null) {
                                        //todo refrence name
                                        a_parm_values.push("REF." + fp_values.pop());
                                    } else if (obj_values != null) {
                                        a_parm_values.push("REAL32." + api.methods.getLitValue(obj_values.pop()));
                                    }
                                    else {
                                        a_parm_values.push("REAL32." + real32_values.pop());
                                    }
                                        break;
                                    case "REAL64": if (fp_values != null) {
                                        //todo refrence name
                                        a_parm_values.push("REF." + fp_values.pop());
                                    } else if (obj_values != null) {
                                        a_parm_values.push("REAL64." + api.methods.getLitValue(obj_values.pop()));
                                    }
                                    else {
                                        a_parm_values.push("REAL64." + real64_values.pop());
                                    }
                                        break;
                                    case "TV":
                                        a_parm_values.push("TV." + uint_values.pop());
                                        break;
                                    case "TS":
                                        a_parm_values.push("TS." + uint_values.pop());
                                        break;
                                    case "BOOL":
                                        a_parm_values.push("BOOL." + int_values.pop());
                                        break;
                                    case "EXPR":
                                        a_parm_values.push("EXPR." + int_values.pop());
                                        break;
                                    case "BYTE":
                                        a_parm_values.push("BYTE." + int_values.pop());
                                        break;

                                    case "BYTESTR":
                                        a_parm_values.push("BYTESTR." + int_values.pop());
                                        break;

                                    case "TNVC": //tnvc
                                        a_parm_values.push("TNVC." + int_values.pop());
                                        break;
                                    case "ARI": //ari
                                        a_parm_values.push("ARI." + int_values.pop());
                                        break;

                                    case "AC": //ac
                                        a_parm_values.push("AC." + int_values.pop());
                                        break;
                                }
                            }

                            results =
                            "ari://IANA:"+
                                ari.adm_name +
                                "/" +
                                ari.type_name +
                                "." +
                                ari.obj_name +
                                "(" +
                                a_parm_values +
                                ")";

                            aris.push(Object.assign({}, ari, { display: results }));


                        });
                });
            });

            resolve(aris)
        },
        genParms: async function (ariKey, resolve, ACs) {


            // let promise = new Promise((resolve, reject) => { this.genNames(ACs, resolve) })
            let aris = ACs
            var description = "";
            var distParms = [];
            let finResult = []
            if (ariKey.actual || ariKey.parm_id == null) {
                distParms = [];
                resolve([], "");
            } else {
                let parms = [];
                let names = [];

                api.methods
                    .apiGetFormalParmID(ariKey.parm_id)
                    .then((response) => {
                        parms = response.data.parm_type_name.split(",");
                        names = response.data.parm_names.split(",");


                        let combined = collect(parms).zip(names);
                        let typeLabel = "";
                        description = ariKey.use_desc;

                        combined.each((info, index) => {
                            let parm = info.items[0];
                            let name = info.items[1];

                            switch (parm) {
                                case "STR":
                                    finResult.push({ "type": "STR", "value": " " });
                                    typeLabel = "STR";
                                    distParms.push({
                                        type: prim_parameter,
                                        parameter: { result: "", name: name, type: typeLabel },
                                    });
                                    break;
                                case "BYTESTR":
                                    finResult.push({ "type": "BYTESTR", "value": " " });
                                    typeLabel = "BYTESTR";
                                    distParms.push({
                                        type: prim_parameter,
                                        parameter: { result: "", name: name, type: typeLabel },
                                    });
                                    break;
                                case "BYTE":
                                    finResult.push({ "type": "BYTE", "value": " " });
                                    typeLabel = "BYTE";
                                    distParms.push({
                                        type: prim_parameter,
                                        parameter: { result: "", name: name, type: typeLabel },
                                    });
                                    break;
                                case "INT":
                                    finResult.push({ "type": "INT", "value": 0 });
                                    typeLabel = "INT";
                                    distParms.push({
                                        type: prim_parameter,
                                        parameter: { result: "", name: name, type: typeLabel },
                                    });
                                    break;
                                case "UINT":
                                    finResult.push({ "type": "UINT", "value": 0 });
                                    typeLabel = "UINT";
                                    distParms.push({
                                        type: prim_parameter,
                                        parameter: { result: "", name: name, type: typeLabel },
                                    });
                                    break;
                                case "VAST":
                                    finResult.push({ "type": "VAST", "value": 0 });
                                    typeLabel = "VAST";
                                    distParms.push({
                                        type: prim_parameter,
                                        parameter: { result: "", name: name, type: typeLabel },
                                    });
                                    break;
                                case "UVAST":
                                    finResult.push({ "type": "UVAST", "value": 0 });
                                    typeLabel = "UVAST";
                                    distParms.push({
                                        type: prim_parameter,
                                        parameter: { result: "", name: name, type: typeLabel },
                                    });
                                    break;
                                case "REAL32":
                                    finResult.push({ "type": "REAL32", "value": 0 })
                                    Label = "REAL32";
                                    distParms.push({
                                        type: prim_parameter,
                                        parameter: { result: "", name: name, type: typeLabel },
                                    });
                                    break;
                                case "REAL64":
                                    finResult.push({ "type": "REAL64", "value": 0 })
                                    Label = "REAL64";
                                    distParms.push({
                                        type: prim_parameter,
                                        parameter: { result: "", name: name, type: typeLabel },
                                    });
                                    break;
                                case "TV":
                                    finResult.push({ "type": "TV", "value": 0 });
                                    typeLabel = "TV";
                                    distParms.push({
                                        type: prim_parameter,
                                        parameter: { result: "", name: name, type: typeLabel },
                                    });
                                    break;
                                case "TS":
                                    finResult.push({ "type": "TS", "value": 0 });
                                    typeLabel = "TS";
                                    distParms.push({
                                        type: prim_parameter,
                                        parameter: { result: "", name: name, type: typeLabel },
                                    });
                                    break;

                                case "TNVC": //tnvc
                                    finResult.push({ "type": "TNVC", "value": [] });

                                    distParms.push({
                                        type: tnvc_parameter,
                                        parameter: {
                                            result: [],
                                            types: this.types,
                                            name: name,
                                            listComponents: [],
                                        },
                                    });
                                    break;
                                case "ARI": //ari
                                    finResult.push({ "type": "ARI", "value": "" });
                                    typeLabel = "ARI";
                                    distParms.push({
                                        type: prim_parameter,
                                        parameter: { result: "", name: name, type: typeLabel },
                                    });
                                    break;

                                case "AC": //ac
                                    finResult.push({ "type": "AC", "value": [] });

                                    distParms.push({
                                        type: ari_parameter,
                                        parameter: {
                                            result: [],
                                            name: name,
                                            type: "AC",
                                            listComponents: aris,
                                        },
                                    });
                                    break;
                                    case "EXPR": //EXPR
                                    finResult.push({ "type": "EXPR", "value": [] });

                                    distParms.push({
                                        type: ari_parameter,
                                        parameter: {
                                            result: [],
                                            name: name,
                                            type: "EXPR",
                                            listComponents: aris,
                                        },
                                    });
                                    break;

                            }

                        });
                        resolve([distParms, description, finResult]);
                    })
                    .catch((error) => {
                        console.error(error);
                        this.errored = true;
                        this.results = "error sending request to node! (check node index)";
                    })
                    .finally();

                // for(type in ctrls.get(id).get("parm_type").split(','))
                //     distParms.push({'ari_parameter':{'listComponents':this.ACs}})
                //   '//'     distParms.push({'ari_parameter':{'listComponents':this.mngs}})

            }
            //''if parms' is tnvc 'for' rxmanger
            // spawn man box
        },
    }
}
