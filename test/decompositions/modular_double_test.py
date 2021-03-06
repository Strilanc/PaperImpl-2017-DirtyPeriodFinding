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
from projectq.cengines import DecompositionRuleSet, DummyEngine
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    modular_double_rules,
    pivot_flip_rules,
    addition_rules,
    increment_rules,
    multi_not_rules,
    offset_rules,
    rotate_bits_rules,
    reverse_bits_rules,
    comparison_rules,
)
from dirty_period_finding.decompositions.modular_double_rules import (
    decompose_into_align_and_rotate
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import (
    ModularDoubleGate,
    ModularUndoubleGate,
)
from .._test_util import (
    check_permutation_decomposition,
    cover,
    decomposition_to_ascii,
)


def test_toffoli_size_of_modular_double():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            modular_double_rules,
            pivot_flip_rules,
            offset_rules,
            addition_rules,
            swap2cnot,
            increment_rules,
            multi_not_rules,
            rotate_bits_rules,
            reverse_bits_rules,
            comparison_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(15)
    target = eng.allocate_qureg(16)
    dirty = eng.allocate_qureg(2)
    modulus = 0xAEFD

    ModularDoubleGate(modulus) & controls | target

    assert dirty is not None
    assert 2000 < len(rec.received_commands) < 4000


def test_operation():
    assert ModularDoubleGate(7).do_operation(0) == (0,)
    assert ModularDoubleGate(7).do_operation(1) == (2,)
    assert ModularDoubleGate(7).do_operation(2) == (4,)
    assert ModularDoubleGate(7).do_operation(3) == (6,)
    assert ModularDoubleGate(7).do_operation(4) == (1,)
    assert ModularDoubleGate(7).do_operation(5) == (3,)
    assert ModularDoubleGate(7).do_operation(6) == (5,)

    assert ModularUndoubleGate(7).do_operation(0) == (0,)
    assert ModularUndoubleGate(7).do_operation(2) == (1,)
    assert ModularUndoubleGate(7).do_operation(4) == (2,)
    assert ModularUndoubleGate(7).do_operation(6) == (3,)
    assert ModularUndoubleGate(7).do_operation(1) == (4,)
    assert ModularUndoubleGate(7).do_operation(3) == (5,)
    assert ModularUndoubleGate(7).do_operation(5) == (6,)


def test_decompose_modular_double_into_align_and_rotate():
    for register_size in cover(50):
        for control_size in cover(3):
            for h_modulus in cover((1 << register_size) // 2):
                modulus = h_modulus * 2 + 1

                check_permutation_decomposition(
                    decomposition_rule=decompose_into_align_and_rotate,
                    gate=ModularDoubleGate(modulus),
                    register_sizes=[register_size],
                    control_size=control_size,
                    register_limits=[modulus])


def test_diagram_decompose_into_align_and_rotate():
    text_diagram = decomposition_to_ascii(
        gate=ModularDoubleGate(27),
        decomposition_rule=decompose_into_align_and_rotate,
        register_sizes=[5],
        control_size=1)
    print(text_diagram)
    assert text_diagram == """
|0>-----@---------@-----@-----@------
    .---|---. .---|---. | .---|----.
|0>-|       |-|       |-|-|        |-
    |       | |       | | |        |
|0>-|       |-|       |-|-|        |-
    |       | |       | | |        |
|0>-|  -14  |-|  +14  |-|-|  <<<1  |-
    |       | |       | | |        |
|0>-|       |-|       |-|-|        |-
    |       | `---|---` | |        |
|0>-|       |-----@-----X-|        |-
    `-------`             `--------`
    """.strip()
