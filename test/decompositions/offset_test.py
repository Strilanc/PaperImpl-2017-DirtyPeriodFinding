# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import itertools
import random

from projectq.cengines import DecompositionRuleSet

from dirty_period_finding.decompositions import offset_rules, multi_not_rules
from dirty_period_finding.decompositions.offset_rules import (
    estimate_cost_of_bitrange_offset,
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import OffsetGate
from .._test_util import fuzz_permutation_circuit, check_permutation_circuit


def test_estimate_cost_of_bitrange_offset():
    assert estimate_cost_of_bitrange_offset(0b11111111, 8) == 1
    assert estimate_cost_of_bitrange_offset(0b01111111, 8) == 2
    assert estimate_cost_of_bitrange_offset(0b11110111, 8) == 3
    assert estimate_cost_of_bitrange_offset(0b11110000, 8) == 1
    assert estimate_cost_of_bitrange_offset(0b01110000, 8) == 2
    assert estimate_cost_of_bitrange_offset(0b11110001, 8) == 2
    assert estimate_cost_of_bitrange_offset(0b10101001, 8) == 4


def test_check_offset_permutations_small():
    for n, nc in itertools.product([1, 2, 3],
                                   [0, 1]):
        for offset in range(1 << n):
            dirty = 1
            check_permutation_circuit(
                register_sizes=[n, dirty, nc],
                permutation=lambda _, (t, d, c):
                    (t + (offset if c + 1 == 1 << nc else 0), d, c),
                engine_list=[
                    AutoReplacerEx(DecompositionRuleSet(modules=[
                        offset_rules,
                        multi_not_rules,
                    ])),
                    LimitedCapabilityEngine(
                        allow_all=True,
                        ban_classes=[OffsetGate],
                    ),
                ],
                actions=lambda eng, regs:
                    OffsetGate(offset) & regs[2] | regs[0])


def test_fuzz_offset_permutations_large():
    for _ in range(10):
        n = random.randint(0, 50)
        nc = random.randint(0, 2)
        offset = random.randint(0, 1 << n)
        dirty = 1
        fuzz_permutation_circuit(
            register_sizes=[n, dirty, nc],
            permutation=lambda _, (t, d, c):
                (t + (offset if c + 1 == 1 << nc else 0), d, c),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    offset_rules,
                    multi_not_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_all=True,
                    ban_classes=[OffsetGate],
                ),
            ],
            actions=lambda eng, regs:
                OffsetGate(offset) & regs[2] | regs[0])
