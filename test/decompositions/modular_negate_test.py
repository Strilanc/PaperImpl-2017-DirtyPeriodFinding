# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import fractions

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
    comparison_rules,
    modular_negate_rules,
)
from dirty_period_finding.decompositions.modular_negate_rules import (
    decompose_modular_negate,
)
from dirty_period_finding.extensions import (
    AutoReplacerEx,
    LimitedCapabilityEngine,
)
from dirty_period_finding.gates import (
    ModularNegate,
)
from .._test_util import (
    decomposition_to_ascii,
    cover,
    check_permutation_decomposition,
)


def test_toffoli_size_of_modular_negate():
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            swap2cnot,
            multi_not_rules,
            addition_rules,
            increment_rules,
            pivot_flip_rules,
            offset_rules,
            comparison_rules,
            modular_negate_rules,
        ])),
        LimitedCapabilityEngine(
            allow_toffoli=True,
        ),
    ])

    t = eng.allocate_qureg(5)
    controls = eng.allocate_qureg(1)
    workspace = eng.allocate_qureg(2)
    modulus = 29

    ModularNegate(modulus) & controls | t

    assert 100 < len(rec.received_commands) < 200
    assert workspace is not None


def test_bimultiplication_operation():
    assert ModularNegate(13).do_operation(0) == (0,)
    assert ModularNegate(13).do_operation(1) == (12,)
    assert ModularNegate(13).do_operation(2) == (11,)
    assert ModularNegate(13).do_operation(11) == (2,)
    assert ModularNegate(13).do_operation(12) == (1,)
    assert ModularNegate(13).do_operation(13) == (13,)
    assert ModularNegate(13).do_operation(14) == (14,)


def test_decompose_modular_negate():
    for register_size in range(1, 100):
        for control_size in range(3):
            for h_modulus in cover(1 << register_size):
                modulus = h_modulus + 1
                check_permutation_decomposition(
                    decomposition_rule=decompose_modular_negate,
                    gate=ModularNegate(modulus),
                    register_sizes=[register_size],
                    control_size=control_size,
                    register_limits=[modulus])


def test_diagram_decompose_modular_negate():
    text_diagram = decomposition_to_ascii(
        gate=ModularNegate(13),
        decomposition_rule=decompose_modular_negate,
        register_sizes=[4],
        control_size=1)
    print(text_diagram)
    assert text_diagram == """
|0>----------------@----------------
    .------. .-----|-----. .------.
|0>-|      |-|           |-|      |-
    |      | |           | |      |
|0>-|      |-|           |-|      |-
    |      | |           | |      |
|0>-|  −1  |-|  Flip<12  |-|  +1  |-
    |      | |           | |      |
|0>-|      |-|           |-|      |-
    `------` `-----------` `------`
        """.strip()
