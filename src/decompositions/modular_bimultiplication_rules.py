# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from ..gates import (
    ModularBimultiplicationGate,
    ModularScaledAdditionGate,
    RotateBitsGate
)


def do_bimultiplication(gate, forward_reg, inverse_reg, controls):
    """
    Reversibly multiplies one register by a constant and another register by
    the negation of the modular multiplicative inverse of that constant.

    N: len(input_reg) + len(target_reg) + len(controls)
    Size: O(N lg N)
    Depth: O(N)
    Diagram:
        c                   c
       ━/━━━━━●━━━━        ━/━━━━━●━━━━━━━●━━━━━━━●━━━━━━━━●━━━
        n ┌───┴───┐         n  ┌──┴──┐┌───┴───┐┌──┴──┐  ┌──┴──┐
       ━/━┥ ×K%R  ┝━   =   ━/━━┥  A  ┝┥-AK⁻¹%R┝┥  A  ┝━━┥━╲ ╱━┝━
        n ├───────┤         n  ├─────┤├───────┤├─────┤  │  ╳  │
       ━/━┥×-K⁻¹%R┝━       ━/━━┥+AK%R┝┥   A   ┝┥+AK%R┝━━┥━╱ ╲━┝━
          └───────┘            └─────┘└───────┘└─────┘  └─────┘
    Args:
        gate (ModularBimultiplicationGate):
            The gate being decomposed.
        forward_reg (projectq.types.Qureg):
            The register to mod-multiply by the forward factor.
        inverse_reg (projectq.types.Qureg):
            The register to mod-multiply by the inverse factor.
        controls (list[Qubit]):
            Control qubits.
    """
    n = len(forward_reg)
    assert len(inverse_reg) == n
    assert 1 << (n - 1) < gate.modulus <= 1 << n

    scale_add = ModularScaledAdditionGate(gate.factor, gate.modulus)
    scale_sub = ModularScaledAdditionGate(-gate.inverse_factor, gate.modulus)

    scale_add & controls | (forward_reg, inverse_reg)
    scale_sub & controls | (inverse_reg, forward_reg)
    scale_add & controls | (forward_reg, inverse_reg)

    RotateBitsGate(n) & controls | forward_reg + inverse_reg


all_defined_decomposition_rules = [
    DecompositionRule(
        gate_class=ModularBimultiplicationGate,
        gate_decomposer=lambda cmd: do_bimultiplication(
            cmd.gate,
            forward_reg=cmd.qubits[0],
            inverse_reg=cmd.qubits[1],
            controls=cmd.control_qubits)),
]
