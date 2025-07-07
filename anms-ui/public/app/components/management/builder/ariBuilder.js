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
import collect from "collect.js";
import api from "../../../shared/api";
import ActionParameter from "./ActionParameter";
import prim_parameter from "./primParameter.vue";
import ExpressionParameter from "./ExprParameter.vue";

export default {
    components: {
        prim_parameter,
        ActionParameter,
        ExpressionParameter,
    },
    data: function () {
        return {
            parameters: null,
            finResult: [],
            types: ["LITERAL", "NULL", "BOOL", "BYTE", "INT", "UINT", "VAST", "UVAST", "REAL32", "REAL64", "TEXTSTR", "BYTESTR", "TP", "TD", "LABEL", "CBOR", "ARITYPE", "AC", "AM", "TBL", "EXECSET", "RPTSET", "OBJECT", "TYPEDEF", "IDENT", "CONST", "EDD", "VAR", "CTRL", "OPER", "SBR", "TBR"]
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
                        case "/ARITYPE/TEXTSTR":
                            finResult.push({ "index": index, "type": "/ARITYPE/TEXTSTR", "value": " " });
                            typeLabel = "TEXTSTR";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "/ARITYPE/BYTESTR":
                            finResult.push({ "index": index, "type": "/ARITYPE/BYTESTR", "value": " " });
                            typeLabel = "BYTESTR";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "/ARITYPE/BYTE":
                            finResult.push({ "index": index, "type": "/ARITYPE/BYTE", "value": " " });
                            typeLabel = "BYTE";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "/ARITYPE/INT":
                            finResult.push({ "index": index, "type": "/ARITYPE/INT", "value": 0 });
                            typeLabel = "INT";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "/ARITYPE/UINT":
                            finResult.push({ "index": index, "type": "/ARITYPE/UINT", "value": 0 });
                            typeLabel = "UINT";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "/ARITYPE/VAST":
                            finResult.push({ "index": index, "type": "/ARITYPE/VAST", "value": 0 });
                            typeLabel = "VAST";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "/ARITYPE/UVAST":
                            finResult.push({ "index": index, "type": "/ARITYPE/UVAST", "value": 0 });
                            typeLabel = "UVAST";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "/ARITYPE/REAL32":
                            finResult.push({ "index": index, "type": "/ARITYPE/REAL32", "value": 0 })
                            typeLabel = "REAL32";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "/ARITYPE/REAL64":
                            finResult.push({ "index": index, "type": "/ARITYPE/REAL64", "value": 0 })
                            typeLabel = "REAL64";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "/ARITYPE/BOOL":
                                finResult.push({ "index": index, "type": "/ARITYPE/BOOl", "value": 0 })
                                typeLabel = "BOOl";
                                distParms.push({
                                    type: prim_parameter,// TODO update to its own 
                                    parameter: { index: index, result: "", name: name, type: typeLabel },
                                });
                                break;
                        case "/ARITYPE/TP":
                            finResult.push({ "index": index, "type": "/ARITYPE/TP", "value": 0 });
                            typeLabel = "TV";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                        case "/ARITYPE/TD":
                            finResult.push({ "index": index, "type": "/ARITYPE/TD", "value": 0 });
                            typeLabel = "TS";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;

                
                        case "/ARITYPE/OBJECT": //ari
                            finResult.push({ "index": index, "type": "/ARITYPE/OBJECT", "value": "" });
                            typeLabel = "ARI";
                            distParms.push({
                                type: prim_parameter,
                                parameter: { index: index, result: "", name: name, type: typeLabel },
                            });
                            break;
                            
                        case "/ARITYPE/AC": //ac
                            finResult.push({ "index": index, "type": "/ARITYPE/AC", "value": [] });

                            distParms.push({
                                type: ActionParameter,
                                parameter: {
                                    index: index,
                                    result: [],
                                    name: name,
                                    type: "AC",
                                    listComponents: aris,
                                    count: 10000000000000, //TODO make infinite large 
                                },
                            });
                            break;
                        case "/ARITYPE/EXECSET": //EXPR
                            finResult.push({ "index": index, "type": "/ARITYPE/EXECSET", "value": [] });

                            distParms.push({
                                type: ExpressionParameter,
                                parameter: {
                                    index: index,
                                    result: [],
                                    name: name,
                                    type: "EXPR",
                                    listComponents: aris,
                                },
                            });
                            break;
                        default:
                            if (parm.includes("TYPEDEF")){
                                finResult.push({ "index": index, "type": "/ARITYPE/TYPEDEF", "value": [] });
                                //  TODO make more complex handle on the actual required 
                                distParms.push({
                                    type: ActionParameter,
                                    parameter: {
                                        index: index,
                                        result: [],
                                        name: name,
                                        type: "TYPEDEF",
                                        listComponents: aris,
                                        count: 1, 
                                    },
                                });
                            }
                            else{
                                finResult.push({ "index": index, "type": parm, "value": "" });
                                typeLabel = parm;
                                distParms.push({
                                    type: prim_parameter,
                                    parameter: { index: index, result: "", name: name, type: typeLabel },
                               });
                            }
                            break;

                    }
                });
                return [distParms, description, finResult];
            }
        },
    }
}
