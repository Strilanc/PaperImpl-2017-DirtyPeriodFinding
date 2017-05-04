# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math
from fractions import Fraction

from projectq import MainEngine
from projectq.backends import Simulator, ResourceCounter
from projectq.cengines import DecompositionRuleSet
from projectq.ops import Measure
from projectq.setups.decompositions import swap2cnot
from projectq.types import Qureg

from dirty_period_finding.decompositions import *
from dirty_period_finding.extensions import (
    H,
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import *


def measure_qureg(qureg):
    if len(qureg) == 0:
        return 0
    Measure | qureg
    qureg[0].engine.flush()
    return sum(1 << i if bool(qureg[i]) else 0 for i in range(len(qureg)))


def sample_period(eng,
                  factor,
                  modulus,
                  precision,
                  phase_qubit,
                  work_qureg,
                  ancilla_qureg):
    """
    Args:
        eng (projectq.cengines.MainEngine):
        factor (int):
        modulus (int):
        precision (int):
            The number of iterations.
        phase_qubit (Qubit):
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
        op = ModularBimultiplicationGate(pow(factor, 1 << rev_i, modulus),
                                         modulus)

        H | phase_qubit
        op & phase_qubit | (work_qureg, ancilla_qureg)
        Z**frac | phase_qubit
        H | phase_qubit

        Measure | phase_qubit
        eng.flush()
        b = bool(phase_qubit)
        if b:
            X | phase_qubit
            frac += Fraction(1, 2 << i)
        print("done iter", i, b, frac)

    # Fix work register.
    Measure | work_qureg
    eng.flush()
    total_factor = measure_qureg(work_qureg)
    fixup_gate = ModularBimultiplicationGate(total_factor * -(-1)**precision,
                                             modulus).get_inverse()
    fixup_gate | (ancilla_qureg, work_qureg)

    # Estimate period based on denominator of closest fraction.
    return frac.limit_denominator(modulus - 1).denominator


def main():
    sim = Simulator()
    ctr = ResourceCounter()
    eng = MainEngine(backend=sim, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[
            addition_rules,
            increment_rules,
            modular_addition_rules,
            modular_bimultiplication_rules,
            modular_double_rules,
            modular_scaled_addition_rules,
            multi_not_rules,
            offset_rules,
            pivot_flip_rules,
            reverse_bits_rules,
            rotate_bits_rules,
            swap2cnot
        ])),
        LimitedCapabilityEngine(
            allow_toffoli=True,
            allow_single_qubit_gates=True,
        ),
        ctr
    ])

    m = 7 * 11
    n = int(math.ceil(math.log(m, 2)))
    sample_period(eng,
                  factor=3,
                  modulus=m,
                  precision=1,
                  phase_qubit=eng.allocate_qubit(),
                  work_qureg=eng.allocate_qureg(n),
                  ancilla_qureg=eng.allocate_qureg(n))
    print('{}'.format(ctr))


if __name__ == "__main__":
    main()
