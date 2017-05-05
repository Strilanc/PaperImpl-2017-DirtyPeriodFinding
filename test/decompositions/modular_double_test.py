# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq import MainEngine
from projectq.cengines import DecompositionRuleSet, DummyEngine
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    modular_double_rules,
    pivot_flip_rules,
    addition_rules,
    increment_rules,
    multi_not_rules,
    offset_rules,
    rotate_bits_rules,
    reverse_bits_rules,
    predict_overflow_rules,
)
from dirty_period_finding.decompositions.modular_double_rules import (
    decompose_into_align_and_rotate
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import (
    ModularDoubleGate,
    ModularUndoubleGate,
)
from .._test_util import (
    check_permutation_decomposition,
    cover,
)


def test_toffoli_size_of_modular_double():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            modular_double_rules,
            pivot_flip_rules,
            offset_rules,
            addition_rules,
            swap2cnot,
            increment_rules,
            multi_not_rules,
            rotate_bits_rules,
            reverse_bits_rules,
            predict_overflow_rules,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(15)
    target = eng.allocate_qureg(16)
    dirty = eng.allocate_qureg(2)
    modulus = 0xAEFD

    ModularDoubleGate(modulus) & controls | target

    assert dirty is not None
    assert 2000 < len(rec.received_commands) < 4000


def test_operation():
    assert ModularDoubleGate(7).do_operation(0) == (0,)
    assert ModularDoubleGate(7).do_operation(1) == (2,)
    assert ModularDoubleGate(7).do_operation(2) == (4,)
    assert ModularDoubleGate(7).do_operation(3) == (6,)
    assert ModularDoubleGate(7).do_operation(4) == (1,)
    assert ModularDoubleGate(7).do_operation(5) == (3,)
    assert ModularDoubleGate(7).do_operation(6) == (5,)

    assert ModularUndoubleGate(7).do_operation(0) == (0,)
    assert ModularUndoubleGate(7).do_operation(2) == (1,)
    assert ModularUndoubleGate(7).do_operation(4) == (2,)
    assert ModularUndoubleGate(7).do_operation(6) == (3,)
    assert ModularUndoubleGate(7).do_operation(1) == (4,)
    assert ModularUndoubleGate(7).do_operation(3) == (5,)
    assert ModularUndoubleGate(7).do_operation(5) == (6,)


def test_decompose_modular_double_into_align_and_rotate():
    for register_size in range(50):
        for control_size in range(3):
            for h_modulus in cover((1 << register_size) // 2):
                modulus = h_modulus*2 + 1

                check_permutation_decomposition(
                    decomposition_rule=decompose_into_align_and_rotate,
                    gate=ModularDoubleGate(modulus),
                    register_sizes=[register_size],
                    control_size=control_size,
                    register_limits=[modulus])
