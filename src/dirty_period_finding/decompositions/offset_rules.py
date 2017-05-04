# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math

from projectq.cengines import DecompositionRule

from dirty_period_finding.gates import X
from dirty_period_finding.extensions import (
    min_workspace,
    min_controls,
    max_controls,
    workspace,
)
from dirty_period_finding.gates import Increment, OffsetGate, MultiNot


def do_predict_carry_signals(offset_bits, query_reg, target_reg):
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
        . ───⊕┼┼┼┼─────────────●┼┼┼┼─────────────⊕┼┼┼┼──
        .     ││││             │││││              ││││
        q ────⊕┼┼┼────────●────┼●┼┼┼────●─────────⊕┼┼┼──
        u      │││        │    │││││    │          │││
        e ─────⊕┼┼──────●─┼────┼┼●┼┼────┼─●────────⊕┼┼──
        r       ││      │ │    │││││    │ │         ││
        y ──────⊕┼────●─┼─┼────┼┼┼●┼────┼─┼─●───────⊕┼──
        .        │    │ │ │    │││││    │ │ │        │
        . ───────⊕──●─┼─┼─┼────┼┼┼┼●────┼─┼─┼─●──────⊕──
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
        offset_bits (list[bool]):
        query_reg (projectq.types.Qureg):
        target_reg (projectq.types.Qureg):
    """
    n = len(offset_bits)
    target_ons = [query_reg[i] for i in range(n) if offset_bits[i]]

    MultiNot | target_ons

    # Sweep high-to-low.
    for i in range(1, n)[::-1]:
        X & query_reg[i] & target_reg[i - 1] | target_reg[i]

    # Twiddle target.
    for i in range(n):
        if offset_bits[i]:
            X | query_reg[i]
            X & query_reg[i] | target_reg[i]
            X | query_reg[i]

    # Sweep low-to-high.
    for i in range(1, n):
        X & query_reg[i] & target_reg[i - 1] | target_reg[i]

    MultiNot | target_ons


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
         offset ══/═══╪══╡offset╞═══╪══╡offset╞══╪═══
                      │  └──┬───┘   │  └──┬───┘  │
                ──────●─────┼──────●┼●────┼─────●┼●──
                      │     │      │││    │     │││
                 n-1  │  ┌──┴───┐  │││ ┌──┴───┐ │││
          query ━━/━━━┿━━┥query ┝━━┿┿┿━┥query ┝━┿┿┿━━
                      │  └──┬───┘  │││ └──┬───┘ │││
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

    offset_bits = [bool((offset >> i) & 1) for i in range(n)]

    if offset_bits[-1]:
        X & controls & query_reg[-1] | target_bit

    if n == 1:
        return

    for _ in range(2):
        do_predict_carry_signals(offset_bits[:-1], query_reg[:-1], dirty_reg)

        if offset_bits[-1]:
            X | query_reg[-1]
        X & controls & query_reg[-1] & dirty_reg[-1] | target_bit
        if offset_bits[-1]:
            X | query_reg[-1]


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

    # Increment high part based on predicted carry signal from low part.
    Increment & dirty_qubit | high
    MultiNot & dirty_qubit | high
    do_predict_overflow(offset, low, dirty_qubit, controls, high[:h-1])
    Increment & dirty_qubit | high
    do_predict_overflow(offset, low, dirty_qubit, controls, high[:h-1])
    MultiNot & dirty_qubit | high

    # Separately recurse on low and high parts.
    mask = (~0 << h)
    low_offset = offset & ~mask
    high_offset = (offset & mask) >> h
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
