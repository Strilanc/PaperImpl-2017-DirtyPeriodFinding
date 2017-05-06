# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq import MainEngine
from projectq.cengines import DecompositionRuleSet, DummyEngine
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    addition_rules,
    increment_rules,
    multi_not_rules
)
from dirty_period_finding.decompositions.increment_rules import (
    decompose_increment_into_cnot_triangle,
    decompose_increment_with_low_workspace,
    decompose_increment_high_workspace,
)
from dirty_period_finding.extensions import (
    AutoReplacerEx,
    LimitedCapabilityEngine,
)
from dirty_period_finding.gates import Decrement, Increment
from .._test_util import (
    check_permutation_decomposition,
    decomposition_to_ascii
)


def test_increment_operation():
    assert Increment.do_operation(101) == (102,)
    assert Increment.do_operation(5) == (6,)
    assert Decrement.do_operation(101) == (100,)
    assert Decrement.do_operation(5) == (4,)


def test_toffoli_size_of_increment():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
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


def test_decompose_increment_into_cnot_triangle():
    for register_size in range(9):
        for control_size in range(4):
            check_permutation_decomposition(
                decomposition_rule=decompose_increment_into_cnot_triangle,
                gate=Increment,
                register_sizes=[register_size],
                control_size=control_size)


def test_decompose_increment_with_low_workspace():
    for register_size in range(100):
        for control_size in range(3):
            check_permutation_decomposition(
                decomposition_rule=decompose_increment_with_low_workspace,
                gate=Increment,
                register_sizes=[register_size],
                workspace=1,
                control_size=control_size)


def test_decompose_increment_high_workspace():
    for register_size in range(100):
        check_permutation_decomposition(
            decomposition_rule=decompose_increment_high_workspace,
            gate=Increment,
            register_sizes=[register_size],
            workspace=register_size)


def test_diagram_decompose_increment_into_cnot_triangle():
    text_diagram = decomposition_to_ascii(
        decomposition_rule=decompose_increment_into_cnot_triangle,
        gate=Increment,
        register_sizes=[6],
        control_size=1)
    print(text_diagram)
    assert text_diagram == """
|0>-@-@-@-@-@-@-
    | | | | | |
|0>-@-@-@-@-@-X-
    | | | | |
|0>-@-@-@-@-X---
    | | | |
|0>-@-@-@-X-----
    | | |
|0>-@-@-X-------
    | |
|0>-@-X---------
    |
|0>-X-----------
    """.strip()


def test_diagram_decompose_increment_with_low_workspace():
    text_diagram = decomposition_to_ascii(
        decomposition_rule=decompose_increment_with_low_workspace,
        gate=Increment,
        register_sizes=[6],
        workspace=1,
        control_size=1)
    print(text_diagram)
    assert text_diagram == """
|0>--------------@----------@-@----------@----------@-
                 |          | |          |          |
|0>--------------@----------@-@----------@----------X-
        .------. | .------. | | .------. | .------.
|0>-----|      |-@-|      |-@-X-|      |-X-|      |---
        |      | | |      | | | |      | | |      |
|0>-----|  A   |-@-|  A   |-@-X-|  +A  |-X-|  −A  |---
        |      | | |      | | | |      | | |      |
|0>-----|      |-@-|      |-@-X-|      |-X-|      |---
        |------| | |------| | | |------| | |------|
|0>-----|1     |-X-|1     |-X-X-|1     |-X-|1     |---
        |      | | |      | | | |      | | |      |
|0>-----|2 −A  |-X-|2 +A  |-X-X-|2 A   |-X-|2 A   |---
        |      | | |      | | | |      | | |      |
|0>-???-|0     |-X-|0     |-X-X-|0     |-X-|0     |---
        `------`   `------`     `------`   `------`
    """.strip()


def test_diagram_decompose_increment_high_workspace():
    text_diagram = decomposition_to_ascii(
        decomposition_rule=decompose_increment_high_workspace,
        gate=Increment,
        register_sizes=[4],
        workspace=4)
    print(text_diagram)
    assert text_diagram == """
        .------.   .------.
|0>-----|      |---|      |---
        |      |   |      |
|0>-----|      |---|      |---
        |      |   |      |
|0>-----|  −A  |---|  −A  |---
        |      |   |      |
|0>-----|      |---|      |---
        |------|   |------|
|0>-???-|      |-X-|      |-X-
        |      |   |      |
|0>-???-|      |-X-|      |-X-
        |      |   |      |
|0>-???-|  A   |-X-|  A   |-X-
        |      |   |      |
|0>-???-|      |-X-|      |-X-
        `------`   `------`
    """.lstrip('\n').rstrip()
