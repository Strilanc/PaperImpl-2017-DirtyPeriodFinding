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

"""Factors a number given as a command-line argument."""

from __future__ import print_function
from __future__ import unicode_literals

import fractions
import math
import random
import sys
from fractions import Fraction

from projectq import MainEngine
from projectq.backends import Simulator
from projectq.cengines import DecompositionRuleSet
from projectq.ops import X, Z
from projectq.types import Qureg

import dirty_period_finding.decompositions as decompositions
from dirty_period_finding.extensions import (
    H,
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import ModularBimultiplicationGate


# The whole point is to break things down into toffoli gates, but simulating
# all of them makes things ridiculously slow. So... it's up to you, reader.
DECOMPOSE_INTO_TOFFOLIS_AND_GO_VERY_VERY_SLOW = False


def shor_find_period(base,
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
        frac /= 2
        if b:
            X | phase_qubit
            frac += Fraction(1, 2)

    # Fix ancilla register using factor in work register.
    fixup_factor = work_qureg.measure()
    fixup_gate = ModularBimultiplicationGate(fixup_factor, modulus)
    fixup_gate | (ancilla_qureg, work_qureg)

    # Estimate period based on denominator of closest fraction.
    return frac.limit_denominator(modulus - 1).denominator


def simulate_sample_period(base, modulus):
    sim = Simulator()
    eng = MainEngine(backend=sim, engine_list=[
        AutoReplacerEx(DecompositionRuleSet(modules=[decompositions])),
        LimitedCapabilityEngine(
            allow_arithmetic=not DECOMPOSE_INTO_TOFFOLIS_AND_GO_VERY_VERY_SLOW,
            allow_toffoli=True,
            allow_single_qubit_gates=True
        ),
    ])

    n = int(math.ceil(math.log(modulus, 2)))

    ancilla_qureg = eng.allocate_qureg(n)
    for q in ancilla_qureg[:-1]:
        if random.random() < 0.5:
            X | q
    before = ancilla_qureg.measure()

    result = shor_find_period(base=base,
                              modulus=modulus,
                              precision=n * 2,
                              phase_qubit=eng.allocate_qubit(),
                              work_qureg=eng.allocate_qureg(n),
                              ancilla_qureg=ancilla_qureg)
    after = ancilla_qureg.measure()
    assert after == before

    return result


def cleanup_period(base, sampled_period, modulus):
    tweaks = [
        lambda x: x // 2,
        lambda x: x,
        lambda x: x + 1,
        lambda x: x - 1,
        lambda x: x * 2,
    ]

    for tweak in tweaks:
        tweaked_period = tweak(sampled_period)
        if pow(base, tweaked_period, modulus) == 1:
            return tweaked_period

    # No good.
    return 0


def period_to_factors(base, modulus, period):
    half_period = period // 2
    x = pow(base, half_period, modulus)
    if x**2 % modulus != 1 or x == 1 or x == -1 % modulus:
        return None

    # (x + 1) * (x - 1) = x^2 - 1^2 = 1 - 1 = 0
    # therefore (x+1)*(x-1) * k = k * modulus
    # but (x+1) and (x-1) can't be multiples of modulus
    # therefore they contain factors

    factors_1 = fractions.gcd(x + 1, modulus)
    factors_2 = fractions.gcd(x - 1, modulus)

    assert factors_1 * factors_2 == modulus
    return sorted([factors_1, factors_2])


def random_base(modulus):
    while True:
        base = random.randint(2, modulus - 2)
        if fractions.gcd(modulus, base) == 1:
            return base


def partial_factorize(n, attempts=10):
    if n % 2 == 0:
        return [n // 2, 2]

    for _ in range(attempts):
        base = random_base(n)

        p_raw = simulate_sample_period(base, n)
        p = cleanup_period(base, p_raw, n)
        factors = period_to_factors(base, n, p)
        if factors is not None:
            return factors

    raise RuntimeError("Failed to factor in {} attempts.".format(attempts))


def main():
    if len(sys.argv) < 2:
        raise ValueError("Give a number to factor as a command line argument.")
    n = int(sys.argv[1])
    if n < 4:
        raise ValueError("Give a positive composite number.")

    factors = partial_factorize(n)
    print(' * '.join(str(e) for e in factors))


if __name__ == "__main__":
    main()
