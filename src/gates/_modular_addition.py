# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..extensions import BasicMathGateEx


class ModularAdditionGate(BasicMathGateEx):
    def __init__(self, modulus):
        BasicMathGateEx.__init__(self)
        self.modulus = modulus

    def do_operation(self, x, y):
        if x >= self.modulus or y >= self.modulus:
            return x, y
        return x, (y + x) % self.modulus

    def get_inverse(self):
        return ModularSubtractionGate(self.modulus)

    def __repr__(self):
        return 'ModularAdditionGate(modulus={})'.format(self.modulus)

    def __str__(self):
        return repr(self)

    def ascii_register_labels(self):
        return ['A', '+A % {}'.format(self.modulus)]


class ModularSubtractionGate(BasicMathGateEx):
    def __init__(self, modulus):
        BasicMathGateEx.__init__(self)
        self.modulus = modulus

    def do_operation(self, x, y):
        if x >= self.modulus or y >= self.modulus:
            return x, y
        return x, (y - x) % self.modulus

    def get_inverse(self):
        return ModularAdditionGate(self.modulus)

    def __repr__(self):
        return 'ModularSubtractionGate(modulus={})'.format(self.modulus)

    def __str__(self):
        return repr(self)

    def ascii_register_labels(self):
        return ['A', '−A % {}'.format(self.modulus)]


class ModularOffsetGate(BasicMathGateEx):
    def __init__(self, offset, modulus):
        BasicMathGateEx.__init__(self)
        self.offset = offset % modulus
        self.modulus = modulus

    def do_operation(self, x):
        if x >= self.modulus:
            return x,
        return (x + self.offset) % self.modulus,

    def get_inverse(self):
        return ModularOffsetGate(-self.offset, self.modulus)

    def __repr__(self):
        return 'ModularOffsetGate({}, modulus={})'.format(self.offset,
                                                          self.modulus)

    def __str__(self):
        return '+{} % {}'.format(self.offset, self.modulus)
