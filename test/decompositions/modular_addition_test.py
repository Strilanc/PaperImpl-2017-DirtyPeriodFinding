# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import itertools
import random

from projectq import MainEngine
from projectq.cengines import (AutoReplacer,
                               DecompositionRuleSet,
                               DummyEngine)
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    modular_addition_rules,
    pivot_flip_rules,
    offset_rules,
    addition_rules,
    increment_rules,
    multi_not_rules,
)
from dirty_period_finding.extensions import LimitedCapabilityEngine
from dirty_period_finding.gates import (
    ModularAdditionGate,
    ModularOffsetGate,
)
from .._test_util import fuzz_permutation_circuit, check_permutation_circuit


def test_toffoli_size_of_modular_addition():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacer(DecompositionRuleSet(modules=[
            pivot_flip_rules,
            offset_rules,
            addition_rules,
            swap2cnot,
            increment_rules,
            multi_not_rules,
            modular_addition_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(15)
    target1 = eng.allocate_qureg(16)
    target2 = eng.allocate_qureg(16)
    modulus = 0xAEFD

    ModularAdditionGate(modulus) & controls | (target1, target2)

    assert 25000 < len(rec.received_commands) < 50000


def test_toffoli_size_of_modular_offset():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacer(DecompositionRuleSet(modules=[
            pivot_flip_rules,
            offset_rules,
            addition_rules,
            swap2cnot,
            increment_rules,
            multi_not_rules,
            modular_addition_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(15)
    target = eng.allocate_qureg(16)
    dirty = eng.allocate_qureg(2)
    modulus = 0xAEFD
    offset = 0x9E0A

    ModularOffsetGate(offset, modulus) & controls | target

    assert dirty is not None
    assert 25000 < len(rec.received_commands) < 50000


def test_check_modular_offset_permutations_small():
    for n, nc in itertools.product([2, 3, 4],
                                   [0, 1]):
        for modulus in range((1 << (n-1)) + 1, (1 << n) + 1)[::2]:
            for offset in range(modulus):
                check_permutation_circuit(
                    register_sizes=[n, nc],
                    register_limits=[modulus, 1 << nc],
                    permutation=lambda _, (t, c):
                        ((t + offset) % modulus if c + 1 == 1 << nc else t, c),
                    engine_list=[
                        AutoReplacer(DecompositionRuleSet(modules=[
                            modular_addition_rules,
                        ])),
                        LimitedCapabilityEngine(
                            allow_all=True,
                            ban_classes=[
                                ModularOffsetGate,
                            ],
                        ),
                    ],
                    actions=lambda eng, (t, c):
                        ModularOffsetGate(offset, modulus) & c | t)


def test_fuzz_modular_offset_permutations_large():
    for _ in range(10):
        n = random.randint(2, 50)
        nc = random.randint(0, 2)
        modulus = random.randint((1 << (n-1)) + 1, (1 << n) - 1)
        offset = random.randint(0, modulus - 1)
        fuzz_permutation_circuit(
            register_sizes=[n, nc],
            register_limits=[modulus, 1 << nc],
            permutation=lambda _, (t, c):
                ((t + offset) % modulus if c + 1 == 1 << nc else t, c),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    modular_addition_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_all=True,
                    ban_classes=[
                        ModularOffsetGate,
                    ],
                ),
            ],
            actions=lambda eng, (t, c):
                ModularOffsetGate(offset, modulus) & c | t)


def test_check_modular_addition_permutations_small():
    for n, nc in itertools.product([2, 3, 4],
                                   [0, 1]):
        for modulus in range((1 << (n-1)) + 1, (1 << n) + 1)[::2]:
            check_permutation_circuit(
                register_sizes=[n, n, nc],
                register_limits=[modulus, modulus, 1 << nc],
                permutation=lambda _, (a, t, c):
                    (a, (t + a) % modulus if c + 1 == 1 << nc else t, c),
                engine_list=[
                    AutoReplacer(DecompositionRuleSet(modules=[
                        modular_addition_rules,
                    ])),
                    LimitedCapabilityEngine(
                        allow_all=True,
                        ban_classes=[
                            ModularAdditionGate,
                        ],
                    ),
                ],
                actions=lambda eng, (a, t, c):
                    ModularAdditionGate(modulus) & c | (a, t))


def test_fuzz_modular_addition_permutations_large():
    for _ in range(10):
        n = random.randint(2, 50)
        nc = random.randint(0, 2)
        modulus = random.randint((1 << (n - 1)) + 1, (1 << n) - 1)
        fuzz_permutation_circuit(
            register_sizes=[n, n, nc],
            register_limits=[modulus, modulus, 1 << nc],
            permutation=lambda _, (a, t, c):
            (a, (t + a) % modulus if c + 1 == 1 << nc else t, c),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    modular_addition_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_all=True,
                    ban_classes=[
                        ModularAdditionGate,
                    ],
                ),
            ],
            actions=lambda eng, (a, t, c):
            ModularAdditionGate(modulus) & c | (a, t))
