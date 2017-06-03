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
    modular_addition_rules,
    pivot_flip_rules,
    offset_rules,
    addition_rules,
    increment_rules,
    multi_not_rules,
    comparison_rules,
)
from dirty_period_finding.decompositions.modular_addition_rules import (
    decompose_modular_offset,
    decompose_modular_addition,
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import (
    ModularAdditionGate,
    ModularOffsetGate,
)
from .._test_util import (
    cover,
    check_permutation_decomposition,
    decomposition_to_ascii,
)


def test_modular_offset_operation():
    assert ModularOffsetGate(2, 13).do_operation(234) == (234,)
    assert ModularOffsetGate(2, 13).do_operation(11) == (0,)
    assert ModularOffsetGate(5, 13).do_operation(11) == (3,)
    assert ModularOffsetGate(5, 13).do_operation(1) == (6,)


def test_modular_addition_operation():
    assert ModularAdditionGate(13).do_operation(3, 11) == (3, 1)
    assert ModularAdditionGate(13).do_operation(3, 17) == (3, 17)
    assert ModularAdditionGate(13).do_operation(17, 3) == (17, 3)
    assert ModularAdditionGate(13).do_operation(2, 4) == (2, 6)


def test_toffoli_size_of_modular_addition():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            pivot_flip_rules,
            offset_rules,
            addition_rules,
            swap2cnot,
            increment_rules,
            multi_not_rules,
            modular_addition_rules,
            comparison_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(15)
    target1 = eng.allocate_qureg(16)
    target2 = eng.allocate_qureg(16)
    modulus = 0xAEFD

    ModularAdditionGate(modulus) & controls | (target1, target2)

    assert 10000 < len(rec.received_commands) < 15000


def test_toffoli_size_of_modular_offset():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            pivot_flip_rules,
            offset_rules,
            addition_rules,
            swap2cnot,
            increment_rules,
            multi_not_rules,
            modular_addition_rules,
            comparison_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(15)
    target = eng.allocate_qureg(16)
    dirty = eng.allocate_qureg(2)
    modulus = 0xAEFD
    offset = 0x9E0A

    ModularOffsetGate(offset, modulus) & controls | target

    assert dirty is not None
    assert 5000 < len(rec.received_commands) < 15000


def test_decompose_modular_addition():
    for register_size in cover(100, min=1):
        for control_size in range(3):
            for h_modulus in cover((1 << register_size) - 1):
                modulus = h_modulus + 1

                check_permutation_decomposition(
                    decomposition_rule=decompose_modular_addition,
                    gate=ModularAdditionGate(modulus),
                    register_sizes=[register_size, register_size],
                    control_size=control_size,
                    register_limits=[modulus, modulus])


def test_decompose_modular_offset():
    for register_size in cover(100, min=1):
        for control_size in range(3):
            for h_modulus in cover(1 << register_size):
                modulus = h_modulus + 1
                for offset in cover(modulus):

                    check_permutation_decomposition(
                        decomposition_rule=decompose_modular_offset,
                        gate=ModularOffsetGate(offset, modulus),
                        register_sizes=[register_size],
                        control_size=control_size,
                        register_limits=[modulus])


def test_diagram_decompose_modular_addition():
    text_diagram = decomposition_to_ascii(
        gate=ModularAdditionGate(51),
        decomposition_rule=decompose_modular_addition,
        register_sizes=[6, 6],
        control_size=1)
    print(text_diagram)
    assert text_diagram == """
|0>-@-----@----------------------@-----@-----@------------------
    | .---|---. .----------.     |     | .---|---. .----------.
|0>-X-|       |-|          |-----|-----X-|       |-|          |-
    | |       | |          |     |     | |       | |          |
|0>-X-|       |-|          |-----|-----X-|       |-|          |-
    | |       | |          |     |     | |       | |          |
|0>-X-|       |-|          |-----|-----X-|       |-|          |-
    | |       | |          |     |     | |       | |          |
|0>-X-|  +52  |-|    A     |-----|-----X-|  +52  |-|    A     |-
    | |       | |          |     |     | |       | |          |
|0>-X-|       |-|          |-----|-----X-|       |-|          |-
    | |       | |          |     |     | |       | |          |
|0>-X-|       |-|          |-----|-----X-|       |-|          |-
      `-------` |----------| .---|---. | `-------` |----------|
|0>-------------|          |-|       |-X-----------|          |-
                |          | |       | |           |          |
|0>-------------|          |-|       |-X-----------|          |-
                |          | |       | |           |          |
|0>-------------|          |-|       |-X-----------|          |-
                |          | |       | |           |          |
|0>-------------|  Flip<A  |-|  -51  |-X-----------|  Flip<A  |-
                |          | |       | |           |          |
|0>-------------|          |-|       |-X-----------|          |-
                |          | |       | |           |          |
|0>-------------|          |-|       |-X-----------|          |-
                `----------` `-------`             `----------`
        """.strip()


def test_diagram_decompose_modular_offset():
    text_diagram = decomposition_to_ascii(
        gate=ModularOffsetGate(13, 51),
        decomposition_rule=decompose_modular_offset,
        register_sizes=[6],
        control_size=1)
    print(text_diagram)
    assert text_diagram == """
|0>-------@-----------@-----@-------@-------
    .-----|-----. .---|---. | .-----|-----.
|0>-|           |-|       |-X-|           |-
    |           | |       | | |           |
|0>-|           |-|       |-X-|           |-
    |           | |       | | |           |
|0>-|           |-|       |-X-|           |-
    |           | |       | | |           |
|0>-|  Flip<38  |-|  -51  |-X-|  Flip<13  |-
    |           | |       | | |           |
|0>-|           |-|       |-X-|           |-
    |           | |       | | |           |
|0>-|           |-|       |-X-|           |-
    `-----------` `-------`   `-----------`
        """.strip()
