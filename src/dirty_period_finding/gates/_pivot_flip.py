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

from dirty_period_finding.extensions import BasicMathGateEx, SelfInverseGateEx


class PivotFlipGate(BasicMathGateEx, SelfInverseGateEx):
    def __init__(self):
        SelfInverseGateEx.__init__(self)
        BasicMathGateEx.__init__(self)

    def do_operation(self, pivot, x):
        if x >= pivot:
            return pivot, x
        return pivot, pivot - x - 1

    def __eq__(self, other):
        return isinstance(other, PivotFlipGate)

    def __hash__(self):
        return hash(PivotFlipGate)

    def __repr__(self):
        return 'PivotFlip'

    def __str__(self):
        return 'Flip<A'

    def ascii_register_labels(self):
        return ['A', 'Flip<A']


class ConstPivotFlipGate(BasicMathGateEx, SelfInverseGateEx):
    def __init__(self, pivot):
        SelfInverseGateEx.__init__(self)
        BasicMathGateEx.__init__(self)
        self.pivot = pivot

    def do_operation(self, x):
        if x >= self.pivot:
            return x,
        return self.pivot - x - 1,

    def __eq__(self, other):
        return (isinstance(other, ConstPivotFlipGate) and
                self.pivot == other.pivot)

    def __hash__(self):
        return hash((ConstPivotFlipGate, self.pivot))

    def __repr__(self):
        return 'ConstPivotFlipGate({})'.format(self.pivot)

    def __str__(self):
        return 'Flip<{}'.format(self.pivot)


PivotFlip = PivotFlipGate()
