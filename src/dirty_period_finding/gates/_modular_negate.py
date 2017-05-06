# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dirty_period_finding.extensions import BasicMathGateEx, SelfInverseGateEx


class ModularNegate(BasicMathGateEx, SelfInverseGateEx):
    def __init__(self, modulus):
        BasicMathGateEx.__init__(self)
        SelfInverseGateEx.__init__(self)
        self.modulus = modulus

    def do_operation(self, x):
        if x >= self.modulus:
            return x,
        return -x % self.modulus,

    def __repr__(self):
        return 'ModularNegate(modulus={})'.format(
            self.factor, self.modulus)

    def __str__(self):
        return '×-1 % {}'.format(self.modulus)

    def __eq__(self, other):
        return (isinstance(other, ModularNegate) and
                self.modulus == other.modulus)

    def __hash__(self):
        return hash((ModularNegate, self.modulus))
