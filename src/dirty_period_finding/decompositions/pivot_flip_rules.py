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

from dirty_period_finding.extensions import (
    min_workspace,
    workspace,
)
from dirty_period_finding.gates import (
    Add,
    ConstPivotFlipGate,
    MultiNot,
    OffsetGate,
    PivotFlipGate,
    Subtract,
    LessThanConstantGate,
)


def do_pivot_flip(pivot_reg, target_reg, controls, dirty_qubit):
    """
    Args:
        pivot_reg (projectq.types.Qureg):
            The register that determines which target stats get reversed.
        target_reg (projectq.types.Qureg):
            The register where states are reversed up to the pivot.
        controls (list[Qubit]):
            Control qubits.
        dirty_qubit (Qubit):
            Workspace.
    """
    for _ in range(2):
        # Compare.
        Subtract | (pivot_reg, target_reg + [dirty_qubit])
        Add | (pivot_reg, target_reg)

        # Conditioned double flip.
        Subtract & dirty_qubit & controls | (pivot_reg, target_reg)
        MultiNot & dirty_qubit & controls | target_reg


def do_const_pivot_flip(gate, target_reg, controls, dirty_qubit):
    """
    Args:
        gate (ConstPivotFlipGate):
            The gate being decomposed (contains pivot info).
        target_reg (projectq.types.Qureg):
            The register where states are reversed up to the pivot.
        controls (list[Qubit]):
            Control qubits.
        dirty_qubit (Qubit):
            Workspace.
    """
    # Trivial case: no-op.
    if gate.pivot <= 1:
        return

    for _ in range(2):
        # Compare.
        LessThanConstantGate(gate.pivot) | (target_reg, dirty_qubit)

        # Conditioned double flip.
        OffsetGate(-gate.pivot) & dirty_qubit & controls | target_reg
        MultiNot & dirty_qubit & controls | target_reg


all_defined_decomposition_rules = [
    DecompositionRule(
        gate_class=ConstPivotFlipGate,
        gate_recognizer=min_workspace(1),
        gate_decomposer=lambda cmd: do_const_pivot_flip(
            cmd.gate,
            target_reg=cmd.qubits[0],
            controls=cmd.control_qubits,
            dirty_qubit=workspace(cmd)[0])),

    DecompositionRule(
        gate_class=PivotFlipGate,
        gate_recognizer=min_workspace(1),
        gate_decomposer=lambda cmd: do_pivot_flip(
            pivot_reg=cmd.qubits[0],
            target_reg=cmd.qubits[1],
            controls=cmd.control_qubits,
            dirty_qubit=workspace(cmd)[0])),
]
