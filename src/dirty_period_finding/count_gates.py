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

"""Prints gate counts for various sizes of the controlled bimultiply gate."""

from __future__ import print_function
from __future__ import unicode_literals

import fractions
import random

from projectq import MainEngine
from projectq.backends import ResourceCounter
from projectq.cengines import DecompositionRuleSet, DummyEngine

import dirty_period_finding.decompositions as decompositions
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import ModularBimultiplicationGate


def main():
    x = 2
    modulus = 2

    for reg_size in range(2, 20):
        reg_max_val = 1 << reg_size
        while True:
            modulus = random.randint(reg_max_val // 2 + 1, reg_max_val - 1)
            x = random.randint(2, modulus - 1)
            if modulus % 2 != 0 and fractions.gcd(x, modulus) == 1:
                break
        cnt = ResourceCounter()
        eng = MainEngine(backend=DummyEngine(), engine_list=[
            AutoReplacerEx(DecompositionRuleSet(modules=[decompositions])),
            LimitedCapabilityEngine(
                allow_toffoli=True,
                allow_single_qubit_gates=True,
                allow_classes=[]
            ),
            cnt,
        ])
        v1 = eng.allocate_qureg(reg_size)
        v2 = eng.allocate_qureg(reg_size)
        c = eng.allocate_qubit()
        gate = ModularBimultiplicationGate(x, modulus)
        gate & c | (v1, v2)
        print()
        print()
        print("Register Size: {}".format(reg_size))
        print("Gate count for controlled {}".format(gate))
        print("\t{}".format(cnt).replace('\n', '\n\t'))


if __name__ == "__main__":
    main()
