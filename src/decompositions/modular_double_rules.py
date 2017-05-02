# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from ..extensions import X
from ..gates import (
    ModularBimultiplicationGate,
    ModularDoubleGate,
    ConstPivotFlipGate,
    OffsetGate,
    MultiNot,
    LeftRotateBits
)


def do_modular_double(gate, target_reg, controls):
    """
    Args:
        gate (ModularBimultiplicationGate):
            The gate being decomposed.
        target_reg (projectq.types.Qureg):
            The register to mod-multiply by the inverse factor.
        controls (list[Qubit]):
            Control qubits.
    """
    assert 1 << (len(target_reg) - 1) < gate.modulus <= 1 << len(target_reg)

    h = (gate.modulus + 1) // 2

    ConstPivotFlipGate(h) & controls | target_reg
    OffsetGate(-h) & controls | target_reg
    MultiNot & target_reg[-1] & controls | target_reg[:-1]
    X & controls | target_reg[-1]
    LeftRotateBits & controls | target_reg


all_defined_decomposition_rules = [
    DecompositionRule(
        gate_class=ModularDoubleGate,
        gate_decomposer=lambda cmd: do_modular_double(
            cmd.gate,
            target_reg=cmd.qubits[0],
            controls=cmd.control_qubits)),
]
