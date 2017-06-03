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

from dirty_period_finding.extensions import BasicSizedMathGateEx


class ScaledAdditionGate(BasicSizedMathGateEx):
    def __init__(self, factor):
        BasicSizedMathGateEx.__init__(self)
        self.factor = factor

    def do_operation(self, sizes, args):
        inp, out = args
        mask = ~(~0 << sizes[1])
        return inp, (out + inp * self.factor) & mask

    def get_inverse(self):
        return ScaledAdditionGate(-self.factor)

    def get_merged(self, other):
        if not isinstance(other, ScaledAdditionGate):
            raise NotMergeable()
        return ScaledAdditionGate(self.factor * other.factor)

    def __repr__(self):
        return 'ScaledAdditionGate({})'.format(self.factor)

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        return (isinstance(other, ScaledAdditionGate) and
                self.factor == other.factor)

    def __hash__(self):
        return hash((ScaledAdditionGate, self.factor))

    def sanity_check(self, registers):
        assert len(registers) == 2

    def ascii_register_labels(self):
        return ['A', '+A·{}'.format(self.factor)]
