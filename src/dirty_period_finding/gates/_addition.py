# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dirty_period_finding.extensions import BasicMathGateEx


class AdditionGate(BasicMathGateEx):
    def do_operation(self, x, y):
        return x, y + x

    def get_inverse(self):
        return SubtractionGate()

    def __repr__(self):
        return 'Add'

    def __str__(self):
        return 'Add'

    def __eq__(self, other):
        return isinstance(other, AdditionGate)

    def __hash__(self):
        return hash(AdditionGate)

    def ascii_register_labels(self):
        return ['A', '+A']


class SubtractionGate(BasicMathGateEx):
    def do_operation(self, x, y):
        return x, y - x

    def get_inverse(self):
        return AdditionGate()

    def __repr__(self):
        return 'Subtract'

    def __str__(self):
        return 'Subtract'

    def __eq__(self, other):
        return isinstance(other, SubtractionGate)

    def __hash__(self):
        return hash(SubtractionGate)

    def ascii_register_labels(self):
        return ['A', '−A']


Add = AdditionGate()
Subtract = SubtractionGate()
