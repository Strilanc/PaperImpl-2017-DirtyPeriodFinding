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

from dirty_period_finding.decompositions.offset_rules import (
    estimate_cost_of_bitrange_offset,
    decompose_into_range_increments,
    decompose_into_recursion,
    decompose_remove_controls,
    decompose_decrease_size,
)
from dirty_period_finding.gates import OffsetGate
from .._test_util import (
    decomposition_to_ascii,
    cover,
    check_permutation_decomposition,
)


def test_offset_operation():
    assert OffsetGate(4).do_operation(3) == (7,)


def test_estimate_cost_of_bitrange_offset():
    assert estimate_cost_of_bitrange_offset(0b11111111, 8) == 1
    assert estimate_cost_of_bitrange_offset(0b01111111, 8) == 2
    assert estimate_cost_of_bitrange_offset(0b11110111, 8) == 3
    assert estimate_cost_of_bitrange_offset(0b11110000, 8) == 1
    assert estimate_cost_of_bitrange_offset(0b01110000, 8) == 2
    assert estimate_cost_of_bitrange_offset(0b11110001, 8) == 2
    assert estimate_cost_of_bitrange_offset(0b10101001, 8) == 4


def test_decompose_into_range_increments():
    for register_size in cover(100):
        for offset in cover(1 << register_size):
            if estimate_cost_of_bitrange_offset(offset, register_size) > 4:
                continue

            check_permutation_decomposition(
                decomposition_rule=decompose_into_range_increments,
                gate=OffsetGate(offset),
                register_sizes=[register_size])


def test_decompose_decrease_size():
    for register_size in cover(100):
        for offset in cover(1 << register_size):
            for control_size in cover(2):
                check_permutation_decomposition(
                    decomposition_rule=decompose_decrease_size,
                    gate=OffsetGate(offset * 2),
                    register_sizes=[register_size],
                    control_size=control_size)


def test_decompose_into_recursion():
    for register_size in range(1, 10):
        for offset in cover(1 << (register_size - 1)):
            check_permutation_decomposition(
                decomposition_rule=decompose_into_recursion,
                gate=OffsetGate(offset),
                register_sizes=[register_size],
                workspace=1)


def test_decompose_remove_controls():
    for register_size in cover(100):
        for offset in cover(1 << register_size):
            for controls in range(1, 4):
                check_permutation_decomposition(
                    decomposition_rule=decompose_remove_controls,
                    gate=OffsetGate(offset),
                    register_sizes=[register_size],
                    workspace=1,
                    control_size=controls)


def test_diagram_decompose_decrease_size():
    text_diagram = decomposition_to_ascii(
        gate=OffsetGate(0b110111000),
        decomposition_rule=decompose_decrease_size,
        register_sizes=[9])
    print(text_diagram)
    assert text_diagram == """
|0>-----------
|0>-----------
|0>-----------
    .-------.
|0>-|       |-
    |       |
|0>-|       |-
    |       |
|0>-|       |-
    |       |
|0>-|  +55  |-
    |       |
|0>-|       |-
    |       |
|0>-|       |-
    `-------`
        """.strip()


def test_diagram_decompose_into_range_increments():
    text_diagram = decomposition_to_ascii(
        gate=OffsetGate(0b110111001),
        decomposition_rule=decompose_into_range_increments,
        register_sizes=[9])
    print(text_diagram)
    assert text_diagram == """
    .------.
|0>-|      |----------------------------
    |      |
|0>-|      |----------------------------
    |      |
|0>-|      |----------------------------
    |      | .------.
|0>-|      |-|      |-------------------
    |      | |      |
|0>-|  +1  |-|      |-------------------
    |      | |      |
|0>-|      |-|      |-------------------
    |      | |      | .------.
|0>-|      |-|  −1  |-|      |----------
    |      | |      | |      | .------.
|0>-|      |-|      |-|  +1  |-|      |-
    |      | |      | |      | |      |
|0>-|      |-|      |-|      |-|  −1  |-
    `------` `------` `------` `------`
        """.lstrip('\n').rstrip()


def test_diagram_decompose_into_recursion():
    text_diagram = decomposition_to_ascii(
        gate=OffsetGate(0b110111001),
        decomposition_rule=decompose_into_recursion,
        register_sizes=[9],
        workspace=1)
    print(text_diagram)
    assert text_diagram == """
                   .-------------------.          .-------------------.   .------.
|0>----------------|                   |----------|                   |---|      |-----------
                   |                   |          |                   |   |      |
|0>----------------|                   |----------|                   |---|      |-----------
                   |                   |          |                   |   |      |
|0>----------------|         A         |----------|         A         |---|  +9  |-----------
                   |                   |          |                   |   |      |
|0>----------------|                   |----------|                   |---|      |-----------
        .------.   `-------------------` .------. `-------------------`   `------` .-------.
|0>-----|      |-X-----------------------|      |-----------------------X----------|       |-
        |      | |                       |      |                       |          |       |
|0>-----|      |-X-----------------------|      |-----------------------X----------|       |-
        |      | |                       |      |                       |          |       |
|0>-----|  +1  |-X-----------------------|  +1  |-----------------------X----------|  +27  |-
        |      | |                       |      |                       |          |       |
|0>-----|      |-X-----------------------|      |-----------------------X----------|       |-
        |      | |                       |      |                       |          |       |
|0>-----|      |-X-----------------------|      |-----------------------X----------|       |-
        `--|---` | .-------------------. `--|---` .-------------------. |          `-------`
|0>-???----@-----@-|  Xoverflow(A+=9)  |----@-----|  Xoverflow(A+=9)  |-@--------------------
                   `-------------------`          `-------------------`
        """.lstrip('\n').rstrip()


def test_diagram_decompose_remove_controls():
    text_diagram = decomposition_to_ascii(
        gate=OffsetGate(0b110111001),
        decomposition_rule=decompose_remove_controls,
        register_sizes=[9],
        workspace=1,
        control_size=3)
    print(text_diagram)
    assert text_diagram == """
|0>----------------@------------@-
                   |            |
|0>----------------@------------@-
                   |            |
|0>----------------@------------@-
        .--------. | .--------. |
|0>-----|1       |-X-|1       |-X-
        |        | | |        | |
|0>-----|2       |-X-|2       |-X-
        |        | | |        | |
|0>-----|3       |-X-|3       |-X-
        |        | | |        | |
|0>-----|4       |-X-|4       |-X-
        |        | | |        | |
|0>-----|5       |-X-|5       |-X-
        |        | | |        | |
|0>-----|6 +441  |-X-|6 -441  |-X-
        |        | | |        | |
|0>-----|7       |-X-|7       |-X-
        |        | | |        | |
|0>-----|8       |-X-|8       |-X-
        |        | | |        | |
|0>-----|9       |-X-|9       |-X-
        |        | | |        | |
|0>-???-|0       |-X-|0       |-X-
        `--------`   `--------`
        """.strip()
