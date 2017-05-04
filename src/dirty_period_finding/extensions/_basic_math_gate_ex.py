# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import projectq.ops
from projectq.ops import BasicMathGate
from ._basic_gate_ex import BasicGateEx


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


class BasicSizedMathGateEx(BasicMathGate, BasicGateEx):
    def __init__(self):
        def do_not_call(*_):
            raise AssertionError()
        BasicGateEx.__init__(self)
        BasicMathGate.__init__(self, do_not_call)

    def do_operation(self, sizes, args):
        raise NotImplementedError()

    def get_math_function(self, qubits):
        sizes = [len(q) for q in qubits]
        return lambda x: self.do_operation(sizes, x)


class SwapGate(projectq.ops.SwapGate, BasicMathGateEx):
    def do_operation(self, a, b):
        return b, a

    def __eq__(self, other):
        return isinstance(other, SwapGate)

    def __hash__(self):
        return hash(SwapGate)

Swap = SwapGate()
