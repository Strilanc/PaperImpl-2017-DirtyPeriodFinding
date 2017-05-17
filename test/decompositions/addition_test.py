# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import itertools
import random

from projectq import MainEngine
from projectq.cengines import (DummyEngine,
                               DecompositionRuleSet)
from projectq.ops import X
from projectq.setups.decompositions import swap2cnot
from projectq.types import Qureg

from dirty_period_finding.decompositions import (
    multi_not_rules,
    addition_rules,
    increment_rules
)
from dirty_period_finding.decompositions.addition_rules import (
    do_addition_with_same_size_and_no_controls
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import (
    Add,
    Subtract,
    MultiNot,
    IncrementGate,
    DecrementGate,
)
from .._test_util import fuzz_permutation_circuit, check_permutation_circuit


def test_exact_commands_for_small_circuit():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    src = eng.allocate_qureg(2)
    dst = eng.allocate_qureg(2)
    backend.received_commands = []
    do_addition_with_same_size_and_no_controls(src, dst)

    a, c = src[0], src[1]
    x, y = dst[0], dst[1]
    assert backend.received_commands == [
        (MultiNot & c).generate_command(Qureg([y, x, a])),
        (X & c).generate_command(x),
        (X & x & c).generate_command(a),
        (X & x & a).generate_command(c),
        (X & c).generate_command(y),
        (X & x & a).generate_command(c),
        (X & x & c).generate_command(a),
        (X & a).generate_command(x),
        (MultiNot & c).generate_command(Qureg([a, x, y])),
    ]


def test_toffoli_size_of_addition():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            swap2cnot,
            multi_not_rules,
            addition_rules,
            increment_rules
        ])),
        LimitedCapabilityEngine(allow_nots_with_many_controls=True),
    ])
    src = eng.allocate_qureg(50)
    dst = eng.allocate_qureg(100)
    Add | (src, dst)

    assert 1000 < len(backend.received_commands) < 10000


def test_check_small_permutations():
    for in_len, out_len, control_len in itertools.product([0, 1, 2, 3],
                                                          [0, 1, 2, 3],
                                                          [0, 1, 2]):
        dirty_len = 1 if control_len > 0 and in_len > 1 and out_len > 1 else 0

        check_permutation_circuit(
            register_sizes=[in_len, out_len, control_len, dirty_len],
            permutation=lambda ns, (a, b, c, d):
                (a,
                 b + (a if c + 1 == 1 << control_len else 0),
                 c,
                 d),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    swap2cnot,
                    multi_not_rules,
                    addition_rules,
                    increment_rules
                ])),
                LimitedCapabilityEngine(
                    allow_nots_with_many_controls=True,
                    allow_classes=[DecrementGate, IncrementGate],
                )],
            actions=lambda eng, regs:
                Add & regs[2] | (regs[0], regs[1]))


def test_fuzz_large_add_same_size():
    for _ in range(10):
        n = random.randint(1, 100)
        fuzz_permutation_circuit(
            register_sizes=[n, n],
            permutation=lambda ns, (a, b): (a, b + a),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    swap2cnot,
                    multi_not_rules,
                    addition_rules
                ])),
                LimitedCapabilityEngine(allow_toffoli=True)],
            actions=lambda eng, regs: Add | (regs[0], regs[1]))


def test_fuzz_large_subtract_different_sizes():
    for _ in range(10):
        n = random.randint(1, 15)
        e = random.randint(1, 15)
        fuzz_permutation_circuit(
            register_sizes=[n, n + e, 2],
            permutation=lambda ns, (a, b, d): (a, b - a, d),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    swap2cnot,
                    multi_not_rules,
                    addition_rules,
                    increment_rules
                ])),
                LimitedCapabilityEngine(allow_toffoli=True)],
            actions=lambda eng, regs: Subtract | (regs[0], regs[1]))
