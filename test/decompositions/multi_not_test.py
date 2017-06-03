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

from projectq.ops import X

from dirty_period_finding.decompositions.multi_not_rules import (
    decompose_multi_not_into_cnots,
    decompose_halve_cnot_with_single_workspace,
    decompose_cnot_with_big_workspace,
)
from dirty_period_finding.gates import MultiNot
from .._test_util import (
    decomposition_to_ascii,
    check_permutation_decomposition,
    cover,
)


def test_multinot_operation():
    assert MultiNot.do_operation(5) == (~5,)


def test_decompose_multi_not_into_cnots():
    for register_size in cover(100):
        for control_size in cover(10):
            check_permutation_decomposition(
                decomposition_rule=decompose_multi_not_into_cnots,
                gate=MultiNot,
                register_sizes=[register_size],
                control_size=control_size)


def test_decompose_halve_cnot_with_single_workspace():
    for control_size in cover(100, min=3):
        check_permutation_decomposition(
            decomposition_rule=decompose_halve_cnot_with_single_workspace,
            gate=X,
            register_sizes=[1],
            control_size=control_size,
            workspace=1)


def test_decompose_cnot_with_big_workspace():
    for control_size in cover(100, min=3):
        check_permutation_decomposition(
            decomposition_rule=decompose_cnot_with_big_workspace,
            gate=X,
            register_sizes=[1],
            control_size=control_size,
            workspace=max(0, control_size - 2))


def test_diagram_decompose_multi_not_into_cnots():
    text_diagram = decomposition_to_ascii(
        gate=MultiNot,
        decomposition_rule=decompose_multi_not_into_cnots,
        register_sizes=[4],
        control_size=4)
    print(text_diagram)
    assert text_diagram == """
|0>-------@-------
          |
|0>-------@-------
          |
|0>-------@-------
          |
|0>-------@-------
          |
|0>-----@-X-@-----
        |   |
|0>---@-X---X-@---
      |       |
|0>-@-X-------X-@-
    |           |
|0>-X-----------X-
        """.strip()


def test_diagram_decompose_halve_cnot_with_single_workspace():
    text_diagram = decomposition_to_ascii(
        gate=X,
        decomposition_rule=decompose_halve_cnot_with_single_workspace,
        register_sizes=[1],
        control_size=8,
        workspace=1)
    print(text_diagram)
    assert text_diagram == """
|0>-------@---@-
          |   |
|0>-------@---@-
          |   |
|0>-------@---@-
          |   |
|0>-------@---@-
          |   |
|0>-----@-|-@-|-
        | | | |
|0>-----@-|-@-|-
        | | | |
|0>-----@-|-@-|-
        | | | |
|0>-----@-|-@-|-
        | | | |
|0>-----|-X-|-X-
        | | | |
|0>-???-X-@-X-@-
        """.strip()


def test_diagram_decompose_cnot_with_big_workspace():
    text_diagram = decomposition_to_ascii(
        gate=X,
        decomposition_rule=decompose_cnot_with_big_workspace,
        register_sizes=[1],
        control_size=6,
        workspace=4)
    print(text_diagram)
    assert text_diagram == """
|0>-------------@---------------@-------
                |               |
|0>-------------@---------------@-------
                |               |
|0>-----------@-|-@-----------@-|-@-----
              | | |           | | |
|0>---------@-|-|-|-@-------@-|-|-|-@---
            | | | | |       | | | | |
|0>-------@-|-|-|-|-|-@---@-|-|-|-|-|-@-
          | | | | | | |   | | | | | | |
|0>-----@-|-|-|-|-|-|-|-@-|-|-|-|-|-|-|-
        | | | | | | | | | | | | | | | |
|0>-----X-|-|-|-|-|-|-|-X-|-|-|-|-|-|-|-
        | | | | | | | | | | | | | | | |
|0>-???-|-|-|-@-X-@-|-|-|-|-|-@-X-@-|-|-
        | | | |   | | | | | | |   | | |
|0>-???-|-|-@-X---X-@-|-|-|-@-X---X-@-|-
        | | |       | | | | |       | |
|0>-???-|-@-X-------X-@-|-@-X-------X-@-
        | |           | | |           |
|0>-???-@-X-----------X-@-X-----------X-
        """.strip()
