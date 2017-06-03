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

from __future__ import division
from __future__ import unicode_literals

from projectq import MainEngine
from projectq.cengines import DummyEngine, DecompositionRuleSet
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import multi_not_rules
from dirty_period_finding.decompositions import (
    reverse_bits_rules,
    rotate_bits_rules,
)
from dirty_period_finding.decompositions.rotate_bits_rules import (
    decompose_into_reverses,
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import RotateBitsGate
from .._test_util import (
    decomposition_to_ascii,
    check_permutation_decomposition,
    cover,
)


def test_toffoli_size_of_bit_rotate():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            swap2cnot,
            multi_not_rules,
            reverse_bits_rules,
            rotate_bits_rules
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(50)
    target = eng.allocate_qureg(100)

    RotateBitsGate(-3) & controls | target
    RotateBitsGate(+1) & controls | target[1:]

    assert 500 < len(rec.received_commands) < 5000


def test_rotate_operation():
    assert RotateBitsGate(-1).do_operation((7,), (0b1011001,)) == (0b1101100,)
    assert RotateBitsGate(0).do_operation((7,), (0b1011001,)) == (0b1011001,)
    assert RotateBitsGate(1).do_operation((7,), (0b1011001,)) == (0b0110011,)
    assert RotateBitsGate(2).do_operation((7,), (0b1011001,)) == (0b1100110,)
    assert RotateBitsGate(3).do_operation((7,), (0b1011001,)) == (0b1001101,)
    assert RotateBitsGate(4).do_operation((7,), (0b1011001,)) == (0b0011011,)
    assert RotateBitsGate(5).do_operation((7,), (0b1011001,)) == (0b0110110,)
    assert RotateBitsGate(6).do_operation((7,), (0b1011001,)) == (0b1101100,)
    assert RotateBitsGate(7).do_operation((7,), (0b1011001,)) == (0b1011001,)


def test_decompose_into_reverses():
    for register_size in cover(100, min=1):
        for control_size in cover(3):
            for rotation in cover(register_size):

                check_permutation_decomposition(
                    decomposition_rule=decompose_into_reverses,
                    gate=RotateBitsGate(rotation),
                    register_sizes=[register_size],
                    control_size=control_size)


def test_diagram_decompose_into_reverses():
    text_diagram = decomposition_to_ascii(
        gate=RotateBitsGate(2),
        decomposition_rule=decompose_into_reverses,
        register_sizes=[9],
        control_size=3)
    print(text_diagram)
    assert text_diagram == """
|0>-------@-------------@-------------@-------
          |             |             |
|0>-------@-------------@-------------@-------
          |             |             |
|0>-------@-------------@-------------@-------
    .-----|-----. .-----|-----.       |
|0>-|           |-|           |-------|-------
    |           | |           |       |
|0>-|           |-|  Reverse  |-------|-------
    |           | `-----------` .-----|-----.
|0>-|           |---------------|           |-
    |           |               |           |
|0>-|           |---------------|           |-
    |           |               |           |
|0>-|  Reverse  |---------------|           |-
    |           |               |           |
|0>-|           |---------------|  Reverse  |-
    |           |               |           |
|0>-|           |---------------|           |-
    |           |               |           |
|0>-|           |---------------|           |-
    |           |               |           |
|0>-|           |---------------|           |-
    `-----------`               `-----------`
        """.strip()
