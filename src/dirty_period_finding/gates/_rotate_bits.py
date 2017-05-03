# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dirty_period_finding.extensions import BasicGateEx


class RotateBitsGate(BasicGateEx):
    def __init__(self, amount):
        BasicGateEx.__init__(self)
        self.amount = amount

    def __repr__(self):
        return "RotateBitsGate({})".format(repr(self.amount))

    def __str__(self):
        if self.amount < 0:
            return ">>>" + str(-self.amount)
        return "<<<" + str(self.amount)

    def __pow__(self, power):
        return RotateBitsGate(self.amount * power)

    def get_inverse(self):
        return RotateBitsGate(-self.amount)

LeftRotateBits = RotateBitsGate(1)
RightRotateBits = RotateBitsGate(-1)
