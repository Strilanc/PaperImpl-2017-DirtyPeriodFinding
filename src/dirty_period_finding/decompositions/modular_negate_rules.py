# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule

from dirty_period_finding.gates import (
    ModularNegate,
    ConstPivotFlipGate,
    Decrement,
    Increment
)


def do_modular_negate(gate, target_reg, controls):
    """
    Negates a register modular a constant.

    N: len(target_reg)
    C: len(controls)
    Size: O(N lg N + C)
    Depth: O(N + C)
    Diagram:
        c                 c
       ━/━━━━━●━━        ━/━━━━━━━━━━━●━━━━━━━━━
        n ┌───┴─┐         n  ┌──┐┌────┴───┐┌──┐
       ━/━┥×-1%R┝━       ━/━━┥-1┝┥Flip<R-1┝┥+1┝━
          └─────┘            └──┘└────────┘└──┘
    Args:
        gate (ModularNegate):
            The gate being decomposed.
        target_reg (projectq.types.Qureg):
            The register to negate.
        controls (list[Qubit]):
            Control qubits.
    """
    n = len(target_reg)
    assert 0 < gate.modulus <= 1 << n

    Decrement | target_reg
    ConstPivotFlipGate(gate.modulus - 1) & controls | target_reg
    Increment | target_reg


decompose_modular_negate = DecompositionRule(
    gate_class=ModularNegate,
    gate_decomposer=lambda cmd: do_modular_negate(
        cmd.gate,
        target_reg=cmd.qubits[0],
        controls=cmd.control_qubits))


all_defined_decomposition_rules = [
    decompose_modular_negate,
]
