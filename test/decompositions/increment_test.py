# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import random

from projectq import MainEngine
from projectq.cengines import (AutoReplacer,
                               DecompositionRuleSet,
                               DummyEngine)
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    addition_rules,
    increment_rules,
    multi_not_rules
)
from dirty_period_finding.decompositions.increment_rules import (
    do_increment_with_no_controls_and_n_dirty
)
from dirty_period_finding.extensions import LimitedCapabilityEngine
from dirty_period_finding.gates import Subtract, Increment, MultiNot
from .._test_util import fuzz_permutation_circuit


def test_do_increment_with_no_controls_and_n_dirty():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    target = eng.allocate_qureg(10)
    dirty = eng.allocate_qureg(10)
    backend.received_commands = []

    do_increment_with_no_controls_and_n_dirty(target, dirty)

    assert backend.received_commands == [
        Subtract.generate_command((dirty, target)),
        MultiNot.generate_command(dirty),
        Subtract.generate_command((dirty, target)),
        MultiNot.generate_command(dirty),
    ]


def test_fuzz_do_increment_with_no_controls_and_n_dirty():
    for _ in range(10):
        fuzz_permutation_circuit(
            register_sizes=[4, 4],
            permutation=lambda ns, (a, b): (a + 1, b),
            engine_list=[AutoReplacer(DecompositionRuleSet(modules=[
                addition_rules,
                multi_not_rules,
                swap2cnot
            ]))],
            actions=lambda eng, regs:
                do_increment_with_no_controls_and_n_dirty(
                    target_reg=regs[0],
                    dirty_reg=regs[1]))


def test_toffoli_size_of_increment():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[
        AutoReplacer(DecompositionRuleSet(modules=[
            multi_not_rules,
            increment_rules,
            addition_rules,
            swap2cnot,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(40)
    target = eng.allocate_qureg(35)
    _ = eng.allocate_qureg(2)
    Increment & controls | target
    assert 1000 < len(backend.received_commands) < 10000


def test_fuzz_controlled_increment():
    for _ in range(10):
        n = random.randint(1, 30)
        control_size = random.randint(0, 3)
        satisfy = (1 << control_size) - 1
        fuzz_permutation_circuit(
            register_sizes=[control_size, n, 2],
            permutation=lambda ns, (c, t, d):
                (c, t + (1 if c == satisfy else 0), d),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    swap2cnot,
                    multi_not_rules,
                    increment_rules,
                    addition_rules,
                ])),
                LimitedCapabilityEngine(allow_toffoli=True),
            ],
            actions=lambda eng, regs: Increment & regs[0] | regs[1])
