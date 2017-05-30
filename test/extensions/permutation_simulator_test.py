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

from projectq import MainEngine
from projectq.ops import BasicMathGate, X

from dirty_period_finding.extensions import PermutationSimulator


def test_simulator_triangle_increment():
    sim = PermutationSimulator()
    eng = MainEngine(sim, [])
    a = eng.allocate_qureg(5)

    assert sim.permutation_equals([a], lambda ns, es: es)

    for i in range(5)[::-1]:
        X & a[:i] | a[i]

    assert not sim.permutation_equals([a], lambda ns, es: es)
    assert sim.permutation_equals([a], lambda ns, es: ((es[0] + 1) & 0b11111,))

    for i in range(5)[::-1]:
        X & a[:i] | a[i]

    assert not sim.permutation_equals([a], lambda ns, es: es)
    assert sim.permutation_equals([a], lambda ns, es: ((es[0] + 2) & 0b11111,))


def test_simulator_arithmetic():
    class Offset(BasicMathGate):
        def __init__(self, amount):
            BasicMathGate.__init__(self, lambda x: (x+amount,))

    class Sub(BasicMathGate):
        def __init__(self):
            BasicMathGate.__init__(self, lambda x, y: (x, y-x))

    sim = PermutationSimulator()
    eng = MainEngine(sim, [])
    a = eng.allocate_qureg(3)
    b = eng.allocate_qureg(4)

    Offset(2) | a
    assert sim.permutation_equals([a, b],
                                  lambda ns, xs: ((xs[0] + 2) & 0b111,
                                                   xs[1] & 0b1111))
    assert not sim.permutation_equals([a, b],
                                      lambda ns, xs: ((xs[0] - 2) & 0b111,
                                                       xs[1] & 0b1111))

    Offset(3) | b
    assert sim.permutation_equals([a, b],
                                  lambda ns, xs: ((xs[0] + 2) & 0b111,
                                                  (xs[1] + 3) & 0b1111))

    Offset(32 + 5) | b
    assert sim.permutation_equals([a, b],
                                  lambda ns, xs: ((xs[0] + 2) & 0b111,
                                                  (xs[1] + 8) & 0b1111))

    Sub() | (a, b)
    assert sim.permutation_equals(
        [a, b],
        lambda ns, xs: ((xs[0] + 2) & 0b111,
                        (xs[1] + 8 - ((xs[0]+2) & 0b111)) & 0b1111))

    Sub() | (a, b)
    Sub() | (a, b)
    assert sim.permutation_equals(
        [a, b],
        lambda ns, xs: ((xs[0] + 2) & 0b111,
                        (xs[1] + 8 - 3*((xs[0] + 2) & 0b111)) & 0b1111))
