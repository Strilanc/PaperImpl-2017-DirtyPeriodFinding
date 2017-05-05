# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

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
    predict_overflow_rules,
)
from dirty_period_finding.decompositions.modular_scaled_addition_rules import (
    decompose_into_doubled_addition
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import ModularScaledAdditionGate
from .._test_util import (
    check_permutation_decomposition,
    cover,
)


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
            predict_overflow_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(15)
    target1 = eng.allocate_qureg(8)
    target2 = eng.allocate_qureg(8)
    modulus = 0xAD
    factor = 0x9A

    ModularScaledAdditionGate(factor, modulus) & controls | (target1, target2)

    assert 30000 < len(rec.received_commands) < 60000


def test_scaled_modular_addition_operation():
    assert ModularScaledAdditionGate(3, 11).do_operation(5, 9) == (5, 2)
    assert ModularScaledAdditionGate(-2, 11).do_operation(5, 9) == (5, 10)


def test_decompose_scaled_modular_addition_into_doubled_addition():
    for register_size in range(1, 50):
        for control_size in range(3):
            for h_modulus in cover(1 << (register_size - 1)):
                modulus = h_modulus*2 + 1
                for factor in cover(modulus):

                    check_permutation_decomposition(
                        decomposition_rule=decompose_into_doubled_addition,
                        gate=ModularScaledAdditionGate(factor, modulus),
                        register_sizes=[register_size, register_size],
                        control_size=control_size,
                        register_limits=[modulus, modulus])
