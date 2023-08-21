--
-- Copyright (c) 2023 The Johns Hopkins University Applied Physics
-- Laboratory LLC.
--
-- This file is part of the Asynchronous Network Managment System (ANMS).
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
adm_enum INTEGER;
dtn_namespace_id INTEGER;
ion_ltpadmin_meta_name INTEGER;
ion_ltpadmin_meta_name_did INTEGER;
ion_ltpadmin_meta_namespace INTEGER;
ion_ltpadmin_meta_namespace_did INTEGER;
ion_ltpadmin_meta_version INTEGER;
ion_ltpadmin_meta_version_did INTEGER;
ion_ltpadmin_meta_organization INTEGER;
ion_ltpadmin_meta_organization_did INTEGER;
ion_ltpadmin_edd_ion_version INTEGER;
ion_ltpadmin_edd_ion_version_did INTEGER;
ion_ltpadmin_edd_ion_version_aid INTEGER;
ion_ltpadmin_tblt_spans INTEGER;
tbl_tnvc_id INTEGER;
tnvc_entry INTEGER;
ion_ltpadmin_tblt_spans_did INTEGER;
ion_ltpadmin_ctrl_manage_heap INTEGER;
fp_spec_id INTEGER;
r_fp_ent INTEGER;
ion_ltpadmin_ctrl_manage_heap_did INTEGER;
ion_ltpadmin_ctrl_manage_max_ber INTEGER;
ion_ltpadmin_ctrl_manage_max_ber_did INTEGER;
ion_ltpadmin_ctrl_manage_own_queue_time INTEGER;
ion_ltpadmin_ctrl_manage_own_queue_time_did INTEGER;
ion_ltpadmin_ctrl_manage_screening INTEGER;
ion_ltpadmin_ctrl_manage_screening_did INTEGER;
ion_ltpadmin_ctrl_span_add INTEGER;
ion_ltpadmin_ctrl_span_add_did INTEGER;
ion_ltpadmin_ctrl_span_change INTEGER;
ion_ltpadmin_ctrl_span_change_did INTEGER;
ion_ltpadmin_ctrl_span_del INTEGER;
ion_ltpadmin_ctrl_span_del_did INTEGER;
ion_ltpadmin_ctrl_stop INTEGER;
ion_ltpadmin_ctrl_stop_did INTEGER;
ion_ltpadmin_ctrl_watch_set INTEGER;
 negative INTEGER;
ion_ltpadmin_ctrl_watch_set_did INTEGER;


BEGIN
adm_enum = 9;
CALL SP__insert_adm_defined_namespace('JHUAPL', 'DTN/ION/ltpadmin', 'v0.0', 'ion_ltp_admin', adm_enum, NULL, 'The namespace of the ADM.', dtn_namespace_id);


-- #META
CALL SP__insert_obj_metadata(0, 'name', dtn_namespace_id, ion_ltpadmin_meta_name);
CALL SP__insert_const_actual_definition(ion_ltpadmin_meta_name, 'The human-readable name of the ADM.', 'STR', 'ion_ltp_admin', ion_ltpadmin_meta_name_did);

CALL SP__insert_obj_metadata(0, 'namespace', dtn_namespace_id, ion_ltpadmin_meta_namespace);
CALL SP__insert_const_actual_definition(ion_ltpadmin_meta_namespace, 'The namespace of the ADM.', 'STR', 'DTN/ION/ltpadmin', ion_ltpadmin_meta_namespace_did);

CALL SP__insert_obj_metadata(0, 'version', dtn_namespace_id, ion_ltpadmin_meta_version);
CALL SP__insert_const_actual_definition(ion_ltpadmin_meta_version, 'The version of the ADM.', 'STR', 'v0.0', ion_ltpadmin_meta_version_did);

CALL SP__insert_obj_metadata(0, 'organization', dtn_namespace_id, ion_ltpadmin_meta_organization);
CALL SP__insert_const_actual_definition(ion_ltpadmin_meta_organization, 'The name of the issuing organization of the ADM.', 'STR', 'JHUAPL', ion_ltpadmin_meta_organization_did);

-- #EDD
CALL SP__insert_obj_metadata(2, 'ion_version', dtn_namespace_id, ion_ltpadmin_edd_ion_version);
CALL SP__insert_edd_formal_definition(ion_ltpadmin_edd_ion_version, 'This is the version of ION that is currently installed.', NULL, 'STR', ion_ltpadmin_edd_ion_version_did);
CALL SP__insert_edd_actual_definition(ion_ltpadmin_edd_ion_version, 'The singleton value for ion_version', NULL, ion_ltpadmin_edd_ion_version_aid);

-- #OPER

-- #VAR

-- #TBLT
CALL SP__insert_obj_metadata(10, 'spans', dtn_namespace_id, ion_ltpadmin_tblt_spans);
CALL SP__insert_tnvc_collection('columns for the spans table', tbl_tnvc_id);
CALL SP__insert_tnvc_uvast_entry(tbl_tnvc_id, 1, 'peer_engine_nbr', null, tnvc_entry);
CALL SP__insert_tnvc_uint_entry(tbl_tnvc_id, 2, 'max_export_sessions', null, tnvc_entry);
CALL SP__insert_tnvc_uint_entry(tbl_tnvc_id, 3, 'max_import_sessions', null, tnvc_entry);
CALL SP__insert_tnvc_uint_entry(tbl_tnvc_id, 4, 'max_segment_size', null, tnvc_entry);
CALL SP__insert_tnvc_uint_entry(tbl_tnvc_id, 5, 'aggregation_size_limit', null, tnvc_entry);
CALL SP__insert_tnvc_uint_entry(tbl_tnvc_id, 6, 'aggregation_time_limit', null, tnvc_entry);
CALL SP__insert_tnvc_str_entry(tbl_tnvc_id, 7, 'lso_control', null, tnvc_entry);
CALL SP__insert_tnvc_uint_entry(tbl_tnvc_id, 8, 'queueing_latency', null, tnvc_entry);
CALL SP__insert_table_template_actual_definition(ion_ltpadmin_tblt_spans, 'This table lists all spans of potential LTP data interchange that exists between the local LTP engine and the indicated (neighboring) LTP engine.', tbl_tnvc_id, ion_ltpadmin_tblt_spans_did);


-- #RPTT

-- #CTRL
CALL SP__insert_obj_metadata(1, 'manage_heap', dtn_namespace_id, ion_ltpadmin_ctrl_manage_heap);
CALL SP__insert_formal_parmspec(1, 'parms for the manage_heap control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'max_database_heap_per_block', 'UINT', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ltpadmin_ctrl_manage_heap , 'This control declares the maximum number of bytes of SDR heap space that will be occupied by the acquisition of any single LTP block. All data acquired in excess of this limit will be written to a temporary file pending extraction and dispatching of the acquired block. Default is the minimum allowed value (560 bytes), which is the approximate size of a ZCO file reference object; this is the minimum SDR heap space occupancy in the event that all acquisition is into a file.', fp_spec_id, ion_ltpadmin_ctrl_manage_heap_did);

CALL SP__insert_obj_metadata(1, 'manage_max_ber', dtn_namespace_id, ion_ltpadmin_ctrl_manage_max_ber);
CALL SP__insert_formal_parmspec(1, 'parms for the manage_max_ber control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'max_expected_bit_error_rate', 'REAL32', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ltpadmin_ctrl_manage_max_ber , 'This control sets the expected maximum bit error rate(BER) that LTP should provide for in computing the maximum number of transmission efforts to initiate in the transmission of a given block.(Note that this computation is also sensitive to data segment size and to the size of the block that is to be transmitted.) The default value is .0001 (10^-4).', fp_spec_id, ion_ltpadmin_ctrl_manage_max_ber_did);

CALL SP__insert_obj_metadata(1, 'manage_own_queue_time', dtn_namespace_id, ion_ltpadmin_ctrl_manage_own_queue_time);
CALL SP__insert_formal_parmspec(1, 'parms for the manage_own_queue_time control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'own_queing_latency', 'UINT', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ltpadmin_ctrl_manage_own_queue_time , 'This control sets the number of seconds of predicted additional latency attributable to processing delay within the local engine itself that should be included whenever LTP computes the nominal round-trip time for an exchange of data with any remote engine.The default value is 1.', fp_spec_id, ion_ltpadmin_ctrl_manage_own_queue_time_did);

CALL SP__insert_obj_metadata(1, 'manage_screening', dtn_namespace_id, ion_ltpadmin_ctrl_manage_screening);
CALL SP__insert_formal_parmspec(1, 'parms for the manage_screening control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'new_state', 'UINT', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ltpadmin_ctrl_manage_screening , 'This control enables or disables the screening of received LTP segments per the periods of scheduled reception in the node''s contact graph. By default, screening is disabled. When screening is enabled, such segments are silently discarded. Note that when screening is enabled the ranges declared in the contact graph must be accurate and clocks must be synchronized; otherwise, segments will be arriving at times other than the scheduled contact intervals and will be discarded.', fp_spec_id, ion_ltpadmin_ctrl_manage_screening_did);

CALL SP__insert_obj_metadata(1, 'span_add', dtn_namespace_id, ion_ltpadmin_ctrl_span_add);
CALL SP__insert_formal_parmspec(8, 'parms for the span_add control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'peer_engine_number', 'UVAST', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 2, 'max_export_sessions', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 3, 'max_import_sessions', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 4, 'max_segment_size', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 5, 'aggregtion_size_limit', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 6, 'aggregation_time_limit', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 7, 'lso_control', 'STR', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 8, 'queuing_latency', 'UINT', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ltpadmin_ctrl_span_add , 'This control declares that a span of potential LTP data interchange exists between the local LTP engine and the indicated (neighboring) LTP engine.', fp_spec_id, ion_ltpadmin_ctrl_span_add_did);

CALL SP__insert_obj_metadata(1, 'span_change', dtn_namespace_id, ion_ltpadmin_ctrl_span_change);
CALL SP__insert_formal_parmspec(8, 'parms for the span_change control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'peer_engine_number', 'UVAST', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 2, 'max_export_sessions', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 3, 'max_import_sessions', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 4, 'max_segment_size', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 5, 'aggregtion_size_limit', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 6, 'aggregation_time_limit', 'UINT', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 7, 'lso_control', 'STR', null, r_fp_ent);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 8, 'queuing_latency', 'UINT', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ltpadmin_ctrl_span_change , 'This control sets the indicated span''s configuration parameters to the values provided as arguments', fp_spec_id, ion_ltpadmin_ctrl_span_change_did);

CALL SP__insert_obj_metadata(1, 'span_del', dtn_namespace_id, ion_ltpadmin_ctrl_span_del);
CALL SP__insert_formal_parmspec(1, 'parms for the span_del control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'peer_engine_number', 'UVAST', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ltpadmin_ctrl_span_del , 'This control deletes the span identified by peerEngineNumber. The control will fail if any outbound segments for this span are pending transmission or any inbound blocks from the peer engine are incomplete.', fp_spec_id, ion_ltpadmin_ctrl_span_del_did);

CALL SP__insert_obj_metadata(1, 'stop', dtn_namespace_id, ion_ltpadmin_ctrl_stop);
CALL SP__insert_control_formal_definition(ion_ltpadmin_ctrl_stop , 'This control stops all link service input and output tasks for the local LTP engine.', null, ion_ltpadmin_ctrl_stop_did);

CALL SP__insert_obj_metadata(1, 'watch_set', dtn_namespace_id, ion_ltpadmin_ctrl_watch_set);
CALL SP__insert_formal_parmspec(1, 'parms for the watch_set control', fp_spec_id);
CALL SP__insert_formal_parmspec_entry(fp_spec_id, 1, 'activity', 'STR', null, r_fp_ent);
CALL SP__insert_control_formal_definition(ion_ltpadmin_ctrl_watch_set , 'This control enables and disables production of a continuous stream of user- selected LTP activity indication characters. Activity parameter of 1 selects all LTP activity indication characters; 0 de-selects all LTP activity indication characters; any other activitySpec such as df{] selects all activity indication characters in the string, de-selecting all others. LTP will print each selected activity indication character to stdout every time a processing event of the associated type occurs: d bundle appended to block for next session, e segment of block is queued for transmission, f block has been fully segmented for transmission, g segment popped from transmission queue, h positive ACK received for block and session ended, s segment received, t block has been fully received,  negative ACK received for block and segments retransmitted, = unacknowledged checkpoint was retransmitted, + unacknowledged report segment was retransmitted, { export session canceled locally (by sender), } import session canceled by remote sender, [ import session canceled locally (by receiver), ] export session canceled by remote receiver', fp_spec_id, ion_ltpadmin_ctrl_watch_set_did);


-- #CONST

-- #MAC
END 
$do$