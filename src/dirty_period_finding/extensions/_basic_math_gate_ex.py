# -*- coding: utf-8 -*-

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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
