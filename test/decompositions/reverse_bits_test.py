# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq import MainEngine
from projectq.cengines import DummyEngine, DecompositionRuleSet
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    multi_not_rules,
    reverse_bits_rules,
)
from dirty_period_finding.decompositions.reverse_bits_rules import (
    decompose_into_big_swap,
    decompose_into_cswaps,
)
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import ReverseBits
from .._test_util import (
    decomposition_to_ascii,
    check_permutation_decomposition
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


def test_reverse_operation():
    assert ReverseBits.do_operation((7,), (0b1011001,)) == (0b1001101,)
    assert ReverseBits.do_operation((7,), (1,)) == (1 << 6,)
    assert ReverseBits.do_operation((8,), (1,)) == (1 << 7,)


def test_decompose_into_big_swap():
    for register_size in range(1, 100):
        for control_size in range(2, 4):

            check_permutation_decomposition(
                decomposition_rule=decompose_into_big_swap,
                gate=ReverseBits,
                register_sizes=[register_size],
                control_size=control_size)


def test_decompose_into_cswaps():
    for register_size in range(1, 100):
        for control_size in range(2):

            check_permutation_decomposition(
                decomposition_rule=decompose_into_cswaps,
                gate=ReverseBits,
                register_sizes=[register_size],
                control_size=control_size)


def test_diagram_decompose_into_big_swap():
    text_diagram = decomposition_to_ascii(
        gate=ReverseBits,
        decomposition_rule=decompose_into_big_swap,
        register_sizes=[10],
        control_size=2)
    print(text_diagram)
    assert text_diagram == """
|0>-@---------@---------@-----------------
    |         |         |
|0>-@---------@---------@-----------------
    |         |         |
|0>-|-@-------|-X-------|-X-------@-------
    | |       | |       | |       |
|0>-|-|-@-----|-|-X-----|-|-X-----|-@-----
    | | |     | | |     | | |     | |
|0>-|-|-|-@---|-|-|-X---|-|-|-X---|-|-@---
    | | | |   | | | |   | | | |   | | |
|0>-|-|-|-|-@-|-|-|-|-X-|-|-|-|-X-|-|-|-@-
    | | | | | | | | | | | | | | | | | | |
|0>-*-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-
    | | | | | | | | | | | | | | | | | | |
|0>-*-|-|-|-|-X-@-@-@-@-X-@-@-@-@-|-|-|-|-
      | | | |   | | | |   | | | | | | | |
|0>---|-|-|-X---|-|-|-@---|-|-|-@-|-|-|-X-
      | | |     | | |     | | |   | | |
|0>---|-|-X-----|-|-@-----|-|-@---|-|-X---
      | |       | |       | |     | |
|0>---|-X-------|-@-------|-@-----|-X-----
      |         |         |       |
|0>---X---------@---------@-------X-------
        """.strip()


def test_diagram_decompose_into_cswaps():
    text_diagram = decomposition_to_ascii(
        gate=ReverseBits,
        decomposition_rule=decompose_into_cswaps,
        register_sizes=[10],
        control_size=1)
    print(text_diagram)
    assert text_diagram == """
|0>-@-@-@-@-@-
    | | | | |
|0>-*-|-|-|-|-
    | | | | |
|0>-|-*-|-|-|-
    | | | | |
|0>-|-|-*-|-|-
    | | | | |
|0>-|-|-|-*-|-
    | | | | |
|0>-|-|-|-|-*-
    | | | | |
|0>-|-|-|-|-*-
    | | | |
|0>-|-|-|-*---
    | | |
|0>-|-|-*-----
    | |
|0>-|-*-------
    |
|0>-*---------
        """.strip()
