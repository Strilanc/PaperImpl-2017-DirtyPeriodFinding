# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from projectq.ops import Z

from dirty_period_finding.extensions import max_controls
from dirty_period_finding.gates import PhaseGradientGate


def do_phase_gradient(target_reg, controls, factor):
    """
    Applies a phase gradient to a register.
    If the register has size n, each state |k⟩ will be phased by factor*k/2**n.

    N: len(target_reg)
    C: len(controls)
    Size: O(N*C)
    Depth: O(C)
    Diagram:
       ┌─────┐         ┌────────┐
       ┤     ├        ─┤Z^(t/16)├─
       │     │         ├────────┤
       ┤     ├        ─┤Z^(t/8) ├─
       │     │         ├────────┤
       ┤    t├   =>   ─┤Z^(t/4) ├─
       │Grad │         ├────────┤
       ┤     ├        ─┤Z^(t/2) ├─
       │     │         ├────────┤
       ┤     ├        ─┤   Z^t  ├─
       └─────┘         └────────┘
    Args:
        target_reg (projectq.types.Qureg):
            The register storing the amount to phase proportional to.
        controls (list[projectq.types.Qubit]):
            Qubits that condition the operation.
        factor (int|float|fractions.Fraction):
            A multiplier on the phase amount.
    """
    # TODO: Avoid overhead from many controls.
    n = len(target_reg)
    for i in range(n):
        p = factor / (1 << (n - i - 1))
        if p % 2 == 0:
            continue
        Z**p & controls | target_reg[i]


all_defined_decomposition_rules = [
    # A gradient is just a chain of partial Z gates.
    DecompositionRule(
        gate_class=PhaseGradientGate,
        gate_recognizer=max_controls(2),
        gate_decomposer=lambda cmd: do_phase_gradient(
            target_reg=cmd.qubits[0],
            controls=cmd.control_qubits,
            factor=cmd.gate.exponent)),
]
