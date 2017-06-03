# -*- coding: utf-8 -*-

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals

from projectq.ops import NotMergeable

from dirty_period_finding.extensions import (
    BasicSizedMathGateEx,
    multiplicative_inverse,
)


class ScaleGate(BasicSizedMathGateEx):
    def __init__(self, factor=1, inverse_factor=1):
        if factor & 1 == 0 or inverse_factor & 1 == 0:
            raise ValueError("Can't reversibly scale by even factors.")
        BasicSizedMathGateEx.__init__(self)
        self.factor = factor
        self.inverse_factor = inverse_factor

    def net_factor_for_size(self, size):
        mask = ~(~0 << size)
        inv = multiplicative_inverse(self.inverse_factor, 1 << size)
        return (self.factor * inv) & mask

    def do_operation(self, sizes, args):
        n = sizes[0]
        mask = ~(~0 << n)
        return (args[0] * self.net_factor_for_size(n)) & mask,

    def get_inverse(self):
        return ScaleGate(self.inverse_factor, self.factor)

    def get_merged(self, other):
        if not isinstance(other, ScaleGate):
            raise NotMergeable()
        return ScaleGate(self.factor * other.factor,
                         self.inverse_factor * other.inverse_factor)

    def __repr__(self):
        return 'ScaleGate({}, {})'.format(self.factor, self.inverse_factor)

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        return (isinstance(other, ScaleGate) and
                self.factor == other.factor and
                self.inverse_factor == other.inverse_factor)

    def __hash__(self):
        return hash((ScaleGate, self.factor, self.inverse_factor))

    def sanity_check(self, registers):
        assert len(registers) == 1

    def ascii_register_labels(self):
        if self.inverse_factor == 1:
            return ['×{}'.format(self.factor)]
        if self.factor == 1:
            return ['×{}⁻¹'.format(self.inverse_factor)]
        return ['×{}·{}⁻¹'.format(self.factor, self.inverse_factor)]
