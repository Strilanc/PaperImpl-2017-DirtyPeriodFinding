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

from projectq.ops import NotMergeable

from dirty_period_finding.extensions import BasicMathGateEx


class OffsetGate(BasicMathGateEx):
    def __init__(self, offset):
        BasicMathGateEx.__init__(self)
        self.offset = offset

    def do_operation(self, x):
        return x + self.offset,

    def get_inverse(self):
        return OffsetGate(-self.offset)

    def get_merged(self, other):
        if not isinstance(other, OffsetGate):
            raise NotMergeable()
        return OffsetGate(self.offset + other.offset)

    def __repr__(self):
        return 'OffsetGate({})'.format(self.offset)

    def __str__(self):
        return '{}{}'.format('+' if self.offset >= 0 else '', self.offset)

    def __eq__(self, other):
        return (isinstance(other, OffsetGate) and
                self.offset == other.offset)

    def __hash__(self):
        return hash((OffsetGate, self.offset))
