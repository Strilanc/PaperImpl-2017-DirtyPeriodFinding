# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dirty_period_finding.extensions import (
    SelfInverseGateEx,
    BasicSizedMathGateEx,
)


class ReverseBitsGate(BasicSizedMathGateEx, SelfInverseGateEx):
    def do_operation(self, sizes, args):
        assert len(sizes) == 1
        assert len(args) == 1
        n = sizes[0]
        v = args[0]
        return sum(((v >> i) & 1) << (n - i - 1) for i in range(n)),

    def __repr__(self):
        return "ReverseBits"

    def __str__(self):
        return "Reverse"

    def __eq__(self, other):
        return isinstance(other, ReverseBitsGate)

    def __hash__(self):
        return hash(ReverseBitsGate)


ReverseBits = ReverseBitsGate()
