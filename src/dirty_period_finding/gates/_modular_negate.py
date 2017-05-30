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


class ModularNegate(BasicMathGateEx, SelfInverseGateEx):
    def __init__(self, modulus):
        BasicMathGateEx.__init__(self)
        SelfInverseGateEx.__init__(self)
        self.modulus = modulus

    def do_operation(self, x):
        if x >= self.modulus:
            return x,
        return -x % self.modulus,

    def __repr__(self):
        return 'ModularNegate(modulus={})'.format(
            self.factor, self.modulus)

    def __str__(self):
        return '×-1 % {}'.format(self.modulus)

    def __eq__(self, other):
        return (isinstance(other, ModularNegate) and
                self.modulus == other.modulus)

    def __hash__(self):
        return hash((ModularNegate, self.modulus))
