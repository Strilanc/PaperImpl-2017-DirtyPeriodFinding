# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dirty_period_finding.extensions import BasicMathGateEx


class OffsetGate(BasicMathGateEx):
    def __init__(self, offset):
        BasicMathGateEx.__init__(self)
        self.offset = offset

    def do_operation(self, x):
        return x + self.offset,

    def get_inverse(self):
        return OffsetGate(-self.offset)

    def __repr__(self):
        return 'OffsetGate({})'.format(self.offset)

    def __str__(self):
        return '{}{}'.format('+' if self.offset >= 0 else '', self.offset)
