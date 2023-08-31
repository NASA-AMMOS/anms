/*
 * Copyright (c) 2023 The Johns Hopkins University Applied Physics
 * Laboratory LLC.
 *
 * This file is part of the Asynchronous Network Management System (ANMS).
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
import ari_parameter from "./ariParamter";
import tnvc_parameter from "./tnvcParameter";
import prim_parameter from "./primParameter.vue";
import collect from "collect.js";
import vSelect from "vue-select";
import api from "../../../shared/api";

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
            types: ["CONST", "CTRL", "EDD", "LIT", "MAC", "OPER", "RPT", "RPTT", "SBR", "TBL", "TBLT", "TBR", "VAR", "MDAT", "BOOL", "BYTE", "STR", "INT", "UINT", "VAST", "UVAST", "REAL32", "REAL64", "TV", "TS", "TNV", "TNVC", "ARI", "AC", "EXPR", "BYTESTR"]
        }
    },
    methods: {
        genParms: async function (ariKey, ACs) {
            let aris = ACs
            var description = "";
            var distParms = [];
            let finResult = []
            let paramInfo;
            if (ariKey.actual || ariKey.parm_id == null) {
                distParms = [];
                return [[], ""];
            } else {
                await api.methods.apiQueryForARIById(ariKey.obj_metadata_id, ariKey.obj_id).then(res => {
                    paramInfo = res.data[0]
                })
                let parms = [];
                let names = [];
                parms = paramInfo.param_types
                names = paramInfo.param_names

                let combined = collect(parms).zip(names);
                let typeLabel = "";
                description = paramInfo.use_desc;
                combined.each((info, index) => {
                    let parm = info.items[0];
                    let name = info.items[1];
                    switch (parm) {
                        case "STR":
                            finResult.push({ "index": index, "type": "STR", "value": " " });
                            typeLabel = "STR";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "BYTESTR":
                            finResult.push({ "index": index, "type": "BYTESTR", "value": " " });
                            typeLabel = "BYTESTR";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "BYTE":
                            finResult.push({ "index": index, "type": "BYTE", "value": " " });
                            typeLabel = "BYTE";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "INT":
                            finResult.push({ "index": index, "type": "INT", "value": 0 });
                            typeLabel = "INT";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "UINT":
                            finResult.push({ "index": index, "type": "UINT", "value": 0 });
                            typeLabel = "UINT";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "VAST":
                            finResult.push({ "index": index, "type": "VAST", "value": 0 });
                            typeLabel = "VAST";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "UVAST":
                            finResult.push({ "index": index, "type": "UVAST", "value": 0 });
                            typeLabel = "UVAST";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "REAL32":
                            finResult.push({ "index": index, "type": "REAL32", "value": 0 })
                            Label = "REAL32";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "REAL64":
                            finResult.push({ "index": index, "type": "REAL64", "value": 0 })
                            Label = "REAL64";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "TV":
                            finResult.push({ "index": index, "type": "TV", "value": 0 });
                            typeLabel = "TV";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "TS":
                            finResult.push({ "index": index, "type": "TS", "value": 0 });
                            typeLabel = "TS";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;

                        case "TNVC": //tnvc
                            finResult.push({ "index": index, "type": "TNVC", "value": [] });

                            distParms.push({
                                type: tnvc_parameter,
                                parameter: {
                                    index: index,

                                    result: [],
                                    types: ["CONST", "CTRL", "EDD", "LIT", "MAC", "OPER", "RPT", "RPTT", "SBR", "TBL", "TBLT", "TBR", "VAR", "MDAT", "BOOL", "BYTE", "STR", "INT", "UINT", "VAST", "UVAST", "REAL32", "REAL64", "TV", "TS", "TNV", "TNVC", "ARI", "AC", "EXPR", "BYTESTR"],
                                    name: name,
                                    listComponents: [],
                                },
                            });
                            break;
                        case "ARI": //ari
                            finResult.push({ "index": index, "type": "ARI", "value": "" });
                            typeLabel = "ARI";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;

                        case "AC": //ac
                            finResult.push({ "index": index, "type": "AC", "value": [] });

                            distParms.push({
                                type: ari_parameter,
                                parameter: {
                                    index: index,
                                    result: [],
                                    name: name,
                                    type: "AC",
                                    listComponents: aris,
                                },
                            });
                            break;
                        case "EXPR": //EXPR
                            finResult.push({ "index": index, "type": "EXPR", "value": [] });

                            distParms.push({
                                type: ari_parameter,
                                parameter: {
                                    index: index,
                                    result: [],
                                    name: name,
                                    type: "EXPR",
                                    listComponents: aris,
                                },
                            });
                            break;

                    }
                });
                return [distParms, description, finResult];
            }
        },
    }
}