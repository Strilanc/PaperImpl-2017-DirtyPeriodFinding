# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import random

from projectq import MainEngine
from projectq.cengines import (AutoReplacer,
                               DecompositionRuleSet,
                               DummyEngine)

from dirty_period_finding.decompositions import multi_not_rules
from dirty_period_finding.decompositions.multi_not_rules import (
    do_multi_not_with_one_big_not_and_friends,
    cut_not_max_controls_in_half,
    cut_not_max_controls_into_toffolis,
)
from dirty_period_finding.extensions import LimitedCapabilityEngine
from dirty_period_finding.extensions import X
from dirty_period_finding.gates import MultiNot
from .._test_util import (
    fuzz_permutation_circuit, check_permutation_circuit
)


def test_do_multi_not_with_one_big_not_and_friends():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    controls = eng.allocate_qureg(5)
    targets = eng.allocate_qureg(5)
    backend.received_commands = []

    do_multi_not_with_one_big_not_and_friends(targets, controls)

    assert backend.received_commands == [
        (X & targets[3]).generate_command(targets[4]),
        (X & targets[2]).generate_command(targets[3]),
        (X & targets[1]).generate_command(targets[2]),
        (X & targets[0]).generate_command(targets[1]),
        (X & controls).generate_command(targets[0]),
        (X & targets[0]).generate_command(targets[1]),
        (X & targets[1]).generate_command(targets[2]),
        (X & targets[2]).generate_command(targets[3]),
        (X & targets[3]).generate_command(targets[4]),
    ]


def test_do_multi_not_with_one_big_not_and_friends_trivial():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    controls = eng.allocate_qureg(1)
    targets = eng.allocate_qureg(4)
    backend.received_commands = []

    do_multi_not_with_one_big_not_and_friends(targets, controls)

    assert backend.received_commands == [
        (X & controls).generate_command(targets[0]),
        (X & controls).generate_command(targets[1]),
        (X & controls).generate_command(targets[2]),
        (X & controls).generate_command(targets[3]),
    ]


def test_cut_not_max_controls_in_half():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    controls = eng.allocate_qureg(8)
    target = eng.allocate_qureg(1)[0]
    dirty = eng.allocate_qureg(1)[0]
    backend.received_commands = []

    cut_not_max_controls_in_half(target, controls, dirty)

    assert backend.received_commands == [
        (X & controls[4:]).generate_command(dirty),
        (X & controls[:4] + [dirty]).generate_command(target),
    ] * 2


def test_cut_not_max_controls_into_toffolis():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    c = eng.allocate_qureg(4)
    target = eng.allocate_qureg(1)[0]
    d = eng.allocate_qureg(2)
    backend.received_commands = []

    cut_not_max_controls_into_toffolis(target, c, d)

    assert backend.received_commands == [
        (X & d[1] & c[3]).generate_command(target),
        (X & d[0] & c[2]).generate_command(d[1]),
        (X & c[0] & c[1]).generate_command(d[0]),
        (X & d[0] & c[2]).generate_command(d[1]),
    ] * 2


def test_big_decomposition_chain_size():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[
        AutoReplacer(DecompositionRuleSet(modules=[
            multi_not_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(200)
    targets = eng.allocate_qureg(150)
    MultiNot & controls | targets
    assert 200*4*2 <= len(backend.received_commands) <= 200*4*4


def test_permutations_small():
    for targets in [0, 1, 2, 3, 5]:
        for controls in [0, 1, 2, 3]:
            # If there are multiple targets, each can use the others as\
            # workspace. Otherwise we need a dirty bit.
            dirty = 1 if targets == 1 else 0

            check_permutation_circuit(
                register_sizes=[targets, controls, dirty],
                permutation=lambda ns, (t, c, d):
                    (t ^ (((1 << targets) - 1)
                          if c + 1 == 1 << controls
                          else 0),
                     c,
                     d),
                engine_list=[
                    AutoReplacer(DecompositionRuleSet(modules=[
                        multi_not_rules,
                    ])),
                    LimitedCapabilityEngine(allow_toffoli=True),
                ],
                actions=lambda eng, regs: MultiNot & regs[1] | regs[0])


def test_fuzz_large():
    for _ in range(10):
        targets = random.randint(2, 100)
        controls = random.randint(0, 4)
        fuzz_permutation_circuit(
            register_sizes=[targets, controls],
            permutation=lambda ns, (t, c):
                (t ^ (((1 << targets) - 1) if c+1 == 1 << controls else 0), c),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    multi_not_rules,
                ])),
                LimitedCapabilityEngine(allow_toffoli=True),
            ],
            actions=lambda eng, regs: MultiNot & regs[1] | regs[0])
