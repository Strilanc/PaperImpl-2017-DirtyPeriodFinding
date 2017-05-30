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
