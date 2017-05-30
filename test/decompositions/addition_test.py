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

import random

from projectq import MainEngine
from projectq.cengines import (DummyEngine,
                               DecompositionRuleSet)
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    multi_not_rules,
    addition_rules,
    increment_rules
)
from dirty_period_finding.decompositions.addition_rules import (
    decompose_addition_controlled,
    decompose_addition_no_op,
    decompose_addition_single_input,
    decompose_addition_single_target,
    decompose_addition_uncontrolled,
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import (
    Add,
)
from .._test_util import (
    check_permutation_decomposition,
    cover,
    decomposition_to_ascii)


def test_toffoli_size_of_addition():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            addition_rules,
            increment_rules,
            multi_not_rules,
            swap2cnot,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    src = eng.allocate_qureg(50)
    dst = eng.allocate_qureg(100)
    Add | (src, dst)

    assert 5000 < len(backend.received_commands) < 7000


def test_decompose_addition_uncontrolled():
    for input_register_size in cover(50):
        for target_register_size in cover(50):
            check_permutation_decomposition(
                decomposition_rule=decompose_addition_uncontrolled,
                gate=Add,
                register_sizes=[input_register_size, target_register_size])


def test_decompose_addition_controlled():
    for input_register_size in cover(50):
        for target_register_size in cover(50):
            for control_size in cover(3):
                check_permutation_decomposition(
                    decomposition_rule=decompose_addition_controlled,
                    gate=Add,
                    register_sizes=[input_register_size, target_register_size],
                    control_size=control_size,
                    workspace=1)


def test_decompose_addition_no_op():
    for register_size in cover(50):
        a, b = register_size, 0
        for control_size in cover(3):
            if random.random() < 0.5:
                a, b = b, a
            check_permutation_decomposition(
                decomposition_rule=decompose_addition_no_op,
                gate=Add,
                register_sizes=[a, b],
                control_size=control_size)


def test_decompose_addition_single_target():
    for register_size in cover(50):
        for control_size in cover(3):
            if register_size:
                check_permutation_decomposition(
                    decomposition_rule=decompose_addition_single_target,
                    gate=Add,
                    register_sizes=[register_size, 1],
                    control_size=control_size)


def test_decompose_addition_single_input():
    for register_size in cover(50):
        for control_size in cover(3):
            if register_size and control_size:
                check_permutation_decomposition(
                    decomposition_rule=decompose_addition_single_input,
                    gate=Add,
                    register_sizes=[1, register_size],
                    control_size=control_size)


def test_diagram_decompose_addition_uncontrolled_same_size():
    text_diagram = decomposition_to_ascii(
        gate=Add,
        decomposition_rule=decompose_addition_uncontrolled,
        register_sizes=[6, 6])
    print(text_diagram)
    assert text_diagram == """
|0>-X---X-@---------------------------------------------------@-X-@-X-
    |   | |                                                   | | | |
|0>-X---|-|---X-@---------------------------------------@-X-@-|-|-|-X-
    |   | |   | |                                       | | | | | | |
|0>-X---|-|---|-|---X-@---------------------------@-X-@-|-|-|-|-|-|-X-
    |   | |   | |   | |                           | | | | | | | | | |
|0>-X---|-|---|-|---|-|---X-@---------------@-X-@-|-|-|-|-|-|-|-|-|-X-
    |   | |   | |   | |   | |               | | | | | | | | | | | | |
|0>-X---|-|---|-|---|-|---|-|---X-@---@-X-@-|-|-|-|-|-|-|-|-|-|-|-|-X-
    |   | |   | |   | |   | |   | |   | | | | | | | | | | | | | | | |
|0>-@-@-@-X-@-@-X-@-@-X-@-@-X-@-@-X-@-X-@-|-X-@-|-X-@-|-X-@-|-X-@-|-@-
    | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |
|0>-X-X-@-@-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-@-@-X-X-
    |       | | | | | | | | | | | | | | | | | | | | | | | | |       |
|0>-X-------X-@-@-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-@-@-X-------X-
    |             | | | | | | | | | | | | | | | | | | |             |
|0>-X-------------X-@-@-|-|-|-|-|-|-|-|-|-|-|-|-|-@-@-X-------------X-
    |                   | | | | | | | | | | | | |                   |
|0>-X-------------------X-@-@-|-|-|-|-|-|-|-@-@-X-------------------X-
    |                         | | | | | | |                         |
|0>-X-------------------------X-@-@-|-@-@-X-------------------------X-
    |                               |                               |
|0>-X-------------------------------X-------------------------------X-
        """.strip()


def test_diagram_decompose_addition_uncontrolled_larger_target():
    text_diagram = decomposition_to_ascii(
        gate=Add,
        decomposition_rule=decompose_addition_uncontrolled,
        register_sizes=[3, 6])
    print(text_diagram)
    assert text_diagram == """
|0>---------------------X-@----------------------@-X-@-
                        | |                      | | |
|0>---------------------|-|---X-@----------@-X-@-|-|-|-
                        | |   | |          | | | | | |
|0>----@--------@-----@-@-X-@-@-X----@-----X-@-|-X-@-|-
    .--|---.    |     | | | | | |    |     | | | | | |
|0>-|      |----|-----X-@-@-|-|-|----|-----|-|-|-@-@-X-
    |      |    |           | | |    |     | | |
|0>-|      |----|-----------X-@-@----|-----@-@-X-------
    |      | .--|---.             .--|---.
|0>-|      |-|      |-------------|      |-------------
    |      | |      |             |      |
|0>-|  −1  |-|      |-------------|      |-------------
    |      | |      |             |      |
|0>-|      |-|  +1  |-------------|  +1  |-------------
    |      | |      |             |      |
|0>-|      |-|      |-------------|      |-------------
    `------` `------`             `------`
        """.strip()


def test_diagram_decompose_addition_controlled():
    text_diagram = decomposition_to_ascii(
        gate=Add,
        decomposition_rule=decompose_addition_controlled,
        register_sizes=[3, 4],
        control_size=2,
        workspace=1)
    print(text_diagram)
    assert text_diagram == """
|0>--------------@----------@-
                 |          |
|0>--------------@----------@-
        .------. | .------. |
|0>-----|      |-|-|      |-|-
        |      | | |      | |
|0>-----|  A   |-|-|  A   |-|-
        |      | | |      | |
|0>-----|      |-|-|      |-|-
        |------| | |------| |
|0>-----|1     |-X-|1     |-X-
        |      | | |      | |
|0>-----|2     |-X-|2     |-X-
        |      | | |      | |
|0>-----|3 +A  |-X-|3 −A  |-X-
        |      | | |      | |
|0>-----|4     |-X-|4     |-X-
        |      | | |      | |
|0>-???-|0     |-X-|0     |-X-
        `------`   `------`
        """.strip()


def test_diagram_decompose_addition_single_target():
    text_diagram = decomposition_to_ascii(
        gate=Add,
        decomposition_rule=decompose_addition_single_target,
        register_sizes=[1, 1])
    print(text_diagram)
    assert text_diagram == """
|0>-@-
    |
|0>-X-
        """.strip()


def test_diagram_decompose_addition_single_input():
    text_diagram = decomposition_to_ascii(
        gate=Add,
        decomposition_rule=decompose_addition_single_input,
        register_sizes=[1, 3],
        control_size=2)
    print(text_diagram)
    assert text_diagram == """
|0>----@-----
       |
|0>----@-----
       |
|0>----@-----
    .--|---.
|0>-|      |-
    |      |
|0>-|  +1  |-
    |      |
|0>-|      |-
    `------`
        """.strip()


def test_diagram_decompose_addition_no_op():
    assert decomposition_to_ascii(
        gate=Add,
        decomposition_rule=decompose_addition_no_op,
        register_sizes=[3, 0]) == ''
    assert decomposition_to_ascii(
        gate=Add,
        decomposition_rule=decompose_addition_no_op,
        register_sizes=[0, 3]) == ''
