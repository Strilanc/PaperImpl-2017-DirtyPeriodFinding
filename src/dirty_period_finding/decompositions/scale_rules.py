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

from dirty_period_finding.gates import (
    OffsetGate,
    ScaleGate,
    Negate,
)


def do_scale(gate, target_reg, controls):
    """
    Args:
        gate (ScaleGate):
            The gate being decomposed (contains factor/modulus info).
        target_reg (projectq.types.Qureg):
            The register to scaled-add into.
        controls (list[Qubit]):
            Control qubits.
    """

    n = len(target_reg)
    factor = gate.net_factor_for_size(n)

    # Trivial cases.
    if factor == 1:
        return
    if factor == -1:
        Negate & controls | target_reg
        return

    plus_scale = OffsetGate(factor >> 1) & controls
    for i in range(n)[::-1]:
        plus_scale & target_reg[i] | target_reg[i + 1:]


decompose_scale = DecompositionRule(
    gate_class=ScaleGate,
    gate_decomposer=lambda cmd: do_scale(
        cmd.gate,
        target_reg=cmd.qubits[0],
        controls=cmd.control_qubits))


all_defined_decomposition_rules = [
    decompose_scale,
]
