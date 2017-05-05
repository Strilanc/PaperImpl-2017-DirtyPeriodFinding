# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq.cengines import DecompositionRuleSet

from dirty_period_finding.decompositions import (
    offset_rules,
    multi_not_rules,
)
from dirty_period_finding.decompositions.predict_overflow_rules import (
    do_predict_carry_signals,
    decompose_less_than_into_overflow,
    decompose_overflow,
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import (
    LessThanConstantGate,
    PredictOffsetOverflowGate,
)
from .._test_util import check_permutation_circuit, decomposition_to_ascii, check_permutation_decomposition, cover


def _carry_signals(x, y):
    return ((x + y) ^ x ^ y) >> 1


def test_carry_signals():
    assert _carry_signals(0b001, 0b001) == 0b001
    assert _carry_signals(0b010, 0b010) == 0b010
    assert _carry_signals(0b001, 0b111) == 0b111
    assert _carry_signals(0b111, 0b001) == 0b111
    assert _carry_signals(0b101, 0b101) == 0b101
    assert _carry_signals(0b101, 0b011) == 0b111
    assert _carry_signals(0b101, 0b001) == 0b001
    assert _carry_signals(0b1000000, 0b1000000) == 0b1000000
    assert _carry_signals(0b1001000, 0b1000001) == 0b1000000


def test_do_predict_carry_signals_small():
    for n in [0, 1, 2, 3, 4]:
        for offset in range(1 << n):
            offset_bits = [bool((offset >> i) & 1) for i in range(n)]

            check_permutation_circuit(
                register_sizes=[n, n],
                permutation=lambda _, (q, t):
                    (q, t ^ _carry_signals(q, offset)),
                engine_list=[
                    AutoReplacerEx(DecompositionRuleSet(modules=[
                        offset_rules,
                        multi_not_rules,
                    ])),
                    LimitedCapabilityEngine(allow_toffoli=True),
                ],
                actions=lambda eng, regs: do_predict_carry_signals(
                    offset_bits=offset_bits,
                    query_reg=regs[0],
                    target_reg=regs[1]))


def test_predict_overflow_operation():
    assert PredictOffsetOverflowGate(5).do_operation((4, 1), (3, 0)) == (3, 0)
    assert PredictOffsetOverflowGate(5).do_operation((4, 1), (3, 1)) == (3, 1)

    assert PredictOffsetOverflowGate(6).do_operation((4, 1), (9, 0)) == (9, 0)
    assert PredictOffsetOverflowGate(6).do_operation((4, 1), (9, 1)) == (9, 1)

    assert PredictOffsetOverflowGate(7).do_operation((4, 1), (8, 0)) == (8, 0)
    assert PredictOffsetOverflowGate(7).do_operation((4, 1), (8, 1)) == (8, 1)

    assert PredictOffsetOverflowGate(7).do_operation((4, 1), (9, 0)) == (9, 1)
    assert PredictOffsetOverflowGate(7).do_operation((4, 1), (9, 1)) == (9, 0)


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


def test_diagram_decompose_overflow():
    text_diagram = decomposition_to_ascii(
        gate=PredictOffsetOverflowGate(9),
        decomposition_rule=decompose_overflow,
        register_sizes=[6, 1],
        workspace=5,
        control_size=1)
    print(text_diagram)
    assert text_diagram == """
|0>-------------------------------------@---------------------------------@-
                                        |                                 |
|0>-???---------@---X---------@---------|---------@---X---------@---------|-
                |   |         |         |         |   |         |         |
|0>-???-------@-X---|---------X-@-------|-------@-X---|---------X-@-------|-
              | |   |         | |       |       | |   |         | |       |
|0>-???-----@-X-|---|---------|-X-@-----|-----@-X-|---|---------|-X-@-----|-
            | | |   |         | | |     |     | | |   |         | | |     |
|0>-???---@-X-|-|---|-----X---|-|-X-@---|---@-X-|-|---|-----X---|-|-X-@---|-
          | | | |   |     |   | | | |   |   | | | |   |     |   | | | |   |
|0>-???---X-|-|-|---|-----|---|-|-|-X---@---X-|-|-|---|-----|---|-|-|-X---@-
          | | | |   |     |   | | | |   |   | | | |   |     |   | | | |   |
|0>-----X-|-|-|-|-X-@-X---|---|-|-|-|-X-|-X-|-|-|-|-X-@-X---|---|-|-|-|-X-|-
          | | | |         |   | | | |   |   | | | |         |   | | | |   |
|0>-------|-|-|-@---------|---@-|-|-|---|---|-|-|-@---------|---@-|-|-|---|-
          | | |           |     | | |   |   | | |           |     | | |   |
|0>-------|-|-@-----------|-----@-|-|---|---|-|-@-----------|-----@-|-|---|-
          | |             |       | |   |   | |             |       | |   |
|0>-----X-|-@-----------X-@-X-----@-|-X-|-X-|-@-----------X-@-X-----@-|-X-|-
          |                         |   |   |                         |   |
|0>-------@-------------------------@---|---@-------------------------@---|-
                                        |                                 |
|0>-------------------------------------@---------------------------------@-
                                        |                                 |
|0>-------------------------------------X---------------------------------X-
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
