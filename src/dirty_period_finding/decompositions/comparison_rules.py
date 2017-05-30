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

from projectq.cengines import DecompositionRule
from projectq.ops import X

from dirty_period_finding.extensions import (
    workspace,
    min_workspace_vs_reg1,
    max_controls,
)
from dirty_period_finding.gates import (
    LessThanConstantGate,
    MultiNot,
    PredictOffsetOverflowGate,
    XorOffsetCarrySignalsGate,
    OffsetGate,
)


def do_predict_carry_signals(offset, query_reg, target_reg):
    """
    Source:
        Thomas Häner, Martin Roetteler, and Krysta M. Svore, 2016.
        "Factoring using 2n+2 qubits with Toffoli based modular multiplication"
    Diagram:
        . ═══●═════════════════●═════════════════●══════
        .    │                 │                 │
        o ═══╪●════════════════╪●════════════════╪●═════
        f    ││                ││                ││
        f ═══╪╪●═══════════════╪╪●═══════════════╪╪●════
        s    │││               │││               │││
        e ═══╪╪╪●══════════════╪╪╪●══════════════╪╪╪●═══
        t    ││││              ││││              ││││
        . ═══╪╪╪╪●═════════════╪╪╪╪●═════════════╪╪╪╪●══
             │││││             │││││             │││││
             │││││             │││││             │││││
             │││││             │││││             │││││
        . ───⊕┼┼┼┼─────────────○┼┼┼┼─────────────⊕┼┼┼┼──
        .     ││││             │││││              ││││
        q ────⊕┼┼┼────────●────┼○┼┼┼────●─────────⊕┼┼┼──
        u      │││        │    │││││    │          │││
        e ─────⊕┼┼──────●─┼────┼┼○┼┼────┼─●────────⊕┼┼──
        r       ││      │ │    │││││    │ │         ││
        y ──────⊕┼────●─┼─┼────┼┼┼○┼────┼─┼─●───────⊕┼──
        .        │    │ │ │    │││││    │ │ │        │
        . ───────⊕──●─┼─┼─┼────┼┼┼┼○────┼─┼─┼─●──────⊕──
                    │ │ │ │    │││││    │ │ │ │
                    │ │ │ │    │││││    │ │ │ │
                    │ │ │ │    │││││    │ │ │ │
        . ──────────┼─┼─┼─●────⊕┼┼┼┼────●─┼─┼─┼─────────
        t           │ │ │ │     ││││    │ │ │ │
        a ──────────┼─┼─●─⊕─────⊕┼┼┼────⊕─●─┼─┼─────────
        r           │ │ │        │││      │ │ │
        g ──────────┼─●─⊕────────⊕┼┼──────⊕─●─┼─────────
        e           │ │           ││        │ │
        t ──────────●─⊕───────────⊕┼────────⊕─●─────────
        .           │              │          │
        . ──────────⊕──────────────⊕──────────⊕─────────
    Args:
        offset (int):
        query_reg (projectq.types.Qureg):
        target_reg (projectq.types.Qureg):
    """
    n = len(query_reg)
    assert len(target_reg) == n
    assert 0 <= offset < 1 << n
    offset_bits = [bool((offset >> i) & 1) for i in range(n)]

    offset_bit_targets = [query_reg[i] for i in range(n) if offset_bits[i]]
    MultiNot | offset_bit_targets

    # Sweep high-to-low.
    for i in range(1, n)[::-1]:
        X & query_reg[i] & target_reg[i - 1] | target_reg[i]

    # Twiddle target.
    for i in range(n):
        if offset_bits[i]:
            X & query_reg[i] | target_reg[i]
            X | target_reg[i]

    # Sweep low-to-high.
    for i in range(1, n):
        X & query_reg[i] & target_reg[i - 1] | target_reg[i]

    MultiNot | offset_bit_targets


def do_predict_overflow(offset, query_reg, target_bit, controls, dirty_reg):
    """
    N: len(query_reg)
    C: len(controls)
    Size: O(N + C)
    Depth: O(N + C)
    Dirty workspace: N-1
    Diagram:
                  c
        control ━━/━━━●━━━━━━━━━━━━━●━━━━━━━━━━━━●━━━
                      │             │            │
                 n-1  │  ┌──────┐   │  ┌──────┐  │
                ══/═══╪══╡offset╞═══╪══╡offset╞══╪═══
         offset       │  └──┬───┘   │  └──┬───┘  │
                ──────●─────┼──────●┼●────┼─────●┼●──
                      │     │      │││    │     │││
                 n-1  │  ┌──┴───┐  │││ ┌──┴───┐ │││
                ━━/━━━┿━━┥query ┝━━┿┿┿━┥query ┝━┿┿┿━━
          query       │  └──┬───┘  │││ └──┬───┘ │││
                ──────●─────┼──────⊕●⊕────┼─────⊕●⊕──
                      │     │       │     │      │
                 n-2  │  ┌──┴───┐   │  ┌──┴───┐  │
          dirty ━━/━━━┿━━┥⊕carry┝━━━┿━━┥⊕carry┝━━┿━━━
                ──────┼──┤ sigs ├───●──┤ sigs ├──●───
                      │  └──────┘   │  └──────┘  │
         target ──────⊕─────────────⊕────────────⊕───

    Source:
        Thomas Häner, Martin Roetteler, and Krysta M. Svore, 2016.
        "Factoring using 2n+2 qubits with Toffoli based modular multiplication"
    Args:
        offset (int):
            The amount to pretend to add into the query register, to see if
            an overflow occurs.
        query_reg (projectq.types.Qureg):
            The register that we want to know if it will overflow.
        target_bit (projectq.types.Qubit):
            The bit to toggle if the register will overflow when offset.
        controls (list[projectq.types.Qubit]):
            Conditions the operation.
        dirty_reg (projectq.types.Qureg):
            Workspace register with one less qubit than the query register.
    """
    n = len(query_reg)
    assert len(dirty_reg) == n - 1
    assert 0 <= offset < 1 << n

    m = 1 << (n-1)
    offset_low, offset_top = offset & ~m, offset & m
    query_low, query_top = query_reg[:-1], query_reg[-1]

    if offset_top:
        X & controls & query_top | target_bit

    if n == 1:
        return

    for _ in range(2):
        XorOffsetCarrySignalsGate(offset_low) | (query_reg[:-1], dirty_reg)

        if offset_top:
            X | query_top
        X & controls & query_top & dirty_reg[-1] | target_bit
        if offset_top:
            X | query_top


def do_comparison_to_overflow(gate, comparand_reg, target_bit, controls):
    """
    N: len(query_reg)
    C: len(controls)
    Size: O(N + C)
    Depth: O(N + C)
    Args:
        gate (LessThanConstantGate):
            The gate to decompose, containing the constant to compare against.
        comparand_reg (projectq.types.Qureg):
            The register that we want to compare against a constant.
        target_bit (projectq.types.Qureg):
            The bit to toggle if the comparison is satisfied.
        controls (list[projectq.types.Qubit]):
            Conditions the operation.
    """
    # Trivial case: can't be satisfied.
    if gate.comparand <= 0:
        return

    # Trivial case: always satisfied.
    overflow_val = 1 << len(comparand_reg)
    if gate.comparand >= overflow_val:
        X & controls | target_bit
        return

    g = PredictOffsetOverflowGate(overflow_val - gate.comparand)
    g & controls | (comparand_reg, target_bit)
    X & controls | target_bit


def do_add_subtract_comparison(gate, comparand_reg, target_bit, controls):
    """
    N: len(query_reg)
    C: len(controls)
    Size: O(N + C)
    Depth: O(N + C)
    Args:
        gate (LessThanConstantGate):
            The gate to decompose, containing the constant to compare against.
        comparand_reg (projectq.types.Qureg):
            The register that we want to compare against a constant.
        target_bit (projectq.types.Qureg):
            The bit to toggle if the comparison is satisfied.
        controls (list[projectq.types.Qubit]):
            Conditions the operation.
    """
    # Trivial case: can't be satisfied.
    if gate.comparand <= 0:
        return

    # Trivial case: always satisfied.
    overflow_val = 1 << len(comparand_reg)
    if gate.comparand >= overflow_val:
        X & controls | target_bit
        return

    OffsetGate(-gate.comparand) & controls | comparand_reg + target_bit
    OffsetGate(gate.comparand) & controls | comparand_reg


decompose_xor_offset_carry_signals = DecompositionRule(
    gate_class=XorOffsetCarrySignalsGate,
    gate_recognizer=max_controls(0),
    gate_decomposer=lambda cmd: do_predict_carry_signals(
        offset=cmd.gate.offset,
        query_reg=cmd.qubits[0],
        target_reg=cmd.qubits[1]))

decompose_overflow = DecompositionRule(
    gate_class=PredictOffsetOverflowGate,
    gate_recognizer=min_workspace_vs_reg1(1, offset=-1),
    gate_decomposer=lambda cmd: do_predict_overflow(
        offset=cmd.gate.offset,
        query_reg=cmd.qubits[0],
        target_bit=cmd.qubits[1],
        dirty_reg=workspace(cmd)[:len(cmd.qubits[0]) - 1],
        controls=cmd.control_qubits))

decompose_less_than_into_overflow = DecompositionRule(
    gate_class=LessThanConstantGate,
    gate_recognizer=min_workspace_vs_reg1(1, offset=-1),
    gate_decomposer=lambda cmd: do_comparison_to_overflow(
        gate=cmd.gate,
        comparand_reg=cmd.qubits[0],
        target_bit=cmd.qubits[1],
        controls=cmd.control_qubits))

decompose_less_than_low_workspace = DecompositionRule(
    gate_class=LessThanConstantGate,
    gate_decomposer=lambda cmd: do_add_subtract_comparison(
        gate=cmd.gate,
        comparand_reg=cmd.qubits[0],
        target_bit=cmd.qubits[1],
        controls=cmd.control_qubits))


all_defined_decomposition_rules = [
    decompose_xor_offset_carry_signals,
    decompose_less_than_into_overflow,
    decompose_less_than_low_workspace,
    decompose_overflow,
]
