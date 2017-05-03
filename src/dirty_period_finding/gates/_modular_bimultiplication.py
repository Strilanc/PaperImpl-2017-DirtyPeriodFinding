# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dirty_period_finding.extensions import BasicMathGateEx


class ModularBimultiplicationGate(BasicMathGateEx):
    def __init__(self, factor, modulus):
        inverse_factor = multiplicative_inverse(factor, modulus)
        if inverse_factor is None:
            raise ValueError("Irreversible.")

        BasicMathGateEx.__init__(self)
        self.factor = factor
        self.inverse_factor = inverse_factor
        self.modulus = modulus

    def do_operation(self, x, y):
        if x >= self.modulus or y >= self.modulus:
            return x, y
        return ((x * self.factor) % self.modulus,
                (y * -self.inverse_factor) % self.modulus)

    def get_inverse(self):
        return ModularBimultiplicationGate(
            self.inverse_factor,
            self.modulus)

    def __repr__(self):
        return 'ModularBimultiplicationGate({}, modulus={})'.format(
            self.factor, self.modulus)

    def __str__(self):
        return repr(self)

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
    g, x, y = extended_gcd(a, m)
    return None if g != 1 else x % m
