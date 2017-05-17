# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from projectq.ops import X

from dirty_period_finding.extensions import (
    Swap,
    min_controls,
    max_controls,
)
from dirty_period_finding.gates import ReverseBitsGate


def do_naive_bit_reverse(target_reg, controls):
    """
    Reverses the order of bits in a register conditioned on all the controls
    with a series of swap gates.

    N: len(target_reg)
    C: len(controls)
    Size: O(N*C)
    Depth: O(N*C)
    Diagram:
       ┌───────┐
       ┤       ├        ───────────×───
       │       │                   │
       ┤       ├        ─────────×─┼───
       │       │                 │ │
       ┤       ├        ───────×─┼─┼───
       │       │               │ │ │
       ┤       ├        ─────×─┼─┼─┼───
       │       │             │ │ │ │
       ┤       ├        ───×─┼─┼─┼─┼───
       │Reverse│    =      │ │ │ │ │
       ┤       ├        ───×─┼─┼─┼─┼───
       │       │           │ │ │ │ │
       ┤       ├        ───┼─×─┼─┼─┼───
       │       │           │ │ │ │ │
       ┤       ├        ───┼─┼─×─┼─┼───
       │       │           │ │ │ │ │
       ┤       ├        ───┼─┼─┼─×─┼───
       │       │           │ │ │ │ │
       ┤       ├        ───┼─┼─┼─┼─×───
       └───┬───┘           │ │ │ │ │
        c  │             c │ │ │ │ │
       ━/━━●━━━━        ━/━●━●━●━●━●━━━
    Args:
        target_reg (projectq.types.Qureg):
            The register to reverse.
        controls (list[projectq.types.Qubit]):
            Qubits that condition the operation.
    """
    for i in range(len(target_reg) // 2):
        Swap & controls | (target_reg[i], target_reg[-i-1])


def do_efficient_controlled_bit_reverse(target_reg, controls):
    """
    Reverses the order of bits in a register conditioned on all the controls
    by finding workspace to allow toggle-controlling big swaps.

    N: len(target_reg)
    C: len(controls)
    Size: O(N + C)
    Depth: O(N + C)
    Diagram:
       ┌───────┐               ┌─────┐
       ┤       ├        ───────┤     ├──
       │       │               │     │
       ┤       ├        ───────┤     ├──
       │       │               │Swap1│
       ┤       ├        ───────┤     ├──
       │       │               │     │
       ┤       ├        ───────┤     ├──
       │       │               └──┬──┘
       ┤       ├        ───×──────┼─────
       │Reverse│    =      │      │
       ┤       ├        ───×──────┼─────
       │       │           │   ┌──┴──┐
       ┤       ├        ───┼───┤     ├──
       │       │           │   │     │
       ┤       ├        ───┼───┤     ├──
       │       │           │   │Swap2│
       ┤       ├        ───┼───┤(rev)├──
       │       │           │   │     │
       ┤       ├        ───┼───┤     ├──
       └───┬───┘           │   └──┬──┘
        c  │             c │      │
       ━/━━●━━━━        ━/━●━━━━━━●━━━━━
    Args:
        target_reg (projectq.types.Qureg):
            The register to reverse.
        controls (list[projectq.types.Qubit]):
            Qubits that condition the operation.
    """
    # Do-nothing cases.
    if len(target_reg) <= 1:
        return
    h = len(target_reg) // 2

    # In the even case, there's no workspace for future decompositions to use.
    # So we handle two bits separately, making room.
    if len(target_reg) % 2 == 0:
        Swap & controls | (target_reg[h-1], target_reg[h])
        low = target_reg[:h-1]
        high = target_reg[h+1:]
        dirty = target_reg[h]
    else:
        low = target_reg[:h]
        dirty = target_reg[h]
        high = target_reg[h+1:]

    do_controlled_multi_swap(low, high[::-1], dirty, controls)


def do_controlled_multi_swap(reg1, reg2, dirty, controls):
    """
    Swaps the contents of two equal-sized registers, using a dirty qubit as
    workspace to toggle-control the middle CNOTs of a xor-swapping construct.

    N: len(low) + len(high) + len(controls)
    Size: O(N)
    Depth: O(N)
    Diagram:
       ┌─────┐
       ┤     ├        ─────●────────⊕──────⊕──────●─────
       │     │             │        │      │      │
       ┤     ├        ─────┼●───────┼⊕─────┼⊕─────┼●────
       │Swap1│             ││       ││     ││     ││
       ┤     ├        ─────┼┼●──────┼┼⊕────┼┼⊕────┼┼●───
       │     │             │││      │││    │││    │││
       ┤     ├        ─────┼┼┼●─────┼┼┼⊕───┼┼┼⊕───┼┼┼●──
       └──┬──┘             ││││     ││││   ││││   ││││
          │                ││││     ││││   ││││   ││││
       ───┼───   =    ─────┼┼┼┼───⊕─●●●●─⊕─●●●●───┼┼┼┼──
          │                ││││   │ ││││ │ ││││   ││││
       ┌──┴──┐             ││││   │ ││││ │ ││││   ││││
       ┤     ├        ─────┼┼┼⊕───┼─┼┼┼●─┼─┼┼┼●───┼┼┼⊕──
       │     │             │││    │ │││  │ │││    │││
       ┤     ├        ─────┼┼⊕────┼─┼┼●──┼─┼┼●────┼┼⊕───
       │Swap2│             ││     │ ││   │ ││     ││
       ┤     ├        ─────┼⊕─────┼─┼●───┼─┼●─────┼⊕────
       │     │             │      │ │    │ │      │
       ┤     ├        ─────⊕──────┼─●────┼─●──────⊕─────
       └──┬──┘                    │      │
        c │            c          │      │
       ━/━●━━━        ━/━━━━━━━━━━●━━━━━━●━━━━━━━━━━━━━━
    Args:
        reg1 (projectq.types.Qureg):
            One of the registers to swap.
        reg2 (projectq.types.Qureg):
            The other register to swap.
        dirty (projectq.types.Qubit):
            Workspace for the operation.
        controls (list[projectq.types.Qubit]):
            Qubits that condition the operation.
    """
    assert len(reg1) == len(reg2)
    n = len(reg1)

    for i in range(n):
        X & reg1[i] | reg2[i]

    for _ in range(2):
        X & controls | dirty
        for i in range(n):
            X & dirty & reg2[i] | reg1[i]

    for i in range(n):
        X & reg1[i] | reg2[i]


decompose_into_cswaps = DecompositionRule(
    gate_class=ReverseBitsGate,
    gate_recognizer=max_controls(1),
    gate_decomposer=lambda cmd: do_naive_bit_reverse(
        target_reg=cmd.qubits[0],
        controls=cmd.control_qubits))


decompose_into_big_swap = DecompositionRule(
    gate_class=ReverseBitsGate,
    gate_recognizer=min_controls(2),
    gate_decomposer=lambda cmd: do_efficient_controlled_bit_reverse(
        target_reg=cmd.qubits[0],
        controls=cmd.control_qubits))


all_defined_decomposition_rules = [
    # When there aren't many controls, just do a bunch of C-Swaps.
    decompose_into_cswaps,

    # When there are more controls, do part of the operation then use the
    # free'd up workspace to toggle-control the rest.
    decompose_into_big_swap,
]
