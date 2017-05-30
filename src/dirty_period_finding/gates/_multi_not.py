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

from projectq.ops import SelfInverseGate
from dirty_period_finding.extensions import BasicMathGateEx


class MultiNotGate(BasicMathGateEx, SelfInverseGate):
    def do_operation(self, x):
        return ~x,

    def __repr__(self):
        return "MultiNot"

    def __str__(self):
        return "MultiNot"

    def __eq__(self, other):
        return isinstance(other, MultiNotGate)

    def __hash__(self):
        return hash(MultiNotGate)

    def ascii_register_labels(self):
        return ['⊕']

    def ascii_borders(self):
        return False

MultiNot = MultiNotGate()
