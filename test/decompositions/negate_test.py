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
from projectq.cengines import (DummyEngine,
                               DecompositionRuleSet)
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    addition_rules,
    increment_rules,
    multi_not_rules,
    negate_rules,
)
from dirty_period_finding.decompositions.negate_rules import (
    decompose_negate,
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import (
    Negate,
)
from .._test_util import (
    check_permutation_decomposition,
    cover,
    decomposition_to_ascii,
)


def test_negate_operation():
    assert Negate.do_operation((5,), (9,)) == (32 - 9,)


def test_toffoli_size_of_negate():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            addition_rules,
            increment_rules,
            multi_not_rules,
            negate_rules,
            swap2cnot,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    src = eng.allocate_qureg(100)
    workspace = eng.allocate_qubit()
    Negate | src

    assert 2000 < len(backend.received_commands) < 4000
    assert workspace is not None


def test_decompose_addition_uncontrolled():
    for register_size in cover(50):
        for control_size in cover(3):
            check_permutation_decomposition(
                decomposition_rule=decompose_negate,
                gate=Negate,
                register_sizes=[register_size],
                control_size=control_size)


def test_diagram_decompose_addition_uncontrolled_same_size():
    text_diagram = decomposition_to_ascii(
        gate=Negate,
        decomposition_rule=decompose_negate,
        register_sizes=[6],
        control_size=2)
    print(text_diagram)
    assert text_diagram == """
|0>-@----@-----
    |    |
|0>-@----@-----
    | .--|---.
|0>-X-|      |-
    | |      |
|0>-X-|      |-
    | |      |
|0>-X-|      |-
    | |      |
|0>-X-|  +1  |-
    | |      |
|0>-X-|      |-
    | |      |
|0>-X-|      |-
      `------`
        """.strip()
