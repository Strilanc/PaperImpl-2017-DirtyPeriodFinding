# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import itertools
import random

from projectq import MainEngine
from projectq.cengines import DummyEngine, DecompositionRuleSet
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    modular_scaled_addition_rules,
    modular_addition_rules,
    pivot_flip_rules,
    offset_rules,
    addition_rules,
    increment_rules,
    multi_not_rules,
    modular_double_rules,
    rotate_bits_rules,
    reverse_bits_rules,
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import ModularScaledAdditionGate
from .._test_util import fuzz_permutation_circuit, check_permutation_circuit


def test_toffoli_size_of_scaled_modular_addition():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            modular_scaled_addition_rules,
            modular_double_rules,
            rotate_bits_rules,
            reverse_bits_rules,
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
    target1 = eng.allocate_qureg(8)
    target2 = eng.allocate_qureg(8)
    modulus = 0xAD
    factor = 0x9A

    ModularScaledAdditionGate(factor, modulus) & controls | (target1, target2)

    assert 100000 < len(rec.received_commands) < 300000


def test_check_scaled_modular_addition_permutations_small():
    for n, nc in itertools.product([2, 3],
                                   [0, 1]):
        for modulus in range((1 << (n-1)) + 1, (1 << n) + 1)[::2]:
            for factor in range(0, modulus):
                check_permutation_circuit(
                    register_sizes=[n, n, nc],
                    register_limits=[modulus, modulus, 1 << nc],
                    permutation=lambda _, (a, t, c):
                        (a,
                         (t + a * factor) % modulus if c + 1 == 1 << nc else t,
                         c),
                    engine_list=[
                        AutoReplacerEx(DecompositionRuleSet(modules=[
                            modular_scaled_addition_rules,
                        ])),
                        LimitedCapabilityEngine(
                            allow_all=True,
                            ban_classes=[
                                ModularScaledAdditionGate,
                            ],
                        ),
                    ],
                    actions=lambda eng, (a, t, c): ModularScaledAdditionGate(
                        factor, modulus) & c | (a, t))


def test_fuzz_scaled_modular_addition_permutations_large():
    for _ in range(10):
        n = random.randint(2, 50)
        nc = random.randint(0, 2)
        modulus = random.randint((1 << (n - 1)) + 1, (1 << n) - 1)
        modulus -= modulus % 2
        modulus += 1
        factor = random.randint(0, modulus - 1)
        fuzz_permutation_circuit(
            register_sizes=[n, n, nc],
            register_limits=[modulus, modulus, 1 << nc],
            permutation=lambda _, (a, t, c):
                (a,
                 (t + a * factor) % modulus if c + 1 == 1 << nc else t,
                 c),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    modular_scaled_addition_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_all=True,
                    ban_classes=[
                        ModularScaledAdditionGate,
                    ],
                ),
            ],
            actions=lambda eng, (a, t, c): ModularScaledAdditionGate(
                factor, modulus) & c | (a, t))
