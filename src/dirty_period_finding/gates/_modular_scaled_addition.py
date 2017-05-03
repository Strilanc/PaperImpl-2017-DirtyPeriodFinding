# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dirty_period_finding.extensions import BasicMathGateEx


class ModularScaledAdditionGate(BasicMathGateEx):
    def __init__(self, factor, modulus):
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

    def __repr__(self):
        return 'ModularScaledAdditionGate({}, modulus={})'.format(
            self.factor, self.modulus)

    def __str__(self):
        return repr(self)

    def ascii_register_labels(self):
        return ['A', '+A·{} (mod {})'.format(self.factor, self.modulus)]


def _extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, y, x = _extended_gcd(b % a, a)
    return g, x - (b // a) * y, y


def _multiplicative_inverse(a, m):
    g, x, y = _extended_gcd(a, m)
    return None if g != 1 else x % m
