# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dirty_period_finding.extensions import BasicMathGateEx


class IncrementGate(BasicMathGateEx):
    def do_operation(self, x):
        return x + 1,

    def get_inverse(self):
        return DecrementGate()

    def __repr__(self):
        return "Increment"

    def __str__(self):
        return "Increment"

    def __eq__(self, other):
        return isinstance(other, IncrementGate)

    def __hash__(self):
        return hash(IncrementGate)

    def ascii_register_labels(self):
        return ['+1']


class DecrementGate(BasicMathGateEx):
    def do_operation(self, x):
        return x - 1,

    def get_inverse(self):
        return IncrementGate()

    def __repr__(self):
        return "Decrement"

    def __str__(self):
        return "Decrement"

    def __eq__(self, other):
        return isinstance(other, DecrementGate)

    def __hash__(self):
        return hash(DecrementGate)

    def ascii_register_labels(self):
        return ['−1']


Increment = IncrementGate()
Decrement = DecrementGate()
