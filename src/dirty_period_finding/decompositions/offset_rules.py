# -*- coding: utf-8 -*-

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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


def do_decrease_size(offset, target_reg, controls):
    jump = 0
    while offset & 1 == 0:
        if not offset:
            return
        offset >>= 1
        jump += 1

    OffsetGate(offset) & controls | target_reg[jump:]


decompose_decrease_size = DecompositionRule(
    gate_class=OffsetGate,
    gate_recognizer=lambda cmd: cmd.gate.offset & 1 == 0,
    gate_decomposer=lambda cmd: do_decrease_size(
        offset=cmd.gate.offset,
        target_reg=cmd.qubits[0],
        controls=cmd.control_qubits))


decompose_remove_controls = DecompositionRule(
    gate_class=OffsetGate,
    gate_recognizer=min_controls(1) & min_workspace(1),
    gate_decomposer=lambda cmd: do_controlled_offset(
        gate=cmd.gate,
        target_reg=cmd.qubits[0],
        controls=cmd.control_qubits,
        dirty_qubit=workspace(cmd)[0]))

decompose_into_range_increments = DecompositionRule(
    gate_class=OffsetGate,
    gate_recognizer=max_controls(0) & _better_to_use_bitrange_offset,
    gate_decomposer=lambda cmd: do_bitrange_offset(
        offset=cmd.gate.offset,
        target_reg=cmd.qubits[0]))

decompose_into_recursion = DecompositionRule(
    gate_class=OffsetGate,
    gate_recognizer=max_controls(0) & min_workspace(1),
    gate_decomposer=lambda cmd: do_recursive_offset(
        gate=cmd.gate,
        target_reg=cmd.qubits[0],
        controls=cmd.control_qubits,
        dirty_qubit=workspace(cmd)[0]))


all_defined_decomposition_rules = [
    # Even offsets can be reduced to smaller odd offsets.
    decompose_decrease_size,
    # Separate the controlling from the offsetting.
    decompose_remove_controls,
    # For simple offsets, just use increments and decrements.
    decompose_into_range_increments,
    # Divide-and-conquer an uncontrolled offset.
    decompose_into_recursion,
]
