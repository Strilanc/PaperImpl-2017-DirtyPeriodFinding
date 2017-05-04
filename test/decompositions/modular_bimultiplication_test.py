# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq import MainEngine
from projectq.cengines import DummyEngine, DecompositionRuleSet
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    modular_bimultiplication_rules,
    multi_not_rules,
    addition_rules,
    increment_rules,
    pivot_flip_rules,
    modular_scaled_addition_rules,
    modular_addition_rules,
    offset_rules,
    modular_double_rules,
    rotate_bits_rules,
    reverse_bits_rules,
    predict_overflow_rules,
)
from dirty_period_finding.decompositions.modular_bimultiplication_rules \
    import do_bimultiplication
from dirty_period_finding.extensions import (
    AutoReplacerEx,
    LimitedCapabilityEngine,
)
from dirty_period_finding.gates import (
    ModularBimultiplicationGate,
    ModularScaledAdditionGate,
    RotateBitsGate,
)
from .._test_util import fuzz_permutation_circuit


def test_do_bimultiplication():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    a = eng.allocate_qureg(4)
    b = eng.allocate_qureg(4)
    c = eng.allocate_qureg(3)

    backend.received_commands = []
    do_bimultiplication(
        ModularBimultiplicationGate(3, 13), a, b, c)

    m = ModularScaledAdditionGate
    assert backend.received_commands == [
        (m(3, 13) & c).generate_command((a, b)),
        (m(4, 13) & c).generate_command((b, a)),
        (m(3, 13) & c).generate_command((a, b)),
        (RotateBitsGate(4) & c).generate_command(a + b),
    ]


def test_toffoli_size_of_bimultiplication():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            swap2cnot,
            multi_not_rules,
            addition_rules,
            increment_rules,
            modular_addition_rules,
            modular_bimultiplication_rules,
            modular_scaled_addition_rules,
            pivot_flip_rules,
            offset_rules,
            modular_double_rules,
            rotate_bits_rules,
            reverse_bits_rules,
            predict_overflow_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])

    t1 = eng.allocate_qureg(5)
    t2 = eng.allocate_qureg(5)
    controls = eng.allocate_qureg(1)
    modulus = 29
    factor = 17

    ModularBimultiplicationGate(factor, modulus) & controls | (t1, t2)

    assert 30000 < len(rec.received_commands) < 60000


def test_fuzz_bimultiplication():
    for _ in range(10):
        n = 10
        cn = 1
        mod = 1001
        f = 5
        inv_f = 801
        assert f * inv_f % mod == 1
        op = ModularBimultiplicationGate(5, mod)
        fuzz_permutation_circuit(
            register_sizes=[n, cn, n],
            register_limits=[mod, 1 << cn, mod],
            permutation=lambda ns, (a, c, b):
                (a, c, b)
                if c != 2**cn - 1
                else (a*f % mod, c, b*-inv_f % mod),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    modular_bimultiplication_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_all=True,
                    ban_classes=[ModularBimultiplicationGate]
                )
            ],
            actions=lambda eng, regs: op & regs[1] | (regs[0], regs[2]))
