# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import itertools
import random

from projectq import MainEngine
from projectq.cengines import DecompositionRuleSet, DummyEngine
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    pivot_flip_rules,
    addition_rules,
    offset_rules,
    increment_rules,
    multi_not_rules,
    predict_overflow_rules,
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import (
    PivotFlip,
    PivotFlipGate,
    ConstPivotFlipGate,
)
from .._test_util import fuzz_permutation_circuit, check_permutation_circuit


def test_toffoli_size_of_pivot_flip():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            pivot_flip_rules,
            addition_rules,
            swap2cnot,
            increment_rules,
            multi_not_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(15)
    target1 = eng.allocate_qureg(30)
    target2 = eng.allocate_qureg(40)
    dirty = eng.allocate_qureg(2)

    PivotFlip & controls | (target1, target2)

    assert dirty is not None
    assert 10000 < len(rec.received_commands) < 20000


def test_toffoli_size_of_const_pivot_flip():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            pivot_flip_rules,
            addition_rules,
            offset_rules,
            swap2cnot,
            increment_rules,
            multi_not_rules,
            predict_overflow_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(15)
    target = eng.allocate_qureg(32)
    dirty = eng.allocate_qureg(2)
    offset = 0x789ABCDEF

    ConstPivotFlipGate(offset) & controls | target

    assert dirty is not None
    assert 10000 < len(rec.received_commands) < 20000


def test_check_const_pivot_flip_permutations_small():
    for n, nc in itertools.product([1, 2, 3],
                                   [0, 1]):
        for pivot in range((1 << n) + 1):
            dirty = 1
            check_permutation_circuit(
                register_sizes=[n, nc, dirty],
                permutation=lambda _, (t, c, d):
                    (pivot - t - 1 if c + 1 == 1 << nc and t < pivot else t,
                     c,
                     d),
                engine_list=[
                    AutoReplacerEx(DecompositionRuleSet(modules=[
                        pivot_flip_rules,
                    ])),
                    LimitedCapabilityEngine(
                        allow_all=True,
                        ban_classes=[ConstPivotFlipGate],
                    ),
                ],
                actions=lambda eng, regs:
                    ConstPivotFlipGate(pivot) & regs[1] | regs[0])


def test_fuzz_const_pivot_flip_permutations_large():
    for _ in range(10):
        n = random.randint(0, 50)
        nc = random.randint(0, 2)
        pivot = random.randint(0, 1 << n)
        dirty = 1
        fuzz_permutation_circuit(
            register_sizes=[n, nc, dirty],
            permutation=lambda _, (t, c, d):
                (pivot - t - 1 if c + 1 == 1 << nc and t < pivot else t,
                 c,
                 d),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    pivot_flip_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_all=True,
                    ban_classes=[ConstPivotFlipGate],
                ),
            ],
            actions=lambda eng, regs:
                ConstPivotFlipGate(pivot) & regs[1] | regs[0])


def test_check_pivot_flip_permutations_small():
    for n, e, nc in itertools.product([1, 2, 3],
                                      [0, 1, 3],
                                      [0, 1]):
        dirty = 1
        check_permutation_circuit(
            register_sizes=[n, n + e, nc, dirty],
            permutation=lambda _, (pivot, t, c, d):
                (pivot,
                 pivot - t - 1 if c + 1 == 1 << nc and t < pivot else t,
                 c,
                 d),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    pivot_flip_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_all=True,
                    ban_classes=[PivotFlipGate],
                ),
            ],
            actions=lambda eng, regs:
                PivotFlip & regs[2] | (regs[0], regs[1]))


def test_fuzz_pivot_flip_permutations_large():
    for _ in range(10):
        n = random.randint(0, 50)
        e = random.randint(0, 10)
        nc = random.randint(0, 2)
        dirty = 1
        fuzz_permutation_circuit(
            register_sizes=[n, n + e, nc, dirty],
            permutation=lambda _, (pivot, t, c, d):
                (pivot,
                 pivot - t - 1 if c + 1 == 1 << nc and t < pivot else t,
                 c,
                 d),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    pivot_flip_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_all=True,
                    ban_classes=[PivotFlipGate],
                ),
            ],
            actions=lambda eng, regs:
                PivotFlip & regs[2] | (regs[0], regs[1]))
