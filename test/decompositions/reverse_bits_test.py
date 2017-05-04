# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import itertools
import random

from projectq import MainEngine
from projectq.cengines import DummyEngine, DecompositionRuleSet
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import multi_not_rules
from dirty_period_finding.decompositions import reverse_bits_rules
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.extensions import SwapGate
from dirty_period_finding.gates import ReverseBits
from .._test_util import (
    bit_to_state_permutation,
    check_permutation_circuit,
    fuzz_permutation_circuit,
)


def test_toffoli_size_of_reverse():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            swap2cnot,
            multi_not_rules,
            reverse_bits_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(50)
    target = eng.allocate_qureg(100)

    ReverseBits & controls | target
    ReverseBits & controls | target[1:]

    assert 500 < len(rec.received_commands) < 5000


def test_check_small_reversals():
    for num_t, num_c in itertools.product([0, 1, 2, 3, 4],
                                          [0, 1, 2, 3]):
        check_permutation_circuit(
            register_sizes=[num_t, num_c],
            permutation=bit_to_state_permutation(
                lambda ns, b, (c, ): b if c + 1 != 1 << ns[1]
                                     else ns[0] - b - 1),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    reverse_bits_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_nots_with_many_controls=True,
                    allow_classes=[SwapGate],
                    ban_classes=[ReverseBits.__class__],
                )
            ],
            actions=lambda eng, regs: ReverseBits & regs[1] | regs[0])


def test_fuzz_large_reversals():
    for _ in range(10):
        num_t = random.randint(0, 100)
        num_c = random.randint(0, 3)
        fuzz_permutation_circuit(
            register_sizes=[num_t, num_c],
            permutation=bit_to_state_permutation(
                lambda ns, b, (c,): b if c + 1 != 1 << ns[1]
                                    else ns[0] - b - 1),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    reverse_bits_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_nots_with_many_controls=True,
                    allow_classes=[SwapGate],
                    ban_classes=[ReverseBits.__class__],
                )
            ],
            actions=lambda eng, regs: ReverseBits & regs[1] | regs[0])
