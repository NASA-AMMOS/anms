#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 The Johns Hopkins University Applied Physics
# Laboratory LLC.
#
# This file is part of the Asynchronous Network Management System (ANMS).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This work was performed for the Jet Propulsion Laboratory, California
# Institute of Technology, sponsored by the United States Government under
# the prime contract 80NM0018D0004 between the Caltech and NASA under
# subcontract 1658085.
#

# Internal modules
import ace
import ace.models

# Helper function to check if a docker container image is up or not.

ACCEPT_FILE_CONTENT_TYPE = "application/json"

class AdmCompare:
  ''' Utility class to compare two ADMs structurally for allowed changes.
  '''
  def __init__(self, adm_set: ace.AdmSet):
    self._adm_set = adm_set
    self._errs = []

  def get_errors(self):
    return self._errs

  def compare_adms(self, old_adm: ace.models.AdmModule, new_adm: ace.models.AdmModule) -> bool:
    ''' Gurantee no structural changes, only new objects or allowed doc changes.

    :return: Any specific errors if the new ADM is not acceptable.
    '''
    child_cls = [
      ['const', ace.models.Const, self.compare_const],
      ['ctrl', ace.models.Ctrl, self.compare_ctrl],
      ['edd', ace.models.Edd, self.compare_edd],
      ['mac', ace.models.Mac, self.compare_mac],
      ['oper', ace.models.Oper, self.compare_oper],
      ['rptt', ace.models.Rptt, self.compare_rptt],
      ['tblt', ace.models.Tblt, self.compare_tblt],
      ['var', ace.models.Var, self.compare_var],
    ]


    for attrname, cls, compare in child_cls:
      for old_obj in getattr(old_adm, attrname):
        new_obj = self._adm_set.get_child(new_adm, cls, norm_name=old_obj.norm_name)
        if new_obj:
          compare(old_obj, new_obj)
        else:
          self._add_err(old_obj, 'object removed from new ADM')

    return not bool(self._errs)

  def _add_err(self, old_obj, msg):
    cls_name = type(old_obj).__name__
    new_error= {"obj_type": cls_name, "name": old_obj.norm_name, "issue": msg }
    self._errs.append(new_error)

  def _compare_attr(self, old_obj, new_obj, attrname):
    old_val = getattr(old_obj, attrname)
    new_val = getattr(new_obj, attrname)
    if old_val != new_val:
      self._add_err(old_obj, f'changed {attrname} value from {old_val} to {new_val}')

  def _compare_ac(self, old_obj, new_obj, attrname):
    old_val = getattr(old_obj, attrname)
    new_val = getattr(new_obj, attrname)
    if len(old_val.items) != len(new_val.items):
      self._add_err(old_obj, f'changed AC list size')
    for old_ari, new_ari in zip(old_val.items, new_val.items):
      if not self._ari_equal(old_ari, new_ari):
        self._add_err(old_obj, f'changed #{old_ari.position + 1} ARI value from {old_ari} to {new_ari}')

  def _ari_equal(self, old_ari, new_ari) -> bool:
      if old_ari.ns != new_ari.ns:
          return False
      if old_ari.nm != new_ari.nm:
          return False
      return True

  def _compare_tnl(self, old_obj, new_obj, attrname):
      old_val = getattr(old_obj, attrname)
      new_val = getattr(new_obj, attrname)
      if len(old_val.items) != len(new_val.items):
        self._add_err(old_obj, f'changed type/name list size')
      for old_tn, new_tn in zip(old_val.items, new_val.items):
        if old_tn.type != new_tn.type:
          self._add_err(old_obj, f'changed #{old_tn.position + 1} type from {old_tn.type} to {new_tn.type}')

  def compare_const(self, old_obj, new_obj):
    self._compare_attr(old_obj, new_obj, 'enum')
    self._compare_attr(old_obj, new_obj, 'type')

  def compare_ctrl(self, old_obj, new_obj):
    self._compare_attr(old_obj, new_obj, 'enum')

  def compare_edd(self, old_obj, new_obj):
    self._compare_attr(old_obj, new_obj, 'enum')
    self._compare_attr(old_obj, new_obj, 'type')

  def compare_mac(self, old_obj, new_obj):
    self._compare_attr(old_obj, new_obj, 'enum')
    # The action doesn't affect the manager

  def compare_oper(self, old_obj, new_obj):
    self._compare_attr(old_obj, new_obj, 'enum')
    # The result_type and in_type don't affect the manager

  def compare_rptt(self, old_obj, new_obj):
    self._compare_attr(old_obj, new_obj, 'enum')
    self._compare_ac(old_obj, new_obj, 'definition')

  def compare_tblt(self, old_obj, new_obj):
    self._compare_attr(old_obj, new_obj, 'enum')
    self._compare_tnl(old_obj, new_obj, 'columns')

  def compare_var(self, old_obj, new_obj):
    self._compare_attr(old_obj, new_obj, 'enum')
    self._compare_attr(old_obj, new_obj, 'type')
    # The initializer doesn't affect the manager