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

from __future__ import division
from __future__ import unicode_literals

from projectq.cengines import DecompositionRuleSet

from dirty_period_finding.decompositions import phase_gradient_rules
from dirty_period_finding.extensions import (
    LimitedCapabilityEngine,
    AutoReplacerEx,
)
from dirty_period_finding.gates import PhaseGradient
from .._test_util import check_phase_circuit


def test_circuit_implements_phase_angle_specified_by_gate():
    check_phase_circuit(
        register_sizes=[8],
        expected_turns=lambda lens, vals:
            PhaseGradient.phase_angle_in_turns_for(vals[0], lens[0]),
        engine_list=[
            AutoReplacerEx(DecompositionRuleSet(modules=[
                phase_gradient_rules
            ])),
            LimitedCapabilityEngine(
                allow_single_qubit_gates=True
            )
        ],
        actions=lambda eng, regs: PhaseGradient | regs[0])


def test_controlled_circuit():
    check_phase_circuit(
        register_sizes=[5, 2],
        expected_turns=lambda (ns, nc), (s, c):
            s/2**ns/-4 if c + 1 == 1 << nc else 0,
        engine_list=[
            AutoReplacerEx(DecompositionRuleSet(modules=[
                phase_gradient_rules
            ])),
            LimitedCapabilityEngine(
                allow_single_qubit_gates_with_controls=True
            )
        ],
        actions=lambda eng, regs: PhaseGradient**(-1/4) & regs[1] | regs[0])
