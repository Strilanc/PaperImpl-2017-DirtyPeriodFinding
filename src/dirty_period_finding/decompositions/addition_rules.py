# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from projectq.meta import Control

from dirty_period_finding.extensions import (
    X,
    Swap,
    min_workspace,
    min_controls,
    max_controls,
    min_register_sizes,
    max_register_sizes,
    workspace,
)
from dirty_period_finding.gates import (
    AdditionGate,
    Increment,
    Decrement,
    MultiNot,
)


def do_addition_with_same_size_and_no_controls(input_reg, target_reg):
    """
    Reversibly adds one register into another of the same size.

    N: len(input_reg) + len(target_reg)
    Size: O(N)
    Depth: O(N)
    Sources:
        Takahashi and Kunihiro, 2005
        "A linear-size quantum circuit for addition with no ancillary qubits"

        Yvan Van Rentergem and Alexis De Vos, 2004
        "Optimal Design of A Reversible Full Adder"
    Diagram:
       ┌───┐
       ┤   ├       ─⊕─────×─────────────────────────────────────×─●───⊕─
       │   │        │     │                                     │ │   │
       ┤   ├       ─⊕─────┼────×───────────────────────────×─●──┼─┼───⊕─
       │   │        │     │    │                           │ │  │ │   │
       ┤inp├       ─⊕─────┼────┼────×─────────────────×─●──┼─┼──┼─┼───⊕─
       │ A │        │     │    │    │                 │ │  │ │  │ │   │
       ┤   ├       ─⊕─────┼────┼────┼────×───────×─●──┼─┼──┼─┼──┼─┼───⊕─
       │   │        │     │    │    │    │       │ │  │ │  │ │  │ │   │
       ┤   ├       ─●───●─×──●─×──●─×──●─×───●───×─┼──×─┼──×─┼──×─┼───●─
       └─┬─┘        │   │ │  │ │  │ │  │ │   │   │ │  │ │  │ │  │ │   │
       ┌─┴─┐   =    │   │ │  │ │  │ │  │ │   │   │ │  │ │  │ │  │ │   │
       ┤   ├       ─⊕───⊕─●──┼─●──┼─┼──┼─┼───┼───┼─┼──┼─┼──┼─┼──●─⊕───⊕─
       │   │        │        │ │  │ │  │ │   │   │ │  │ │  │ │        │
       ┤   ├       ─⊕────────⊕─●──┼─┼──┼─┼───┼───┼─┼──┼─┼──●─⊕────────⊕─
       │   │        │             │ │  │ │   │   │ │  │ │             │
       ┤+=A├       ─⊕─────────────⊕─●──┼─┼───┼───┼─┼──●─⊕─────────────⊕─
       │   │        │                  │ │   │   │ │                  │
       ┤   ├       ─⊕──────────────────⊕─●───┼───●─⊕──────────────────⊕─
       │   │        │                        │                        │
       ┤   ├       ─⊕────────────────────────⊕────────────────────────⊕─
       └───┘
                   (1)  --------(2)-------  (3)  --------(4)-------  (5)
    Args:
        input_reg (projectq.types.Qureg):
            The source register. Used as workspace, but ultimately not affected
            by the operation.
            end.
        target_reg (projectq.types.Qureg):
            The destination register, whose value is increased by the value in
            the source register.
    """
    assert len(input_reg) == len(target_reg)
    n = len(target_reg)
    if n == 0:
        return

    carry_bit = input_reg[-1]

    # (1) Dirty MSB correction.
    MultiNot & carry_bit | (input_reg[:-1] + target_reg)[::-1]

    # (2) Ripple forward.
    for i in range(n - 1):
        X & carry_bit | target_reg[i]
        Swap & target_reg[i] | (carry_bit, input_reg[i])

    # (3) High bit toggle.
    X & carry_bit | target_reg[-1]

    # (4) Ripple backward.
    for i in range(n - 1)[::-1]:
        Swap & target_reg[i] | (carry_bit, input_reg[i])
        X & input_reg[i] | target_reg[i]

    # (5) Dirty MSB correction.
    MultiNot & carry_bit | (input_reg[:-1] + target_reg)


def do_addition_with_larger_target_and_no_controls(input_reg, target_reg):
    """
    Reversibly adds one register into another larger one size.

    N: len(input_reg) + len(target_reg)
    Size: O(N)
    Depth: O(N)
    Diagram:
       ┌───┐
       ┤   ├       ────────────────×─────────────────────────────────────×─●─
       │   │                       │                                     │ │
       ┤   ├       ────────────────┼────×───────────────────────────×─●──┼─┼─
       │   │                       │    │                           │ │  │ │
       ┤inp├       ────────────────┼────┼────×─────────────────×─●──┼─┼──┼─┼─
       │ A │                       │    │    │                 │ │  │ │  │ │
       ┤   ├       ────────────────┼────┼────┼────×───────×─●──┼─┼──┼─┼──┼─┼─
       │   │                       │    │    │    │       │ │  │ │  │ │  │ │
       ┤   ├       ────●────●────●─×──●─×──●─×──●─×───●───×─┼──×─┼──×─┼──×─┼─
       └─┬─┘           │    │    │ │  │ │  │ │  │ │   │   │ │  │ │  │ │  │ │
       ┌─┴─┐   =      ┌┴─┐  │    │ │  │ │  │ │  │ │   │   │ │  │ │  │ │  │ │
       ┤   ├       ───┤  ├──┼────⊕─●──┼─●──┼─┼──┼─┼───┼───┼─┼──┼─┼──┼─┼──●─⊕─
       │   │          │  │  │         │ │  │ │  │ │   │   │ │  │ │  │ │
       ┤   ├       ───┤  ├──┼─────────⊕─●──┼─┼──┼─┼───┼───┼─┼──┼─┼──●─⊕──────
       │   │          │  │  │              │ │  │ │   │   │ │  │ │
       ┤+=A├       ───┤-1├──┼──────────────⊕─●──┼─┼───┼───┼─┼──●─⊕───────────
       │   │          │  │  │                   │ │   │   │ │
       ┤   ├       ───┤  ├──┼───────────────────⊕─●───┼───●─⊕────────────────
       │   │        e │  │ ┌┴─┐                      ┌┴─┐
       ┤   ├       ━/━┥  ┝━┥+1┝━━━━━━━━━━━━━━━━━━━━━━┥+1┝━━━━━━━━━━━━━━━━━━━━
       └───┘          └──┘ └──┘                      └──┘
                       (1)  (2)  -------(3)--------  (4)  --------(5)--------
    Args:
        input_reg (projectq.types.Qureg):
            The source register. Used as workspace, but ultimately not affected
            by the operation.
            end.
        target_reg (projectq.types.Qureg):
            The destination register, whose value is increased by the value in
            the source register.
    """
    assert len(input_reg) <= len(target_reg)
    n = len(input_reg)
    if n == 0:
        return

    carry_bit = input_reg[-1]

    # (1) Dirty MSB correction.
    Decrement & carry_bit | target_reg

    # (2) Handle MSB separately.
    Increment & carry_bit | target_reg[n-1:]

    # (3) Ripple forward.
    for i in range(n - 1):
        X & carry_bit | target_reg[i]
        Swap & target_reg[i] | (carry_bit, input_reg[i])

    # (4) Carry into high output bits.
    Increment & carry_bit | target_reg[n-1:]

    # (5) Ripple backward.
    for i in range(n - 1)[::-1]:
        Swap & target_reg[i] | (carry_bit, input_reg[i])
        X & input_reg[i] | target_reg[i]


def do_addition_no_controls(input_reg, target_reg):
    # When input isn't smaller, just ignore its high bits.
    if len(input_reg) >= len(target_reg):
        do_addition_with_same_size_and_no_controls(
            input_reg[:len(target_reg)], target_reg)
        return

    # When input is larger, use a more expensive construction.
    do_addition_with_larger_target_and_no_controls(input_reg, target_reg)


def do_addition(input_reg, target_reg, dirty, controls):
    if len(controls) == 0:
        return do_addition_no_controls(input_reg, target_reg)

    # Remove controls with double-add-invert trick.
    expanded = [dirty] + target_reg
    for _ in range(2):
        do_addition_no_controls(input_reg, expanded)
        MultiNot & controls | expanded
        MultiNot | expanded


def do_addition_with_all_ops_controlled(eng, input_reg, target_reg, controls):
    with Control(eng, controls):
        do_addition_no_controls(input_reg, target_reg)


all_defined_decomposition_rules = [
    # Trivial case: empty input or empty target. Do nothing.
    DecompositionRule(
        gate_class=AdditionGate,
        gate_decomposer=lambda cmd: None,
        gate_recognizer=lambda cmd:
            len(cmd.qubits[0]) == 0 or len(cmd.qubits[1]) == 0),

    # Trivial case: single target bit. Just a controlled NOT.
    DecompositionRule(
        gate_class=AdditionGate,
        gate_recognizer=
            min_register_sizes(1, 1) &
            max_register_sizes(float('inf'), 1),
        gate_decomposer=lambda cmd:
            X & cmd.control_qubits & cmd.qubits[0][0] | cmd.qubits[1][0]),

    # Trivial case: single input bit. Controlled increment.
    # Minimum control requirement avoids cyclic decomp w.r.t. increment.
    DecompositionRule(
        gate_class=AdditionGate,
        gate_recognizer=
            min_controls(1) &
            min_register_sizes(1, 1) &
            max_register_sizes(1, float('inf')),
        gate_decomposer=lambda cmd:
            Increment & cmd.control_qubits & cmd.qubits[0] | cmd.qubits[1]),

    # Additions without controls can be done inline.
    DecompositionRule(
        gate_class=AdditionGate,
        gate_recognizer=max_controls(0),
        gate_decomposer=lambda cmd: do_addition_no_controls(
            input_reg=cmd.qubits[0],
            target_reg=cmd.qubits[1])),

    # When there's workspace, controlled additions of any size are cheap.
    DecompositionRule(
        gate_class=AdditionGate,
        gate_recognizer=min_workspace(1),
        gate_decomposer=lambda cmd: do_addition(
            input_reg=cmd.qubits[0],
            target_reg=cmd.qubits[1],
            controls=cmd.control_qubits,
            dirty=workspace(cmd)[0])),
]
