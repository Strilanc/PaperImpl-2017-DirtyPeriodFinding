# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.ops import BasicMathGate
from .basic_gate_ex import BasicGateEx


class BasicMathGateEx(BasicMathGate, BasicGateEx):
    def __init__(self):
        def do_not_call(*_):
            raise AssertionError()
        BasicGateEx.__init__(self)
        BasicMathGate.__init__(self, do_not_call)

    def do_operation(self, *args):
        raise NotImplementedError()

    def get_math_function(self, qubits):
        return lambda x: self.do_operation(*x)
