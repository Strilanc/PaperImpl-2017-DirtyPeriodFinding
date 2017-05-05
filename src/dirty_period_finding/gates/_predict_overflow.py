# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dirty_period_finding.extensions import (
    BasicSizedMathGateEx,
    SelfInverseGateEx,
)


class PredictOffsetOverflowGate(BasicSizedMathGateEx, SelfInverseGateEx):
    def __init__(self, offset):
        if offset < 0:
            raise ValueError('Negative offset')
        BasicSizedMathGateEx.__init__(self)
        SelfInverseGateEx.__init__(self)
        self.offset = offset

    def do_operation(self, sizes, args):
        assert len(sizes) == 2
        assert len(args) == 2
        assert sizes[1] == 1
        v = args[0]
        m = ~0 << sizes[0]
        b = (v + self.offset) & m
        return v, args[1] ^ (1 if b else 0)

    def __eq__(self, other):
        return (isinstance(other, PredictOffsetOverflowGate) and
                self.offset == other.offset)

    def __hash__(self):
        return hash((PredictOffsetOverflowGate, self.offset))

    def __repr__(self):
        return 'PredictOffsetOverflowGate(offset={})'.format(self.offset)

    def __str__(self):
        return repr(self)

    def ascii_register_labels(self):
        return ['A', '⊕overflow(A+={})'.format(self.offset)]

    def sanity_check(self, registers):
        assert len(registers) == 2
        assert len(registers[1]) == 1
        assert self.offset < 1 << len(registers[0])


class LessThanConstantGate(BasicSizedMathGateEx, SelfInverseGateEx):
    def __init__(self, comparand):
        BasicSizedMathGateEx.__init__(self)
        SelfInverseGateEx.__init__(self)
        self.comparand = comparand

    def do_operation(self, sizes, args):
        assert len(sizes) == 2
        assert len(args) == 2
        assert sizes[1] == 1
        return args[0], args[1] ^ (1 if args[0] < self.comparand else 0)

    def __eq__(self, other):
        return (isinstance(other, LessThanConstantGate) and
                self.comparand == other.comparand)

    def __hash__(self):
        return hash((LessThanConstantGate, self.comparand))

    def __repr__(self):
        return 'LessThanConstantGate({})'.format(self.comparand)

    def __str__(self):
        return repr(self)

    def ascii_register_labels(self):
        return ['A', '⊕A<{}'.format(self.comparand)]
