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

from fractions import Fraction

from projectq.ops import NotMergeable

from dirty_period_finding.extensions import BasicGateEx


class PhaseGradientGate(BasicGateEx):
    def __init__(self, exponent):
        BasicGateEx.__init__(self)
        self.exponent = exponent

    def phase_angle_in_turns_for(self, register_value, register_size):
        return Fraction(register_value, 1 << register_size) * self.exponent

    def get_inverse(self):
        return PhaseGradientGate(-self.exponent)

    def get_merged(self, other):
        if (not isinstance(other, PhaseGradientGate) or
                other.exponent != self.exponent):
            raise NotMergeable()
        return PhaseGradientGate(self.exponent + other.exponent)

    def __repr__(self):
        if self.exponent == 1: return "PhaseGradient"
        return "PhaseGradient**({})".format(repr(self.exponent))

    def __str__(self):
        if self.exponent == 1: return "PhaseGradient"
        return "PhaseGradient**" + str(self.exponent)

    def __eq__(self, other):
        return (isinstance(other, PhaseGradientGate) and
                self.exponent == other.exponent)

    def __hash__(self):
        return hash((PhaseGradientGate, self.exponent))

    def __pow__(self, power):
        """
        Args:
            power (int|float|fractions.Fraction):
        Returns:
            PhaseGradientGate:
        """
        return PhaseGradientGate(self.exponent * power)

    def ascii_register_labels(self):
        if self.exponent == 1:
            return ['Grad']
        return ['Grad^' + str(self.exponent)]

PhaseGradient = PhaseGradientGate(1)
