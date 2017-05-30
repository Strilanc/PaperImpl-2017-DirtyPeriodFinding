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

from ._modular_bimultiplication import multiplicative_inverse
from dirty_period_finding.extensions import BasicMathGateEx


class ModularDoubleGate(BasicMathGateEx):
    def __init__(self, modulus):
        if modulus % 2 == 0:
            raise ValueError(
                'Doubling is irreversible modulo {}.'.format(modulus))
        BasicMathGateEx.__init__(self)
        self.modulus = modulus

    def do_operation(self, x):
        if x >= self.modulus:
            return x,
        return x * 2 % self.modulus,

    def get_inverse(self):
        return ModularUndoubleGate(self.modulus)

    def __repr__(self):
        return 'ModularDoubleGate({})'.format(repr(self.modulus))

    def __str__(self):
        return '×2 % {}'.format(self.modulus)

    def __eq__(self, other):
        return (isinstance(other, ModularDoubleGate) and
                self.modulus == other.modulus)

    def __hash__(self):
        return hash((ModularDoubleGate, self.modulus))


class ModularUndoubleGate(BasicMathGateEx):
    def __init__(self, modulus):
        if modulus % 2 == 0:
            raise ValueError("Undoubling is irreversible modulo even values.")
        BasicMathGateEx.__init__(self)
        self.modulus = modulus

    def do_operation(self, x):
        if x >= self.modulus:
            return x,
        return x * multiplicative_inverse(2, self.modulus) % self.modulus,

    def get_inverse(self):
        return ModularDoubleGate(self.modulus)

    def __repr__(self):
        return 'ModularUndoubleGate({})'.format(repr(self.modulus))

    def __str__(self):
        return '÷2 % {}'.format(self.modulus)

    def __eq__(self, other):
        return (isinstance(other, ModularUndoubleGate) and
                self.modulus == other.modulus)

    def __hash__(self):
        return hash((ModularUndoubleGate, self.modulus))
