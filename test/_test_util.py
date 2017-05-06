# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cmath
import math
import random

import numpy as np
from projectq import MainEngine
from projectq.backends import Simulator
from projectq.cengines import DummyEngine
from projectq.ops import H, All, Rz, Measure

from dirty_period_finding.extensions import (
    ClassicalSimulator,
    PermutationSimulator,
    commands_to_ascii_circuit,
    CommandEx,
    BasicGateEx,
)
from dirty_period_finding.gates import X


def check_phase_circuit(register_sizes,
                        expected_turns,
                        engine_list,
                        actions):
    """
    Args:
        register_sizes (list[int]):
        expected_turns (function(register_sizes: tuple[int],
                                 register_vals: tuple[int])):
        engine_list (list[projectq.cengines.BasicEngine]):
        actions (function(eng: MainEngine, registers: list[Qureg])):
    """

    sim = Simulator()
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=sim, engine_list=list(engine_list) + [rec])
    registers = [eng.allocate_qureg(size) for size in register_sizes]

    # Simulate all.
    for reg in registers:
        for q in reg:
            H | q
    rec.received_commands = []
    actions(eng, registers)

    state = np.array(sim.cheat()[1])
    magnitude_factor = math.sqrt(len(state))
    actions = list(rec.received_commands)
    for reg in registers:
        for q in reg:
            Measure | q

    # Compare.
    for i in range(len(state)):
        vals = []
        t = 0
        for r in register_sizes:
            vals.append((i >> t) & ((1 << r) - 1))
            t += r
        vals = tuple(vals)

        actual_factor = state[i]
        expected_turn = expected_turns(register_sizes, vals)
        actual_turn = cmath.phase(state[i]) / (2 * math.pi)
        delta_turn = abs((actual_turn - expected_turn + 0.5) % 1 - 0.5)
        if not (delta_turn < 0.00001):
            print(commands_to_ascii_circuit(actions))
            print("Register Sizes", register_sizes)
            print("Conflicting state: {}".format(vals))
            print("Expected phase: {} deg".format(float(expected_turn)*360))
            print("Actual phase: {} deg".format(actual_turn*360))
        assert abs(abs(actual_factor * magnitude_factor) - 1) < 0.00001
        assert delta_turn < 0.00001


def check_permutation_circuit(register_sizes,
                              permutation,
                              actions,
                              engine_list=(),
                              register_limits=None):
    """
    Args:
        register_sizes (list[int]):
        permutation (function(register_sizes: tuple[int],
                                        register_vals: tuple[int])
                                        : tuple[int]):
        engine_list (list[projectq.cengines.BasicEngine]):
        actions (function(eng: MainEngine, registers: list[Qureg])):
        register_limits (list[int]|None)
    """

    sim = PermutationSimulator()
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=sim, engine_list=list(engine_list) + [rec])
    registers = [eng.allocate_qureg(size) for size in register_sizes]

    # Simulate.
    actions(eng, registers)

    # Compare.
    permutation_matches = sim.permutation_equals(registers,
                                                 permutation,
                                                 register_limits)
    assert register_limits is None or len(registers) == len(register_limits)
    if not permutation_matches:
        example_count = 0
        print(commands_to_ascii_circuit(rec.received_commands))
        print("Register Sizes", register_sizes)
        print("Register Limits", register_limits)
        print("Differing Permutations [input --> actual != expected]:")
        starts = PermutationSimulator.starting_permutation(register_sizes)
        for a, b in zip(starts, sim.get_permutation(registers)):
            b = list(b)
            c = permutation(register_sizes, a)
            c = [i & ((1 << v) - 1) for i, v in zip(c, register_sizes)]
            if not np.array_equal(c, b):
                if register_limits is not None:
                    if any(x >= m for x, m in zip(a, register_limits)):
                        continue
                example_count += 1
                if example_count > 10:
                    print("   (...)")
                    break
                a = tuple(a)
                b = tuple(b)
                c = tuple(c)
                print("   " + str(a) + " --> " + str(b) + " != " + str(c))
    assert permutation_matches


def bit_to_state_permutation(bit_permutation):
    """
    Args:
        bit_permutation (function(reg_sizes: tuple[int],
                                  bit_position: int,
                                  other_vals: tuple[int]) : int):

    Returns:
        function(reg_sizes: tuple[int], reg_vals: tuple[int]) : tuple[int]):
    """
    def permute(sizes, vals):
        permuted = sum(
            ((vals[0] >> i) & 1) << bit_permutation(sizes, i, vals[1:])
            for i in range(sizes[0]))
        return (permuted,) + tuple(vals[1:])
    return permute


def check_quantum_permutation_circuit(register_size,
                                      permutation_func,
                                      actions,
                                      engine_list=()):
    """
    Args:
        register_size (int):
        permutation_func (function(register_sizes: tuple[int],
                                   register_vals: tuple[int]) : tuple[int]):
        actions (function(eng: MainEngine, registers: list[Qureg])):
        engine_list (list[projectq.cengines.BasicEngine]):
    """
    sim = Simulator()
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=sim, engine_list=list(engine_list) + [rec])

    reg = eng.allocate_qureg(register_size)

    All(H) | reg
    for i in range(len(reg)):
        Rz(math.pi / 2**i) | reg[i]
    pre_state = np.array(sim.cheat()[1])

    # Simulate.
    rec.received_commands = []
    actions(eng, [reg])
    actions = list(rec.received_commands)

    post_state = np.array(sim.cheat()[1])
    for q in reg:
        Measure | q

    denom = math.sqrt(len(pre_state))
    pre_state *= denom
    post_state *= denom
    for i in range(len(pre_state)):
        j = permutation_func([register_size], [i]) & ((1 << len(reg)) - 1)
        if not (abs(post_state[j] - pre_state[i]) < 0.000000001):
            print(commands_to_ascii_circuit(actions))
            print("Input", i)
            print("Expected Output", j)
            print("Input Amp at " + str(i), pre_state[i])
            print("Actual Amp at " + str(j), post_state[j])
        assert abs(post_state[j] - pre_state[i]) < 0.000000001


def fuzz_permutation_circuit(register_sizes,
                             permutation,
                             actions,
                             engine_list=(),
                             register_limits=None):
    """
    Args:
        register_sizes (list[int]):
        permutation (function(register_vals: tuple[int],
                                        register_sizes: tuple[int])
                                        : tuple[int]):
        actions (function(eng: MainEngine, registers: list[Qureg])):
        engine_list (list[projectq.cengines.BasicEngine]):
        register_limits (list[int]):
    """

    n = len(register_sizes)
    if register_limits is None:
        register_limits = [1 << size for size in register_sizes]
    assert len(register_limits) == n
    inputs = tuple(random.randint(0, limit - 1) for limit in register_limits)
    outputs = [e % (1 << d)
               for e, d in zip(permutation(register_sizes, inputs),
                               register_sizes)]

    sim = ClassicalSimulator()
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=sim, engine_list=list(engine_list) + [rec])
    registers = tuple(eng.allocate_qureg(size) for size in register_sizes)

    # Encode inputs.
    for i in range(n):
        for b in range(register_sizes[i]):
            if inputs[i] & (1 << b):
                X | registers[i][b]

    # Simulate.
    rec.received_commands = []
    actions(eng, registers)

    # Compare outputs.
    actual_outputs = [sim.read_register(registers[i]) for i in range(n)]
    if outputs != actual_outputs:
        print(commands_to_ascii_circuit(rec.received_commands))
        print("Register Sizes", register_sizes)
        print("Register Limits", register_limits)
        print("Inputs", inputs)
        print("Expected Outputs", outputs)
        print("Actual Outputs", actual_outputs)
    assert outputs == actual_outputs


def cover(n, cut=10):
    if n < cut:
        return range(n)
    return random.randint(0, n - 1),


def check_permutation_decomposition(gate,
                                    decomposition_rule,
                                    register_sizes,
                                    control_size=0,
                                    workspace=0,
                                    register_limits=None):
    """
    Args:
        gate (projectq.ops.BasicMathGate|
              dirty_period_finding.extensions.BasicGateEx):
        decomposition_rule (projectq.cengines.DecompositionRule):
        register_sizes (list[int]):
        control_size (int):
        workspace (int):
        register_limits (list[int]):
    """
    assert isinstance(gate, decomposition_rule.gate_class)
    assert not register_limits or len(register_limits) == len(register_sizes)

    if control_size + workspace + sum(register_sizes) <= 8:
        test_method = check_permutation_circuit
    else:
        test_method = fuzz_permutation_circuit

    def fake_regs(sizes):
        return tuple([None] * i for i in sizes)

    def apply_decomposition(eng, regs):
        command = CommandEx(eng, gate, regs[2:], regs[0])
        assert decomposition_rule.gate_recognizer(command)
        decomposition_rule.gate_decomposer(command)

    def apply_permutation(sizes, args):
        if args[0] == ~(~0 << sizes[0]):
            out = gate.get_math_function(fake_regs(sizes[2:]))(args[2:])
            return tuple(args[:2]) + tuple(out)
        return args

    test_method(
        register_sizes=[control_size, workspace] + register_sizes,
        register_limits=(None
                         if register_limits is None
                         else [1 << control_size, 1 << workspace] +
                              register_limits),
        permutation=apply_permutation,
        actions=apply_decomposition)


class JunkGate(BasicGateEx):
    def ascii_register_labels(self):
        return ['???']

    def ascii_borders(self):
        return False


def record_decomposition(gate,
                         decomposition_rule,
                         register_sizes,
                         control_size=0,
                         workspace=0):
    """
    Args:
        gate (projectq.ops.BasicMathGate|
              dirty_period_finding.extensions.BasicGateEx):
        decomposition_rule (projectq.cengines.DecompositionRule):
        register_sizes (list[int]):
        control_size (int):
        workspace (int):
    """
    assert isinstance(gate, decomposition_rule.gate_class)

    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=rec, engine_list=[])
    regs = tuple(eng.allocate_qureg(size)
                 for size in [control_size, workspace] + register_sizes)
    rec.received_commands = []
    if len(regs[1]):
        JunkGate() | regs[1]

    command = CommandEx(eng, gate, regs[2:], regs[0])
    assert decomposition_rule.gate_recognizer(command)
    decomposition_rule.gate_decomposer(command)
    return rec.received_commands


def decomposition_to_ascii(gate,
                           decomposition_rule,
                           register_sizes,
                           control_size=0,
                           workspace=0):
    return commands_to_ascii_circuit(record_decomposition(gate,
                                                          decomposition_rule,
                                                          register_sizes,
                                                          control_size,
                                                          workspace),
                                     ascii_only=True)
