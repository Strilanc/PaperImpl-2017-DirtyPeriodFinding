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

import numpy as np

from projectq.cengines import BasicEngine
from projectq.ops import (XGate,
                          BasicMathGate,
                          Measure,
                          FlushGate,
                          Allocate,
                          Deallocate)


class PermutationSimulator(BasicEngine):
    def __init__(self):
        BasicEngine.__init__(self)
        self._states = np.array([0], np.int32)

    @staticmethod
    def starting_permutation(register_sizes):
        sim = PermutationSimulator()
        from projectq import MainEngine
        eng = MainEngine(sim, [])
        quregs = [eng.allocate_qureg(n) for n in register_sizes]
        return sim.get_permutation(quregs)

    def get_permutation(self, quregs):
        n = sum(len(reg) for reg in quregs)
        if len(self._states) != 1 << n:
            raise ValueError("Need all allocated qubits.")

        result = np.zeros((1 << n, len(quregs)), np.int32)
        for i in range(len(quregs)):
            result[:, i] = self._get_partial_permutation(quregs[i])
        return result

    def _get_partial_permutation(self, qureg):
        return np.array(self._internal_order_to_given_order(
            self._states, qureg))

    def permutation_equals(self,
                           quregs,
                           permutation_func,
                           register_limits=None):
        """
        Args:
            quregs (list[Qureg]):
            permutation_func (function(reg_sizes: tuple[int],
                                       reg_vals: tuple[int]) : tuple[int]):
            register_limits (list[int]):
        Returns:
            bool:
        """
        assert not register_limits or len(quregs) == len(register_limits)
        actual = self.get_permutation(quregs)
        ns = tuple(len(reg) for reg in quregs)
        for i in range(len(self._states)):
            xs = []
            t = 0
            for reg in quregs:
                xs.append((i >> t) & ((1 << len(reg)) - 1))
                t += len(reg)
            if register_limits is not None:
                if any(x >= m for x, m in zip(xs, register_limits)):
                    continue
            ys = permutation_func(ns, xs)
            ys = tuple(i & ((1 << len(a)) - 1) for i, a in zip(ys, quregs))
            if ys != tuple(actual[i]):
                return False
        return True

    def _internal_order_to_given_order(self, v, little_endian_qubits):
        return sum(
            ((v >> little_endian_qubits[i].id) & 1) << i
            for i in range(len(little_endian_qubits)))

    def _given_order_to_internal_order(self, v, little_endian_qubits):
        return sum(
            ((v >> i) & 1) << little_endian_qubits[i].id
            for i in range(len(little_endian_qubits)))

    def is_available(self, cmd):
        return (cmd.gate == Measure or
                cmd.gate == Allocate or
                cmd.gate == Deallocate or
                isinstance(cmd.gate, BasicMathGate) or
                isinstance(cmd.gate, FlushGate) or
                isinstance(cmd.gate, XGate))

    def receive(self, command_list):
        for cmd in command_list:
            self._handle(cmd)
        if not self.is_last_engine:
            self.send(command_list)

    def _apply_operation(self, controls, func):
        c = self._given_order_to_internal_order(
            (1 << len(controls)) - 1, controls)
        for i in range(len(self._states)):
            if self._states[i] & c == c:
                self._states[i] = func(self._states[i])

    def _handle(self, cmd):
        if (cmd.gate == Measure or
                isinstance(cmd.gate, FlushGate) or
                cmd.gate == Deallocate):
            return

        if cmd.gate == Allocate:
            new_id = cmd.qubits[0][0].id
            if not (0 <= new_id < 32):
                raise ValueError("Too many allocations.")
            n = len(self._states)
            self._states = np.resize(self._states, 2 * n)
            self._states[n:] += 1 << new_id
            return

        if isinstance(cmd.gate, XGate):
            assert len(cmd.qubits) == 1 and len(cmd.qubits[0]) == 1
            target = cmd.qubits[0][0]
            self._apply_operation(cmd.control_qubits,
                                  lambda x: x ^ (1 << target.id))
            return

        if isinstance(cmd.gate, BasicMathGate):
            def reordered_op(v):
                xs = [self._internal_order_to_given_order(v, reg)
                      for reg in cmd.qubits]
                ys = cmd.gate.get_math_function(cmd.qubits)(xs)
                pys = [
                    self._given_order_to_internal_order(
                        y & ((1 << len(reg)) - 1),
                        reg)
                    for y, reg in zip(ys, cmd.qubits)
                ]
                pxs = [
                    self._given_order_to_internal_order(x, reg)
                    for x, reg in zip(xs, cmd.qubits)
                ]
                return v + sum(pys) - sum(pxs)
            self._apply_operation(cmd.control_qubits, reordered_op)
            return

        raise ValueError(
            "Unsupported operation {}.".format(cmd) +
            "Only support alloc/dealloc/measure/not/math ops.")
