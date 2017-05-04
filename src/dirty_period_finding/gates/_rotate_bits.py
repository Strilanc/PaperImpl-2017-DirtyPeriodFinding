# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dirty_period_finding.extensions import BasicSizedMathGateEx


class RotateBitsGate(BasicSizedMathGateEx):
    def __init__(self, amount):
        BasicSizedMathGateEx.__init__(self)
        self.amount = amount

    def do_operation(self, sizes, args):
        assert len(sizes) == 1
        assert len(args) == 1
        n = sizes[0]
        v = args[0]
        if n == 0:
            return v
        r = self.amount % n
        m = ~0 << (n - r)
        high, low = v & m, v & ~m
        return (low << r) | (high >> (n - r)),

    def __repr__(self):
        return "RotateBitsGate({})".format(repr(self.amount))

    def __str__(self):
        if self.amount < 0:
            return ">>>" + str(-self.amount)
        return "<<<" + str(self.amount)

    def __eq__(self, other):
        return (isinstance(other, RotateBitsGate) and
                self.amount == other.amount)

    def __hash__(self):
        return hash((RotateBitsGate, self.amount))

    def __pow__(self, power):
        return RotateBitsGate(self.amount * power)

    def get_inverse(self):
        return RotateBitsGate(-self.amount)

LeftRotateBits = RotateBitsGate(1)
RightRotateBits = RotateBitsGate(-1)
