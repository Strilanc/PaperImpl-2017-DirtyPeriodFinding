# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule

from dirty_period_finding.gates import (
    ModularScaledAdditionGate,
    ModularDoubleGate,
    ModularUndoubleGate,
    ModularOffsetGate,
)


def do_modular_scaled_addition(gate, input_reg, target_reg, controls):
    """
    Reversibly adds one register, times a constant, into another of the same
    size.

    N: len(input_reg) + len(target_reg)
    C: len(controls)
    Size: O(N² lg N + NC????????????????????????????????????????)
    Depth: O(N² + NC)
    Diagram:
        c              c
       ━/━━━━●━━━     ━/━━━━━━━━━━━━━━●━━━━━━━━━━━●━━━━━━━━━━━●━━━━━━━━━━━━●━━
             │                        │           │           │            │
          ┌──┴──┐                     │           │           │            │
       ───┤     ├  =  ────────────────┼───────────┼───────────┼────────────●──
       n-3│     │     n-3             │           │             .`         │
       ━/━┥     ┝  =  ━/━━━━━━━━━━━━━━┿━━━━━━━━━━━┿━━━━━━━━━━━.━━━━━━━━━━━━┿━━
          │  A  │                     │           │         .`             │
       ───┤     ├  =  ────────────────┼───────────●───────────┼────────────┼──
          │     │                     │           │           │            │
       ───┤     ├  =  ────────────────●───────────┼───────────┼────────────┼──
          └──┬──┘                     │           │           │            │
        n ┌──┴──┐      n ┌────┐⊗n-1┌──┴─┐┌────┐┌──┴─┐┌────┐   │   ┌────┐┌──┴─┐
       ━/━┥+AK%R┝     ━/━┥÷2%R┝━━━━┥+K%R┝┥×2%R┝┥+K%R┝┥×2%R┝━ ... ━┥×2%R┝┥+K%R┝
          └─────┘        └────┘    └────┘└────┘└────┘└────┘       └────┘└────┘
    Args:
        gate (ModularScaledAdditionGate):
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
    assert 0 < gate.modulus <= 1 << n

    double = ModularDoubleGate(gate.modulus)
    halve = ModularUndoubleGate(gate.modulus)
    offset = ModularOffsetGate(gate.factor, gate.modulus)

    for _ in range(n - 1):
        halve | target_reg

    for i in range(n)[::-1]:
        if i != n - 1:
            double | target_reg
        offset & controls & input_reg[i] | target_reg


decompose_into_doubled_addition = DecompositionRule(
    gate_class=ModularScaledAdditionGate,
    gate_decomposer=lambda cmd: do_modular_scaled_addition(
        cmd.gate,
        input_reg=cmd.qubits[0],
        target_reg=cmd.qubits[1],
        controls=cmd.control_qubits))

all_defined_decomposition_rules = [
    decompose_into_doubled_addition,
]
