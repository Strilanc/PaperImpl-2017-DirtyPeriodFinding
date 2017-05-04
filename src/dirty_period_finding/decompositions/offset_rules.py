# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math

from projectq.cengines import DecompositionRule

from dirty_period_finding.extensions import (
    min_workspace,
    min_controls,
    max_controls,
    workspace,
)
from dirty_period_finding.gates import (
    Decrement,
    Increment,
    OffsetGate,
    MultiNot,
    PredictOffsetOverflowGate,
)


def estimate_cost_of_bitrange_offset(offset, bit_count):
    bits = [0] + [(offset >> i) & 1 for i in range(bit_count)]
    cost = 0

    for i in range(bit_count):
        # An increase forces an increment.
        if bits[i + 1] and not bits[i]:
            cost += 1

        # A hold followed by a decrease pairs a decrement to the increment.
        if not bits[i + 1] and bits[i] and bits[i - 1]:
            cost += 1

    return cost


def do_bitrange_offset(offset, target_reg):
    n = len(target_reg)
    bits = [(offset >> i) & 1 for i in range(n)]
    ops = []

    i = 0
    while i < n:
        if not bits[i]:
            i += 1
            continue

        next_zero = i + 1
        while next_zero < n and bits[next_zero]:
            next_zero += 1

        if next_zero == i + 1:
            Increment | target_reg[i:]
        else:
            Decrement | target_reg[i:]
            Increment | target_reg[next_zero:]

        i = next_zero
    return ops


def do_recursive_offset(gate, target_reg, dirty_qubit, controls):
    """
    N: len(target_reg)
    C: len(controls)
    Size: O(N*C)
    Depth: O(N*C)
    Source:
        Thomas Häner, Martin Roetteler, and Krysta M. Svore, 2016.
        "Factoring using 2n+2 qubits with Toffoli based modular multiplication"
    Args:
        gate (OffsetGate):
            The gate being applied (contains offset info).
        target_reg (projectq.types.Qureg):
            The destination register, whose value is increased by the offset
            (with wraparound).
        dirty_qubit (projectq.types.Qubit):
            Workspace.
        controls (list[Qubit]):
            Control qubits.
    """
    offset = gate.offset & ~(~0 << len(target_reg))

    # Trivial case: adding zero does nothing.
    if offset == 0:
        return

    # Trivial case: adding a power of 2 is a shifted increment.
    if (offset - 1) & offset == 0:
        power = int(math.floor(0.5 + math.log(offset, 2)))
        Increment & controls | target_reg[power:]
        return

    h = len(target_reg) // 2
    low = target_reg[:h]
    high = target_reg[h:]
    mask = (~0 << h)
    low_offset = offset & ~mask
    high_offset = (offset & mask) >> h

    # Increment high part based on predicted carry signal from low part.
    Increment & dirty_qubit | high
    MultiNot & dirty_qubit | high
    PredictOffsetOverflowGate(low_offset) & controls | (low, dirty_qubit)
    Increment & dirty_qubit | high
    PredictOffsetOverflowGate(low_offset) & controls | (low, dirty_qubit)
    MultiNot & dirty_qubit | high

    # Separately recurse on low and high parts.
    OffsetGate(low_offset) & controls | low
    OffsetGate(high_offset) & controls | high


def do_controlled_offset(gate, target_reg, dirty_qubit, controls):
    """
    Separates the controls out of an offset gate using
    double-addition-via-inverted-subtraction trick.

    N: len(target_reg)
    C: len(controls)
    Size: O(N+C)
    Depth: O(N+C)
    Args:
        gate (OffsetGate):
            The gate being applied (contains offset info).
        target_reg (projectq.types.Qureg):
            The destination register, whose value is increased by the offset
            (with wraparound).
        dirty_qubit (projectq.types.Qubit):
            Workspace.
        controls (list[Qubit]):
            Control qubits.
    """
    if len(target_reg) == 0:
        return

    t = [dirty_qubit] + target_reg

    gate | t

    MultiNot & controls | t
    gate.get_inverse() | t
    MultiNot & controls | t


def _better_to_use_bitrange_offset(cmd):
    c = estimate_cost_of_bitrange_offset(cmd.gate.offset, len(cmd.qubits[0]))
    return c <= 4


all_defined_decomposition_rules = [
    # Separate the controlling from the offsetting.
    DecompositionRule(
        gate_class=OffsetGate,
        gate_recognizer=min_controls(1) & min_workspace(1),
        gate_decomposer=lambda cmd: do_controlled_offset(
            gate=cmd.gate,
            target_reg=cmd.qubits[0],
            controls=cmd.control_qubits,
            dirty_qubit=workspace(cmd)[0])),

    # For simple offsets, just use increments and decrements.
    DecompositionRule(
        gate_class=OffsetGate,
        gate_recognizer=max_controls(0) & _better_to_use_bitrange_offset,
        gate_decomposer=lambda cmd: do_bitrange_offset(
            offset=cmd.gate.offset,
            target_reg=cmd.qubits[0])),

    # Divide-and-conquer an uncontrolled offset.
    DecompositionRule(
        gate_class=OffsetGate,
        gate_recognizer=max_controls(0) & min_workspace(1),
        gate_decomposer=lambda cmd: do_recursive_offset(
            gate=cmd.gate,
            target_reg=cmd.qubits[0],
            controls=cmd.control_qubits,
            dirty_qubit=workspace(cmd)[0])),
]
