# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule

from dirty_period_finding.gates import (
    ModularOffsetGate,
    ModularAdditionGate,
    ConstPivotFlipGate,
    PivotFlip,
    MultiNot,
    OffsetGate,
    Subtract,
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
    assert 1 << (n - 1) < gate.modulus <= 1 << n

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
    assert 1 << (n - 1) < gate.modulus <= 1 << n

    MultiNot & controls | input_reg
    OffsetGate(gate.modulus + 1) & controls | input_reg
    PivotFlip | (input_reg, target_reg)

    # It's fine if we also flip the half above the modulus.
    OffsetGate(-gate.modulus) & controls | target_reg
    MultiNot & controls | target_reg

    MultiNot & controls | input_reg
    OffsetGate(gate.modulus + 1) & controls | input_reg
    PivotFlip | (input_reg, target_reg)


all_defined_decomposition_rules = [
    DecompositionRule(
        gate_class=ModularOffsetGate,
        gate_decomposer=lambda cmd: do_modular_offset(
            cmd.gate,
            target_reg=cmd.qubits[0],
            controls=cmd.control_qubits)),

    DecompositionRule(
        gate_class=ModularAdditionGate,
        gate_decomposer=lambda cmd: do_modular_addition(
            cmd.gate,
            input_reg=cmd.qubits[0],
            target_reg=cmd.qubits[1],
            controls=cmd.control_qubits)),
]
