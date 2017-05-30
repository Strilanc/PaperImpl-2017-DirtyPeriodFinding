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

from dirty_period_finding.extensions import (
    SelfInverseGateEx,
    BasicSizedMathGateEx,
)


class ReverseBitsGate(BasicSizedMathGateEx, SelfInverseGateEx):
    def do_operation(self, sizes, args):
        assert len(sizes) == 1
        assert len(args) == 1
        n = sizes[0]
        v = args[0]
        return sum(((v >> i) & 1) << (n - i - 1) for i in range(n)),

    def __repr__(self):
        return "ReverseBits"

    def __str__(self):
        return "Reverse"

    def __eq__(self, other):
        return isinstance(other, ReverseBitsGate)

    def __hash__(self):
        return hash(ReverseBitsGate)


ReverseBits = ReverseBitsGate()
