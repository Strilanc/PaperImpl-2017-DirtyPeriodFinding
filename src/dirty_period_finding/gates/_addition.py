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
