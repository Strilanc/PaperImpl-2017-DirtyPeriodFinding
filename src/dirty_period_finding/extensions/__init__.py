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

from . import _monkey_patching
from ._basic_gate_ex import (
    BasicGateEx,
    gate_and,
    H,
    SelfInverseGateEx,
    GateWithCurriedControls,
)
from ._basic_math_gate_ex import (
    BasicMathGateEx,
    BasicSizedMathGateEx,
    Swap,
    SwapGate,
)
from ._cached_auto_replacer import AutoReplacerEx, MergeRule
from ._classical_simulator import ClassicalSimulator
from ._command_ex import CommandEx
from ._command_predicates import (
    min_controls,
    max_controls,
    max_register_sizes,
    min_register_sizes,
    workspace,
    min_workspace,
    min_workspace_vs_controls,
    min_workspace_vs_reg1,
    max_workspace,
)
from ._limited_capability_engine import LimitedCapabilityEngine
from ._permutation_simulator import PermutationSimulator
from ._to_ascii import commands_to_ascii_circuit
