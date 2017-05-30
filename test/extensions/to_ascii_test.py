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

from projectq.ops import X, Swap
from projectq.types import Qureg, Qubit

from dirty_period_finding.extensions import (
    commands_to_ascii_circuit,
    CommandEx
)


def test_empty_circuit():
    assert commands_to_ascii_circuit([]) == ''


def test_addition_circuit():
    commands = []
    eng = None
    qs = [Qureg([Qubit(eng, idx=i)]) for i in range(10)]

    for i in reversed(range(10)):
        if i != 4:
            commands.append(CommandEx(eng, X, (qs[i],), controls=qs[4]))
    for i in range(4):
        commands.append(CommandEx(eng, X, (qs[5+i],), controls=qs[4]))
        commands.append(CommandEx(eng, Swap, (qs[4], qs[i]), controls=qs[5+i]))
    commands.append(CommandEx(eng, X, (qs[-1],), controls=qs[4]))
    for i in range(4)[::-1]:
        commands.append(CommandEx(eng, Swap, (qs[4], qs[i]), controls=qs[5+i]))
        commands.append(CommandEx(eng, X, (qs[5+i],), controls=qs[i]))
    for i in range(10):
        if i != 4:
            commands.append(CommandEx(eng, X, (qs[i],), controls=qs[4]))

    assert commands_to_ascii_circuit(commands) == '''
|0⟩─────────────────⊕───×───────────────────────────×─•─⊕─────────────────
                    │   │                           │ │ │
|0⟩───────────────⊕─┼───┼───×───────────────────×─•─┼─┼─┼─⊕───────────────
                  │ │   │   │                   │ │ │ │ │ │
|0⟩─────────────⊕─┼─┼───┼───┼───×───────────×─•─┼─┼─┼─┼─┼─┼─⊕─────────────
                │ │ │   │   │   │           │ │ │ │ │ │ │ │ │
|0⟩───────────⊕─┼─┼─┼───┼───┼───┼───×───×─•─┼─┼─┼─┼─┼─┼─┼─┼─┼─⊕───────────
              │ │ │ │   │   │   │   │   │ │ │ │ │ │ │ │ │ │ │ │
|0⟩─•─•─•─•─•─•─•─•─•─•─×─•─×─•─×─•─×─•─×─┼─×─┼─×─┼─×─┼─•─•─•─•─•─•─•─•─•─
    │ │ │ │ │         │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │         │ │ │ │ │
|0⟩─┼─┼─┼─┼─⊕─────────⊕─•─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─•─⊕─────────⊕─┼─┼─┼─┼─
    │ │ │ │               │ │ │ │ │ │ │ │ │ │ │ │ │               │ │ │ │
|0⟩─┼─┼─┼─⊕───────────────⊕─•─┼─┼─┼─┼─┼─┼─┼─┼─┼─•─⊕───────────────⊕─┼─┼─┼─
    │ │ │                     │ │ │ │ │ │ │ │ │                     │ │ │
|0⟩─┼─┼─⊕─────────────────────⊕─•─┼─┼─┼─┼─┼─•─⊕─────────────────────⊕─┼─┼─
    │ │                           │ │ │ │ │                           │ │
|0⟩─┼─⊕───────────────────────────⊕─•─┼─•─⊕───────────────────────────⊕─┼─
    │                                 │                                 │
|0⟩─⊕─────────────────────────────────⊕─────────────────────────────────⊕─
    '''.strip()
