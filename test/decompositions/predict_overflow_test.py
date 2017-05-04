# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import itertools
import random

from projectq.cengines import DecompositionRuleSet

from dirty_period_finding.decompositions import (
    offset_rules,
    multi_not_rules,
    predict_overflow_rules,
)
from dirty_period_finding.decompositions.predict_overflow_rules import (
    do_predict_carry_signals,
    do_predict_overflow,
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import PredictOffsetOverflowGate
from .._test_util import check_permutation_circuit, fuzz_permutation_circuit


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


def test_do_predict_overflow_signal_small():
    for n, nc in itertools.product([1, 2, 3],
                                   [0, 1, 2]):
        for offset in range(1 << n):
            check_permutation_circuit(
                register_sizes=[n, 1, nc, n-1],
                permutation=lambda _, (q, t, c, d):
                    (q,
                     t ^ (0 if c + 1 != 1 << nc or q + offset < 1 << n else 1),
                     c,
                     d),
                engine_list=[
                    AutoReplacerEx(DecompositionRuleSet(modules=[
                        offset_rules,
                        multi_not_rules,
                    ])),
                    LimitedCapabilityEngine(
                        allow_nots_with_many_controls=True,
                    ),
                ],
                actions=lambda eng, regs: do_predict_overflow(
                    offset=offset,
                    query_reg=regs[0],
                    target_bit=regs[1],
                    controls=regs[2],
                    dirty_reg=regs[3]))


def test_check_predict_overflow_signal_gate_small():
    for _ in range(10):
        n = random.randint(1, 100)
        nc = random.randint(0, 2)
        offset = random.randint(0, (1 << n) - 1)
        fuzz_permutation_circuit(
            register_sizes=[n, 1, nc, n-1],
            permutation=lambda _, (q, t, c, d):
                (q,
                 t ^ (0 if c + 1 != 1 << nc or q + offset < 1 << n else 1),
                 c,
                 d),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    predict_overflow_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_arithmetic=True,
                    ban_classes=[PredictOffsetOverflowGate]
                ),
            ],
            actions=lambda eng, regs:
                PredictOffsetOverflowGate(offset) & regs[2] | (regs[0],
                                                               regs[1]))
