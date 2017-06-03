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

import fractions

from projectq import MainEngine
from projectq.cengines import DummyEngine, DecompositionRuleSet
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    modular_bimultiplication_rules,
    multi_not_rules,
    addition_rules,
    increment_rules,
    pivot_flip_rules,
    modular_scaled_addition_rules,
    modular_addition_rules,
    offset_rules,
    modular_double_rules,
    rotate_bits_rules,
    reverse_bits_rules,
    comparison_rules,
    modular_negate_rules,
)
from dirty_period_finding.decompositions.modular_bimultiplication_rules import (
    decompose_into_adds_and_rotate,
)
from dirty_period_finding.extensions import (
    AutoReplacerEx,
    LimitedCapabilityEngine,
)
from dirty_period_finding.gates import (
    ModularBimultiplicationGate,
)
from .._test_util import (
    decomposition_to_ascii,
    cover,
    check_permutation_decomposition,
)


def test_toffoli_size_of_bimultiplication():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            swap2cnot,
            multi_not_rules,
            addition_rules,
            increment_rules,
            modular_addition_rules,
            modular_bimultiplication_rules,
            modular_scaled_addition_rules,
            pivot_flip_rules,
            offset_rules,
            modular_double_rules,
            rotate_bits_rules,
            reverse_bits_rules,
            modular_negate_rules,
            comparison_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])

    t1 = eng.allocate_qureg(5)
    t2 = eng.allocate_qureg(5)
    controls = eng.allocate_qureg(1)
    modulus = 29
    factor = 17

    ModularBimultiplicationGate(factor, modulus) & controls | (t1, t2)

    assert 5000 < len(rec.received_commands) < 10000


def test_bimultiplication_operation():
    assert ModularBimultiplicationGate(7, 13).do_operation(1, 1) == (7, 2)
    assert ModularBimultiplicationGate(7, 13).do_operation(2, 3) == (1, 6)


def test_decompose_scaled_modular_addition_into_doubled_addition():
    for register_size in cover(100, min=1):
        for control_size in cover(3):
            for h_modulus in cover(1 << (register_size - 1)):
                modulus = h_modulus * 2 + 1
                for factor in cover(modulus):
                    if fractions.gcd(modulus, factor) != 1 or factor == 0:
                        continue

                    check_permutation_decomposition(
                        decomposition_rule=decompose_into_adds_and_rotate,
                        gate=ModularBimultiplicationGate(factor, modulus),
                        register_sizes=[register_size, register_size],
                        control_size=control_size,
                        register_limits=[modulus, modulus])


def test_diagram_decompose_into_doubled_addition():
    text_diagram = decomposition_to_ascii(
        gate=ModularBimultiplicationGate(7, 13),
        decomposition_rule=decompose_into_adds_and_rotate,
        register_sizes=[4, 4],
        control_size=1)
    print(text_diagram)
    assert text_diagram == """
|0>--------@---------------@----------------@------------@------------@--------
    .------|------. .------|-------. .------|------. .---|----.       |
|0>-|             |-|              |-|             |-|        |-------|--------
    |             | |              | |             | |        |       |
|0>-|             |-|              |-|             |-|        |-------|--------
    |             | |              | |             | |        |       |
|0>-|      A      |-|  +A*11 % 13  |-|      A      |-|        |-------|--------
    |             | |              | |             | |        |       |
|0>-|             |-|              |-|             |-|        |-------|--------
    |-------------| |--------------| |-------------| |        | .-----|------.
|0>-|             |-|              |-|             |-|  <<<4  |-|            |-
    |             | |              | |             | |        | |            |
|0>-|             |-|              |-|             |-|        |-|            |-
    |             | |              | |             | |        | |            |
|0>-|  +A*7 % 13  |-|      A       |-|  +A*7 % 13  |-|        |-|  *-1 % 13  |-
    |             | |              | |             | |        | |            |
|0>-|             |-|              |-|             |-|        |-|            |-
    `-------------` `--------------` `-------------` `--------` `------------`
    """.strip()
