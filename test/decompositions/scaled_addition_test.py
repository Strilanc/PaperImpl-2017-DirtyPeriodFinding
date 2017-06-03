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

from dirty_period_finding.decompositions import (
    offset_rules,
    addition_rules,
    increment_rules,
    multi_not_rules,
    comparison_rules,
    scaled_addition_rules,
)
from dirty_period_finding.decompositions.scaled_addition_rules import (
    decompose_into_shifted_addition
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import ScaledAdditionGate
from .._test_util import (
    check_permutation_decomposition,
    cover,
    decomposition_to_ascii,
)


def test_toffoli_size_of_scaled_modular_addition():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            addition_rules,
            comparison_rules,
            increment_rules,
            multi_not_rules,
            offset_rules,
            scaled_addition_rules
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(15)
    target1 = eng.allocate_qureg(8)
    target2 = eng.allocate_qureg(8)
    factor = 0x9A

    ScaledAdditionGate(factor) & controls | (target1, target2)

    assert 1000 < len(rec.received_commands) < 2000


def test_scaled_modular_addition_operation():
    assert ScaledAdditionGate(3).do_operation((5, 5), (2, 9)) == (2, 15)
    assert ScaledAdditionGate(-2).do_operation((5, 5), (7, 9)) == (7, 27)


def test_decompose_into_shifted_addition():
    for register_size in cover(50, min=1):
        for control_size in cover(3):
            for factor in cover(1 << register_size, min=-1000):
                check_permutation_decomposition(
                    decomposition_rule=decompose_into_shifted_addition,
                    gate=ScaledAdditionGate(factor),
                    register_sizes=[register_size, register_size],
                    control_size=control_size)


def test_diagram_decompose_into_doubled_addition():
    text_diagram = decomposition_to_ascii(
        gate=ScaledAdditionGate(7),
        decomposition_rule=decompose_into_shifted_addition,
        register_sizes=[4, 4],
        control_size=1)
    print(text_diagram)
    assert text_diagram == """
|0>----@--------@--------@------@---
       |        |        |      |
|0>----@--------|--------|------|---
       |        |        |      |
|0>----|--------@--------|------|---
       |        |        |      |
|0>----|--------|--------@------|---
       |        |        |      |
|0>----|--------|--------|------@---
    .--|---.    |        |      |
|0>-|      |----|--------|------|---
    |      | .--|---.    |      |
|0>-|      |-|      |----|------|---
    |      | |      | .--|---.  |
|0>-|  +7  |-|  +7  |-|      |--|---
    |      | |      | |      | .|-.
|0>-|      |-|      |-|  +7  |-|+7|-
    `------` `------` `------` `--`
    """.strip()
