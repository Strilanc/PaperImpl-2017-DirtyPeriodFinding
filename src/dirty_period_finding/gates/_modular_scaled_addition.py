# -*- coding: utf-8 -*-

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import unicode_literals

from projectq.ops import NotMergeable

from dirty_period_finding.extensions import BasicMathGateEx


class ModularScaledAdditionGate(BasicMathGateEx):
    def __init__(self, factor, modulus):
        if modulus <= 0:
            raise ValueError("non-positive modulus: {}".format(modulus))
        if modulus % 2 == 0:
            raise NotImplementedError("even modulus: {}".format(modulus))
        BasicMathGateEx.__init__(self)
        self.factor = factor % modulus
        self.modulus = modulus

    def do_operation(self, x, y):
        if x >= self.modulus or y >= self.modulus:
            return x, y
        return x, (y + x * self.factor) % self.modulus

    def get_inverse(self):
        return ModularScaledAdditionGate(
            -self.factor % self.modulus,
            self.modulus)

    def get_merged(self, other):
        if (not isinstance(other, ModularScaledAdditionGate) or
                other.modulus != self.modulus):
            raise NotMergeable()
        return ModularScaledAdditionGate(self.factor * other.factor,
                                         self.modulus)

    def __repr__(self):
        return 'ModularScaledAdditionGate({}, modulus={})'.format(
            self.factor, self.modulus)

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        return (isinstance(other, ModularScaledAdditionGate) and
                self.factor == other.factor and
                self.modulus == other.modulus)

    def __hash__(self):
        return hash((ModularScaledAdditionGate, self.modulus, self.factor))

    def sanity_check(self, registers):
        assert len(registers) == 2
        assert len(registers[0]) == len(registers[1])
        assert 1 << len(registers[0]) >= self.modulus

    def ascii_register_labels(self):
        return ['A', '+A·{} % {}'.format(self.factor, self.modulus)]


def _extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, y, x = _extended_gcd(b % a, a)
    return g, x - (b // a) * y, y


def _multiplicative_inverse(a, m):
    g, x, y = _extended_gcd(a, m)
    return None if g != 1 else x % m
