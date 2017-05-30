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

from __future__ import division
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule

from dirty_period_finding.gates import ReverseBits, RotateBitsGate


def do_rotation(target_reg, amount, controls):
    """
    Applies a phase gradient to a register.
    If the register has size n, each state |k⟩ will be phased by factor*k/2**n.

    N: len(target_reg)
    C: len(controls)
    Size: O(N + C)
    Depth: O(N + C)
    Diagram:
       n-k ┌─────┐  k          n-k ┌───────┐┌───────┐  k
       ━/━━┿━╲ ╱━┿━━/━         ━/━━┥       ┝┥Reverse┝━━/━
        k  │  ╳  │ n-k    =     k  │Reverse│├───────┤ n-k
       ━/━━┿━╱ ╲━┿━━/━         ━/━━┥       ┝┥Reverse┝━━/━
           └─────┘                 └───┬───┘└───┬───┘
        c     │                 c      │        │
       ━/━━━━━●━━━━━━━         ━/━━━━━━●━━━━━━━━●━━━━━━━━
    Args:
        target_reg (projectq.types.Qureg):
            The register storing the amount to phase proportional to.
        amount (int|float|fractions.Fraction):
            The amount to left-rotate by. Use negative numbers to right-rotate.
        controls (list[projectq.types.Qubit]):
            Qubits that condition the operation.
    """
    if len(target_reg) == 0:
        return
    amount %= len(target_reg)
    if amount == 0:
        return

    for t in [target_reg,
              target_reg[:amount],
              target_reg[amount:]]:
        ReverseBits & controls | t


decompose_into_reverses = DecompositionRule(
    gate_class=RotateBitsGate,
    gate_decomposer=lambda cmd: do_rotation(
        target_reg=cmd.qubits[0],
        controls=cmd.control_qubits,
        amount=cmd.gate.amount))


all_defined_decomposition_rules = [
    decompose_into_reverses,
]
