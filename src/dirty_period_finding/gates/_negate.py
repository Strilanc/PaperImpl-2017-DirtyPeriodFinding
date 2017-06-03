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
    SelfInverseGateEx,
    BasicSizedMathGateEx,
)


class NegateGate(SelfInverseGateEx, BasicSizedMathGateEx):
    def do_operation(self, sizes, args):
        mask = ~(~0 << sizes[0])
        return -args[0] & mask,

    def get_merged(self, other):
        raise NotMergeable()

    def __repr__(self):
        return 'NegateGate()'

    def __str__(self):
        return 'Negate'

    def __eq__(self, other):
        return isinstance(other, NegateGate)

    def __hash__(self):
        return hash(NegateGate)

    def sanity_check(self, registers):
        assert len(registers) == 1

    def ascii_register_labels(self):
        return ['×-1']


Negate = NegateGate()
