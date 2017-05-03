# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dirty_period_finding.extensions import SelfInverseGateEx


class ReverseBitsGate(SelfInverseGateEx):
    def __repr__(self):
        return "ReverseBits"

    def __str__(self):
        return "Reverse"


ReverseBits = ReverseBitsGate()
