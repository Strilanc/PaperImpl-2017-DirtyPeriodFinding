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

from dirty_period_finding.extensions import BasicMathGateEx


class ModularAdditionGate(BasicMathGateEx):
    def __init__(self, modulus):
        BasicMathGateEx.__init__(self)
        self.modulus = modulus

    def do_operation(self, x, y):
        if x >= self.modulus or y >= self.modulus:
            return x, y
        return x, (y + x) % self.modulus

    def get_inverse(self):
        return ModularSubtractionGate(self.modulus)

    def __eq__(self, other):
        return (isinstance(other, ModularAdditionGate) and
                self.modulus == other.modulus)

    def __hash__(self):
        return hash((ModularAdditionGate, self.modulus))

    def __repr__(self):
        return 'ModularAdditionGate(modulus={})'.format(self.modulus)

    def __str__(self):
        return repr(self)

    def ascii_register_labels(self):
        return ['A', '+A % {}'.format(self.modulus)]


class ModularSubtractionGate(BasicMathGateEx):
    def __init__(self, modulus):
        BasicMathGateEx.__init__(self)
        self.modulus = modulus

    def do_operation(self, x, y):
        if x >= self.modulus or y >= self.modulus:
            return x, y
        return x, (y - x) % self.modulus

    def get_inverse(self):
        return ModularAdditionGate(self.modulus)

    def __eq__(self, other):
        return (isinstance(other, ModularSubtractionGate) and
                self.modulus == other.modulus)

    def __hash__(self):
        return hash((ModularSubtractionGate, self.modulus))

    def __repr__(self):
        return 'ModularSubtractionGate(modulus={})'.format(self.modulus)

    def __str__(self):
        return repr(self)

    def ascii_register_labels(self):
        return ['A', '−A % {}'.format(self.modulus)]


class ModularOffsetGate(BasicMathGateEx):
    def __init__(self, offset, modulus):
        BasicMathGateEx.__init__(self)
        self.offset = offset % modulus
        self.modulus = modulus

    def do_operation(self, x):
        if x >= self.modulus:
            return x,
        return (x + self.offset) % self.modulus,

    def get_inverse(self):
        return ModularOffsetGate(-self.offset, self.modulus)

    def __repr__(self):
        return 'ModularOffsetGate({}, modulus={})'.format(self.offset,
                                                          self.modulus)

    def __str__(self):
        return '+{} % {}'.format(self.offset, self.modulus)

    def __eq__(self, other):
        return (isinstance(other, ModularOffsetGate) and
                self.modulus == other.modulus and
                self.offset == other.offset)

    def __hash__(self):
        return hash((ModularAdditionGate, self.modulus, self.offset))
