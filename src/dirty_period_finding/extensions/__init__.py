from . import _monkey_patching
from ._basic_gate_ex import (
    BasicGateEx,
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
