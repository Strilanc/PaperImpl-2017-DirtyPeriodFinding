# -*- coding: utf-8 -*-

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import unicode_literals

from projectq.cengines import DecompositionRule

from dirty_period_finding.gates import (
    ModularOffsetGate,
    ModularAdditionGate,
    ConstPivotFlipGate,
    PivotFlip,
    MultiNot,
    OffsetGate,
)


def do_modular_offset(gate, target_reg, controls):
    """
    Args:
        gate (ModularOffsetGate):
            The gate being decomposed (contains factor/modulus info).
        target_reg (projectq.types.Qureg):
            The register to scaled-add into.
        controls (list[Qubit]):
            Control qubits.
    """
    n = len(target_reg)
    assert 0 < gate.modulus <= 1 << n

    ConstPivotFlipGate(gate.modulus - gate.offset) & controls | target_reg

    # It's fine if we also flip the half above the modulus.
    OffsetGate(-gate.modulus) & controls | target_reg
    MultiNot & controls | target_reg

    ConstPivotFlipGate(gate.offset) & controls | target_reg


def do_modular_addition(gate, input_reg, target_reg, controls):
    """
    Args:
        gate (ModularAdditionGate):
            The gate being decomposed (contains factor/modulus info).
        input_reg (projectq.types.Qureg):
            The register to scaled-add from.
        target_reg (projectq.types.Qureg):
            The register to scaled-add into.
        controls (list[Qubit]):
            Control qubits.
    """
    n = len(input_reg)
    assert len(target_reg) == n
    assert 0 < gate.modulus < 1 << n

    MultiNot & controls | input_reg
    OffsetGate(gate.modulus + 1) & controls | input_reg
    PivotFlip | (input_reg, target_reg)

    # It's fine if we also flip the half above the modulus.
    OffsetGate(-gate.modulus) & controls | target_reg
    MultiNot & controls | input_reg + target_reg

    OffsetGate(gate.modulus + 1) & controls | input_reg
    PivotFlip | (input_reg, target_reg)


decompose_modular_offset = DecompositionRule(
    gate_class=ModularOffsetGate,
    gate_decomposer=lambda cmd: do_modular_offset(
        cmd.gate,
        target_reg=cmd.qubits[0],
        controls=cmd.control_qubits))

decompose_modular_addition = DecompositionRule(
    gate_class=ModularAdditionGate,
    gate_decomposer=lambda cmd: do_modular_addition(
        cmd.gate,
        input_reg=cmd.qubits[0],
        target_reg=cmd.qubits[1],
        controls=cmd.control_qubits))


all_defined_decomposition_rules = [
    decompose_modular_offset,
    decompose_modular_addition,
]
