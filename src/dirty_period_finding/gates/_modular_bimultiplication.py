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


class ModularBimultiplicationGate(BasicMathGateEx):
    def __init__(self, factor, modulus):
        inverse_factor = multiplicative_inverse(factor, modulus)
        if inverse_factor is None:
            raise ValueError("Irreversible: *{} % {}.".format(factor, modulus))

        BasicMathGateEx.__init__(self)
        self.factor = factor
        self.inverse_factor = inverse_factor
        self.modulus = modulus

    def do_operation(self, x, y):
        if x >= self.modulus or y >= self.modulus:
            return x, y
        return ((x * self.factor) % self.modulus,
                (y * self.inverse_factor) % self.modulus)

    def get_inverse(self):
        return ModularBimultiplicationGate(
            self.inverse_factor,
            self.modulus)

    def get_merged(self, other):
        if (not isinstance(other, ModularBimultiplicationGate) or
                other.modulus != self.modulus):
            raise NotMergeable()
        return ModularBimultiplicationGate(self.factor * other.factor,
                                           self.modulus)

    def __repr__(self):
        return 'ModularBimultiplicationGate({}, modulus={})'.format(
            self.factor, self.modulus)

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        return (isinstance(other, ModularBimultiplicationGate) and
                self.factor == other.factor and
                self.modulus == other.modulus)

    def __hash__(self):
        return hash((ModularBimultiplicationGate, self.factor, self.modulus))

    def ascii_register_labels(self):
        return [
            '×{} (mod {})'.format(self.factor, self.modulus),
            '×{} (mod {})'.format(self.inverse_factor, self.modulus)
        ]


def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, y, x = extended_gcd(b % a, a)
    return g, x - (b // a) * y, y


def multiplicative_inverse(a, m):
    a %= m
    g, x, y = extended_gcd(a, m)
    return None if g != 1 else x % m
