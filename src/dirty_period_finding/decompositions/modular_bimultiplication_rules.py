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
    ModularBimultiplicationGate,
    ModularScaledAdditionGate,
    RotateBitsGate,
    ModularNegate,
)


def do_bimultiplication(gate, forward_reg, inverse_reg, controls):
    """
    Reversibly multiplies one register by a constant and another register by
    the modular multiplicative inverse of that constant.

    N: len(forward_reg) + len(inverse_reg) + len(controls)
    Size: O(N lg N)
    Depth: O(N)
    Diagram:
        c                  c
       ━/━━━━━●━━━        ━/━━━━━●━━━━━━━●━━━━━━━●━━━━━━●━━━━━━●━━━━
        n ┌───┴──┐         n  ┌──┴──┐┌───┴───┐┌──┴──┐┌──┴──┐   │
       ━/━┥ ×K%R ┝━   =   ━/━━┥  A  ┝┥-AK⁻¹%R┝┥  A  ┝┥━╲ ╱━┝━━━┿━━━━
        n ├──────┤         n  ├─────┤├───────┤├─────┤│  ╳  │┌──┴──┐
       ━/━┥×K⁻¹%R┝━       ━/━━┥+AK%R┝┥   A   ┝┥+AK%R┝┥━╱ ╲━┝┥×-1%R┝━
          └──────┘            └─────┘└───────┘└─────┘└─────┘└─────┘
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
    assert 0 < gate.modulus <= 1 << n

    scale_add = ModularScaledAdditionGate(gate.factor, gate.modulus)
    scale_sub = ModularScaledAdditionGate(-gate.inverse_factor, gate.modulus)

    scale_add & controls | (forward_reg, inverse_reg)
    scale_sub & controls | (inverse_reg, forward_reg)
    scale_add & controls | (forward_reg, inverse_reg)

    RotateBitsGate(n) & controls | forward_reg + inverse_reg
    ModularNegate(gate.modulus) & controls | inverse_reg

decompose_into_adds_and_rotate = DecompositionRule(
    gate_class=ModularBimultiplicationGate,
    gate_decomposer=lambda cmd: do_bimultiplication(
        cmd.gate,
        forward_reg=cmd.qubits[0],
        inverse_reg=cmd.qubits[1],
        controls=cmd.control_qubits))

all_defined_decomposition_rules = [
    decompose_into_adds_and_rotate,
]
