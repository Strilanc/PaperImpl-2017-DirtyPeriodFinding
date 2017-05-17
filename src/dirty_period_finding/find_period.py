# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import math
import random
from fractions import Fraction

from projectq import MainEngine
from projectq.backends import Simulator
from projectq.cengines import DecompositionRuleSet
from projectq.ops import X, Z
from projectq.setups.decompositions import swap2cnot
from projectq.types import Qureg

from dirty_period_finding.decompositions import *
from dirty_period_finding.extensions import (
    H,
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import *


def sample_period(base,
                  modulus,
                  precision,
                  phase_qubit,
                  work_qureg,
                  ancilla_qureg):
    """
    Args:
        base (int):
        modulus (int):
        precision (int):
            The number of iterations.
        phase_qubit (Qureg):
            A clean zero-initialized qubit.
        work_qureg (Qureg):
            A clean zero-initialized register with lg(modulus) bits.
        ancilla_qureg (Qureg): A semi-dirty register.
            A mostly-dirty register with lg(modulus) bits.
            Only the most significant bit must be clean and zero-initialised.

    Returns:
        int:
            A number related to the period.
    """

    # Incremental phase estimation.
    X | work_qureg[0]
    frac = Fraction(0, 1)
    for i in range(precision):
        rev_i = precision - i - 1
        op = ModularBimultiplicationGate(pow(base, 1 << rev_i, modulus),
                                         modulus)

        H | phase_qubit
        op & phase_qubit | (work_qureg, ancilla_qureg)
        Z**frac | phase_qubit
        H | phase_qubit

        b = phase_qubit.measure()
        if b:
            X | phase_qubit
            frac += Fraction(1, 2 << i)
        print("done iter",
              i,
              b,
              frac,
              frac.limit_denominator(modulus - 1).denominator)

    # Fix ancilla register using factor in work register.
    fixup_factor = work_qureg.measure()
    fixup_gate = ModularBimultiplicationGate(fixup_factor, modulus)
    fixup_gate | (ancilla_qureg, work_qureg)

    # Estimate period based on denominator of closest fraction.
    return frac.limit_denominator(modulus - 1).denominator


def main():
    sim = Simulator()
    eng = MainEngine(backend=sim, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            addition_rules,
            increment_rules,
            modular_addition_rules,
            modular_bimultiplication_rules,
            modular_double_rules,
            modular_negate_rules,
            modular_scaled_addition_rules,
            multi_not_rules,
            offset_rules,
            pivot_flip_rules,
            reverse_bits_rules,
            rotate_bits_rules,
            swap2cnot,
            comparison_rules,
        ])),
        LimitedCapabilityEngine(
            allow_toffoli=True,
            allow_single_qubit_gates=True,
            allow_classes=[]
        ),
    ])

    modulus = 11 * 5
    n = int(math.ceil(math.log(modulus, 2)))
    base = 6

    ancilla_qureg = eng.allocate_qureg(n)
    for q in ancilla_qureg[:-1]:
        if random.random() < 0.5:
            X | q
    before = ancilla_qureg.measure()

    p = sample_period(base=base,
                      modulus=modulus,
                      precision=n * 2,
                      phase_qubit=eng.allocate_qubit(),
                      work_qureg=eng.allocate_qureg(n),
                      ancilla_qureg=ancilla_qureg)

    after = ancilla_qureg.measure()
    print("before", before, "after", after)
    u = pow(base, p, modulus)
    print("result", p, "u", u if u < modulus / 2 else '-' + str(-u % modulus))

    assert before == after
    print(u == 1 or u == -1 % modulus)


if __name__ == "__main__":
    main()
