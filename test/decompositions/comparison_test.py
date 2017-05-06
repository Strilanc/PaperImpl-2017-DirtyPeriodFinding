# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from dirty_period_finding.decompositions.comparison_rules import (
    decompose_less_than_into_overflow,
    decompose_overflow,
    decompose_xor_offset_carry_signals,
)
from dirty_period_finding.gates import (
    LessThanConstantGate,
    PredictOffsetOverflowGate,
    XorOffsetCarrySignalsGate,
)
from .._test_util import (
    decomposition_to_ascii,
    check_permutation_decomposition,
    cover,
)


def test_carry_signals():

    def _carry_signals(x, y):
        z, t = XorOffsetCarrySignalsGate(x).do_operation((8, 8), (y, 0))
        assert z == y
        return t
    assert _carry_signals(0b001, 0b001) == 0b001
    assert _carry_signals(0b010, 0b010) == 0b010
    assert _carry_signals(0b001, 0b111) == 0b111
    assert _carry_signals(0b111, 0b001) == 0b111
    assert _carry_signals(0b101, 0b101) == 0b101
    assert _carry_signals(0b101, 0b011) == 0b111
    assert _carry_signals(0b101, 0b001) == 0b001
    assert _carry_signals(0b1000000, 0b1000000) == 0b1000000
    assert _carry_signals(0b1001000, 0b1000001) == 0b1000000


def test_predict_overflow_operation():
    assert PredictOffsetOverflowGate(5).do_operation((4, 1), (3, 0)) == (3, 0)
    assert PredictOffsetOverflowGate(5).do_operation((4, 1), (3, 1)) == (3, 1)

    assert PredictOffsetOverflowGate(6).do_operation((4, 1), (9, 0)) == (9, 0)
    assert PredictOffsetOverflowGate(6).do_operation((4, 1), (9, 1)) == (9, 1)

    assert PredictOffsetOverflowGate(7).do_operation((4, 1), (8, 0)) == (8, 0)
    assert PredictOffsetOverflowGate(7).do_operation((4, 1), (8, 1)) == (8, 1)

    assert PredictOffsetOverflowGate(7).do_operation((4, 1), (9, 0)) == (9, 1)
    assert PredictOffsetOverflowGate(7).do_operation((4, 1), (9, 1)) == (9, 0)


def test_decompose_xor_offset_carry_signals():
    for register_size in range(1, 50):
        for offset in cover(1 << register_size):

            check_permutation_decomposition(
                decomposition_rule=decompose_xor_offset_carry_signals,
                gate=XorOffsetCarrySignalsGate(offset),
                register_sizes=[register_size, register_size])


def test_decompose_overflow():
    for register_size in range(1, 50):
        for control_size in range(3):
            for offset in cover(1 << register_size):

                check_permutation_decomposition(
                    decomposition_rule=decompose_overflow,
                    gate=PredictOffsetOverflowGate(offset),
                    register_sizes=[register_size, 1],
                    workspace=register_size - 1,
                    control_size=control_size)


def test_decompose_less_than_into_overflow():
    for register_size in range(1, 100):
        for control_size in range(3):
            for limit in cover((1 << register_size) + 1):

                check_permutation_decomposition(
                    decomposition_rule=decompose_less_than_into_overflow,
                    gate=LessThanConstantGate(limit),
                    register_sizes=[register_size, 1],
                    control_size=control_size)


def test_diagram_decompose_xor_offset_carry_signals():
    text_diagram = decomposition_to_ascii(
        gate=XorOffsetCarrySignalsGate(9),
        decomposition_rule=decompose_xor_offset_carry_signals,
        register_sizes=[6, 6])
    print(text_diagram)
    assert text_diagram == """
|0>-X-----------@-----------------X-
                |
|0>-----------@-|-------@-----------
              | |       |
|0>---------@-|-|-------|-@---------
            | | |       | |
|0>-X-----@-|-|-|---@---|-|-@-----X-
          | | | |   |   | | |
|0>-----@-|-|-|-|---|---|-|-|-@-----
        | | | | |   |   | | | |
|0>---@-|-|-|-|-|---|---|-|-|-|-@---
      | | | | | |   |   | | | | |
|0>---|-|-|-|-@-X-X-|---@-|-|-|-|---
      | | | | |     |   | | | | |
|0>---|-|-|-@-X-----|---X-@-|-|-|---
      | | | |       |     | | | |
|0>---|-|-@-X-------|-----X-@-|-|---
      | | |         |       | | |
|0>---|-@-X---------X-X-----X-@-|---
      | |                     | |
|0>---@-X---------------------X-@---
      |                         |
|0>---X-------------------------X---
        """.strip()


def test_diagram_decompose_overflow():
    text_diagram = decomposition_to_ascii(
        gate=PredictOffsetOverflowGate(9),
        decomposition_rule=decompose_overflow,
        register_sizes=[6, 1],
        workspace=5,
        control_size=1)
    print(text_diagram)
    assert text_diagram == """
|0>--------------------------@----------------------@-
        .------------------. | .------------------. |
|0>-----|                  |-|-|                  |-|-
        |                  | | |                  | |
|0>-----|                  |-|-|                  |-|-
        |                  | | |                  | |
|0>-----|        A         |-|-|        A         |-|-
        |                  | | |                  | |
|0>-----|                  |-|-|                  |-|-
        |                  | | |                  | |
|0>-----|                  |-|-|                  |-|-
        `------------------` | `------------------` |
|0>--------------------------@----------------------@-
                             |                      |
|0>--------------------------X----------------------X-
        .------------------. | .------------------. |
|0>-???-|                  |-|-|                  |-|-
        |                  | | |                  | |
|0>-???-|                  |-|-|                  |-|-
        |                  | | |                  | |
|0>-???-|  Xcarries(A, 9)  |-|-|  Xcarries(A, 9)  |-|-
        |                  | | |                  | |
|0>-???-|                  |-|-|                  |-|-
        |                  | | |                  | |
|0>-???-|                  |-@-|                  |-@-
        `------------------`   `------------------`
        """.strip()


def test_diagram_decompose_less_than_into_overflow():
    text_diagram = decomposition_to_ascii(
        gate=LessThanConstantGate(7),
        decomposition_rule=decompose_less_than_into_overflow,
        register_sizes=[4, 1],
        control_size=1)
    print(text_diagram)
    assert text_diagram == """
|0>-----------@-----------@-
    .---------|---------. |
|0>-|                   |-|-
    |                   | |
|0>-|                   |-|-
    |                   | |
|0>-|         A         |-|-
    |                   | |
|0>-|                   |-|-
    |-------------------| |
|0>-|  Xoverflow(A+=9)  |-X-
    `-------------------`
        """.strip()
