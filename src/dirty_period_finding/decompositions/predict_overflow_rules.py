# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule

from dirty_period_finding.extensions import (
    workspace,
    min_workspace_vs_reg1,
)
from dirty_period_finding.gates import (
    LessThanConstantGate,
    MultiNot,
    PredictOffsetOverflowGate,
    X,
)


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
    assert 0 <= offset < 1 << n

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
        target_bit (projectq.types.Qubit):
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


all_defined_decomposition_rules = [
    DecompositionRule(
        gate_class=PredictOffsetOverflowGate,
        gate_recognizer=min_workspace_vs_reg1(1, offset=-1),
        gate_decomposer=lambda cmd: do_predict_overflow(
            offset=cmd.gate.offset,
            query_reg=cmd.qubits[0],
            target_bit=cmd.qubits[1],
            dirty_reg=workspace(cmd)[:len(cmd.qubits[0]) - 1],
            controls=cmd.control_qubits)),

    DecompositionRule(
        gate_class=LessThanConstantGate,
        gate_decomposer=lambda cmd: do_comparison_to_overflow(
            gate=cmd.gate,
            comparand_reg=cmd.qubits[0],
            target_bit=cmd.qubits[1],
            controls=cmd.control_qubits)),
]
