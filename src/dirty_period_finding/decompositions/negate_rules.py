# -*- coding: utf-8 -*-

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals

from projectq.cengines import DecompositionRule

from dirty_period_finding.gates import MultiNot, Increment, NegateGate


def do_negate(target_reg, controls):
    """
    Args:
        target_reg (projectq.types.Qureg):
            The register to negate.
        controls (list[Qubit]):
            Control qubits.
    """
    MultiNot & controls | target_reg
    Increment & controls | target_reg


decompose_negate = DecompositionRule(
    gate_class=NegateGate,
    gate_decomposer=lambda cmd: do_negate(
        target_reg=cmd.qubits[0],
        controls=cmd.control_qubits))


all_defined_decomposition_rules = [
    decompose_negate,
]
