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

from __future__ import division
from __future__ import unicode_literals

from projectq.cengines import DecompositionRuleSet
from projectq.ops import X
from projectq.setups.decompositions import swap2cnot

from dirty_period_finding.decompositions import (
    bootstrap_ancilla_rules,
    phase_gradient_rules,
    increment_rules,
    multi_not_rules,
    addition_rules
)
from dirty_period_finding.extensions import (
    AutoReplacerEx,
    LimitedCapabilityEngine,
)
from dirty_period_finding.gates import Increment
from .._test_util import check_quantum_permutation_circuit


def test_full_cnot_permutations_small():
    for n in [1, 2, 3, 4, 7, 9]:
        control_mask = ((1 << (n - 1)) - 1) << 1

        check_quantum_permutation_circuit(
            register_size=n,
            permutation_func=lambda ns, (i,):
                i ^ (1 if control_mask & i == control_mask else 0),
            engine_list=[
                AutoReplacerEx(DecompositionRuleSet(modules=[
                    bootstrap_ancilla_rules,
                    phase_gradient_rules,
                    increment_rules,
                    multi_not_rules,
                    addition_rules,
                    swap2cnot,
                ])),
                LimitedCapabilityEngine(
                    allow_toffoli=True,
                    allow_single_qubit_gates=True
                ),
            ],
            actions=lambda eng, regs: X & regs[0][1:] | regs[0][0])


def test_full_increment_permutations_small():
    for n in [1, 2, 3, 4, 7]:
        for c in [0, 1, 2]:
            control_mask = (1 << c) - 1

            check_quantum_permutation_circuit(
                register_size=c + n,
                permutation_func=lambda ns, (i,):
                    i + (1 << c if control_mask & i == control_mask else 0),
                engine_list=[
                    AutoReplacerEx(DecompositionRuleSet(modules=[
                        bootstrap_ancilla_rules,
                        phase_gradient_rules,
                        increment_rules,
                        multi_not_rules,
                        addition_rules,
                        swap2cnot,
                    ])),
                    LimitedCapabilityEngine(
                        allow_toffoli=True,
                        allow_single_qubit_gates=True
                    ),
                ],
                actions=lambda eng, regs:
                    Increment & regs[0][:c] | regs[0][c:])
