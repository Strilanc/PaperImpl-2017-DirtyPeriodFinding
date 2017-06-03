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

from dirty_period_finding.decompositions import (
    addition_rules,
    comparison_rules,
    increment_rules,
    multi_not_rules,
    negate_rules,
    offset_rules,
    scale_rules,
)
from dirty_period_finding.decompositions.scale_rules import decompose_scale
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import (
    ScaleGate,
)
from .._test_util import (
    check_permutation_decomposition,
    cover,
    decomposition_to_ascii,
)


def test_toffoli_size_of_scale():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            addition_rules,
            comparison_rules,
            increment_rules,
            multi_not_rules,
            negate_rules,
            offset_rules,
            scale_rules,
            swap2cnot,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    src = eng.allocate_qureg(16)
    workspace = eng.allocate_qubit()
    ScaleGate(5, 511) | src

    assert 6000 < len(backend.received_commands) < 10000
    assert workspace is not None


def test_decompose_addition_uncontrolled():
    for register_size in cover(50):
        for control_size in cover(3):
            check_permutation_decomposition(
                decomposition_rule=decompose_scale,
                gate=ScaleGate(5, 3),
                register_sizes=[register_size],
                control_size=control_size)


def test_diagram_decompose_addition_uncontrolled_same_size():
    text_diagram = decomposition_to_ascii(
        gate=ScaleGate(7, 3),
        decomposition_rule=decompose_scale,
        register_sizes=[6],
        control_size=2)
    print(text_diagram)
    assert text_diagram == """
|0>---@-------@---------@---------@---------@-----
      |       |         |         |         |
|0>---@-------@---------@---------@---------@-----
      |       |         |         |         |
|0>---|-------|---------|---------|---------@-----
      |       |         |         |     .---|---.
|0>---|-------|---------|---------@-----|       |-
      |       |         |     .---|---. |       |
|0>---|-------|---------@-----|       |-|       |-
      |       |     .---|---. |       | |       |
|0>---|-------@-----|       |-|       |-|  +22  |-
      |   .---|---. |       | |       | |       |
|0>---@---|       |-|  +22  |-|  +22  |-|       |-
    .-|-. |       | |       | |       | |       |
|0>-|+22|-|  +22  |-|       |-|       |-|       |-
    `---` `-------` `-------` `-------` `-------`
        """.strip()
