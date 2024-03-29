--
-- Copyright (c) 2023 The Johns Hopkins University Applied Physics
-- Laboratory LLC.
--
-- This file is part of the Asynchronous Network Management System (ANMS).
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--     http://www.apache.org/licenses/LICENSE-2.0
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.
--
-- This work was performed for the Jet Propulsion Laboratory, California
-- Institute of Technology, sponsored by the United States Government under
-- the prime contract 80NM0018D0004 between the Caltech and NASA under
-- subcontract 1658085.
--

DO
$do$
DECLARE 
adm_enum integer;
dtn_namespace_id integer;
ion_ipnadmin_meta_name integer;
ion_ipnadmin_meta_name_did integer;
ion_ipnadmin_meta_namespace integer;
ion_ipnadmin_meta_namespace_did integer;
ion_ipnadmin_meta_version integer;
ion_ipnadmin_meta_version_did integer;
ion_ipnadmin_meta_organization integer;
ion_ipnadmin_meta_organization_did integer;
ion_ipnadmin_edd_ion_version integer;
ion_ipnadmin_edd_ion_version_did integer;
ion_ipnadmin_edd_ion_version_aid integer;
ion_ipnadmin_tblt_exits integer;
tbl_tnvc_id integer;
tnvc_entry integer;
ion_ipnadmin_tblt_exits_did integer;
ion_ipnadmin_tblt_plans integer;
ion_ipnadmin_tblt_plans_did integer;
ion_ipnadmin_ctrl_exit_add integer;
fp_spec_id integer;
r_fp_ent integer;
ion_ipnadmin_ctrl_exit_add_did integer;
ion_ipnadmin_ctrl_exit_change integer;
ion_ipnadmin_ctrl_exit_change_did integer;
ion_ipnadmin_ctrl_exit_del integer;
ion_ipnadmin_ctrl_exit_del_did integer;
ion_ipnadmin_ctrl_plan_add integer;
ion_ipnadmin_ctrl_plan_add_did integer;
ion_ipnadmin_ctrl_plan_change integer;
ion_ipnadmin_ctrl_plan_change_did integer;
ion_ipnadmin_ctrl_plan_del integer;
ion_ipnadmin_ctrl_plan_del_did integer;
BEGIN
adm_enum = 6;
CALL SP__insert_adm_defined_namespace('JHUAPL', 'DTN/ION/ipnadmin', 'v0.0', 'ion_ipn_admin', adm_enum, NULL, 'The namespace of the ADM', dtn_namespace_id);


-- #META
CALL SP__insert_obj_metadata(0, 'name', dtn_namespace_id, ion_ipnadmin_meta_name);
CALL SP__insert_const_actual_definition(ion_ipnadmin_meta_name, 'The human-readable name of the ADM.', 'STR', 'ion_ipn_admin', ion_ipnadmin_meta_name_did);

CALL SP__insert_obj_metadata(0, 'namespace', dtn_namespace_id, ion_ipnadmin_meta_namespace);
CALL SP__insert_const_actual_definition(ion_ipnadmin_meta_namespace, 'The namespace of the ADM', 'STR', 'DTN/ION/ipnadmin', ion_ipnadmin_meta_namespace_did);

CALL SP__insert_obj_metadata(0, 'version', dtn_namespace_id, ion_ipnadmin_meta_version);
CALL SP__insert_const_actual_definition(ion_ipnadmin_meta_version, 'The version of the ADM', 'STR', 'v0.0', ion_ipnadmin_meta_version_did);

CALL SP__insert_obj_metadata(0, 'organization', dtn_namespace_id, ion_ipnadmin_meta_organization);
CALL SP__insert_const_actual_definition(ion_ipnadmin_meta_organization, 'The name of the issuing organization of the ADM', 'STR', 'JHUAPL', ion_ipnadmin_meta_organization_did);

-- #EDD
CALL SP__insert_obj_metadata(2, 'ion_version', dtn_namespace_id, ion_ipnadmin_edd_ion_version);
CALL SP__insert_edd_formal_definition(ion_ipnadmin_edd_ion_version, 'This is the version of ion is that currently installed.', NULL, 'STR', ion_ipnadmin_edd_ion_version_did);
CALL SP__insert_edd_actual_definition(ion_ipnadmin_edd_ion_version, 'The singleton value for ion_version', NULL, ion_ipnadmin_edd_ion_version_aid);

-- #OPER

-- #VAR

-- #TBLT
CALL SP__insert_obj_metadata(10, 'exits', dtn_namespace_id, ion_ipnadmin_tblt_exits);
CALL SP__insert_tnvc_collection('columns for the exits table', tbl_tnvc_id);
CALL SP__insert_tnvc_uvast_entry(tbl_tnvc_id, 1, 'first_node_nbr', null, tnvc_entry);
CALL SP__insert_tnvc_uvast_entry(tbl_tnvc_id, 2, 'last_node_nbr', null, tnvc_entry);
CALL SP__insert_tnvc_str_entry(tbl_tnvc_id, 3, 'gateway_endpoint_id', null, tnvc_entry);
CALL SP__insert_table_template_actual_definition(ion_ipnadmin_tblt_exits, 'This table lists all of the exits that are defined in the IPN database for the local node.', tbl_tnvc_id, ion_ipnadmin_tblt_exits_did);

CALL SP__insert_obj_metadata(10, 'plans', dtn_namespace_id, ion_ipnadmin_tblt_plans);
CALL SP__insert_tnvc_collection('columns for the plans table', tbl_tnvc_id);
CALL SP__insert_tnvc_uvast_entry(tbl_tnvc_id, 1, 'node_nbr', null, tnvc_entry);
CALL SP__insert_tnvc_str_entry(tbl_tnvc_id, 2, 'action', null, tnvc_entry);
CALL SP__insert_tnvc_str_entry(tbl_tnvc_id, 3, 'spec', null, tnvc_entry);
CALL SP__insert_table_template_actual_definition(ion_ipnadmin_tblt_plans, 'This table lists all of the egress plans that are established in the IPN database for the local node.', tbl_tnvc_id, ion_ipnadmin_tblt_plans_did);


-- #RPTT

-- #CTRL
CALL SP__insert_obj_metadata(1, 'exit_add', dtn_namespace_id, ion_ipnadmin_ctrl_exit_add);
CALL SP__insert_formal_parmspec(3, 'parms for the exit_add control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'first_node_nbr', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 2, 'last_node_nbr', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 3, 'gateway_endpoint_id', 'STR', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ipnadmin_ctrl_exit_add , 'This control establishes an exit for static default routing.', fp_spec_id, ion_ipnadmin_ctrl_exit_add_did);

CALL SP__insert_obj_metadata(1, 'exit_change', dtn_namespace_id, ion_ipnadmin_ctrl_exit_change);
CALL SP__insert_formal_parmspec(3, 'parms for the exit_change control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'first_node_nbr', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 2, 'last_node_nbr', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 3, 'gatewayEndpointId', 'STR', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ipnadmin_ctrl_exit_change , 'This control changes the gateway node number for the exit identified by firstNodeNbr and lastNodeNbr.', fp_spec_id, ion_ipnadmin_ctrl_exit_change_did);

CALL SP__insert_obj_metadata(1, 'exit_del', dtn_namespace_id, ion_ipnadmin_ctrl_exit_del);
CALL SP__insert_formal_parmspec(2, 'parms for the exit_del control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'first_node_nbr', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 2, 'last_node_nbr', 'UINT', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ipnadmin_ctrl_exit_del , 'This control deletes the exit identified by firstNodeNbr and lastNodeNbr.', fp_spec_id, ion_ipnadmin_ctrl_exit_del_did);

CALL SP__insert_obj_metadata(1, 'plan_add', dtn_namespace_id, ion_ipnadmin_ctrl_plan_add);
CALL SP__insert_formal_parmspec(2, 'parms for the plan_add control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'node_nbr', 'UVAST', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 2, 'xmit_rate', 'UINT', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ipnadmin_ctrl_plan_add , 'This control establishes an egress plan for the bundles that must be transmitted to the neighboring node that is identified by it''s nodeNbr.', fp_spec_id, ion_ipnadmin_ctrl_plan_add_did);

CALL SP__insert_obj_metadata(1, 'plan_change', dtn_namespace_id, ion_ipnadmin_ctrl_plan_change);
CALL SP__insert_formal_parmspec(2, 'parms for the plan_change control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'node_nbr', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 2, 'default_duct_expression', 'STR', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ipnadmin_ctrl_plan_change , 'This control changes the duct expression for the indicated plan.', fp_spec_id, ion_ipnadmin_ctrl_plan_change_did);

CALL SP__insert_obj_metadata(1, 'plan_del', dtn_namespace_id, ion_ipnadmin_ctrl_plan_del);
CALL SP__insert_formal_parmspec(1, 'parms for the plan_del control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'node_nbr', 'UINT', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ipnadmin_ctrl_plan_del , 'This control deletes the egress plan for the node that is identified by it''s nodeNbr.', fp_spec_id, ion_ipnadmin_ctrl_plan_del_did);


-- #CONST

-- #MAC
END
$do$