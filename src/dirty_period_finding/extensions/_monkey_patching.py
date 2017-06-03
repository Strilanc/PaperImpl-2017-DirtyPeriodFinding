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

import weakref

from projectq import MainEngine
from projectq.backends import ResourceCounter
from projectq.backends import Simulator
from projectq.cengines import BasicEngine, UnsupportedEngineError
from projectq.ops import Command, Measure, FlushGate, XGate, ZGate
from projectq.types import Qubit, Qureg

from ._basic_gate_ex import gate_and


def command_str(cmd):
    gate_str = '{}'.format(cmd.gate).strip() or cmd.gate.__class__.__name__

    if len(cmd.control_qubits) > 0:
        return "Command({} & {} | {})".format(
            gate_str,
            Qureg(cmd.control_qubits),
            tuple(Qureg(e) for e in cmd.qubits))

    return "Command({} | {})".format(
        gate_str,
        tuple(Qureg(e) for e in cmd.qubits))


def qureg_str(reg):
    if len(reg) == 0:
        return "Q[]"
    start_id = reg[0].id
    next_id = start_id + 1
    if len(reg) == 1:
        return "Q[{}]".format(start_id)
    id_list = []

    def drain():
        id_list.append('{}-{}'.format(start_id, next_id-1)
                       if next_id > start_id + 1
                       else '{}'.format(start_id))
    for q in reg[1:]:
        if q.id == next_id:
            next_id += 1
            continue

        drain()
        start_id = q.id
        next_id = q.id + 1

    drain()
    return "Q[{}]".format(', '.join(id_list))


def resource_ctr_add_cmd(self, cmd):
    """
    Add a gate to the count.
    """
    from projectq.ops import Deallocate, Allocate, Measure
    from projectq.meta import get_control_count
    if cmd.gate == Allocate:
        self._active_qubits += 1
    elif cmd.gate == Deallocate:
        self._active_qubits -= 1
    elif cmd.gate == Measure:
        for qureg in cmd.qubits:
            for qubit in qureg:
                self.main_engine.set_measurement_result(qubit, 0)

    self.max_width = max(self.max_width, self._active_qubits)

    ctrl_cnt = get_control_count(cmd)
    gate_name = '{}{}'.format(ctrl_cnt * "C", cmd.gate)

    try:
        self.gate_counts[gate_name] += 1
    except KeyError:
        self.gate_counts[gate_name] = 1


def MainEngine_init(self, backend=None, engine_list=None):
    """
    Initialize the main compiler engine and all compiler engines.
    Sets 'next_engine'- and 'main_engine'-attributes of all compiler
    engines and adds the back-end as the last engine.
    Args:
        backend (BasicEngine): Backend to send the circuit to.
        engine_list (list<BasicEngine>): List of engines / backends to use
            as compiler engines.
    Example:
        .. code-block:: python
            from projectq import MainEngine
            eng = MainEngine() # uses default setup and the Simulator
    Alternatively, one can specify all compiler engines explicitly, e.g.,
    Example:
        .. code-block:: python
            from projectq.cengines import TagRemover,AutoReplacer,LocalOptimizer,DecompositionRuleSet
            from projectq.backends import Simulator
            from projectq import MainEngine
            rule_set = DecompositionRuleSet()
            engines = [AutoReplacer(rule_set), TagRemover(), LocalOptimizer(3)]
            eng = MainEngine(Simulator(), engines)
    """
    BasicEngine.__init__(self)

    if backend is None:
        backend = Simulator()
    else:  # Test that backend is BasicEngine object
        if not isinstance(backend, BasicEngine):
            raise UnsupportedEngineError(
                "\nYou supplied a backend which is not supported,\n"
                "i.e. not an instance of BasicEngine.\n"
                "Did you forget the brackets to create an instance?\n"
                "E.g. MainEngine(backend=Simulator) instead of \n"
                "     MainEngine(backend=Simulator())")
    if engine_list is None:
        raise ValueError("No engine list")
    else:  # Test that engine list elements are all BasicEngine objects
        if not isinstance(engine_list, list):
            raise UnsupportedEngineError(
                "\n The engine_list argument is not a list!\n")
        for current_eng in engine_list:
            if not isinstance(current_eng, BasicEngine):
                raise UnsupportedEngineError(
                    "\nYou supplied an unsupported engine in engine_list,"
                    "\ni.e. not an instance of BasicEngine.\n"
                    "Did you forget the brackets to create an instance?\n"
                    "E.g. MainEngine(engine_list=[AutoReplacer]) instead "
                    "of\n     MainEngine(engine_list=[AutoReplacer()])")

    engine_list = engine_list + [backend]
    self.backend = backend

    # Test that user did not supply twice the same engine instance
    num_different_engines = len(set([id(item) for item in engine_list]))
    if len(engine_list) != num_different_engines:
        raise UnsupportedEngineError(
            "\n Error:\n You supplied twice the same engine as backend" +
            " or item in engine_list. This doesn't work. Create two \n" +
            " separate instances of a compiler engine if it is needed\n" +
            " twice.\n")

    self._qubit_idx = int(0)
    for i in range(len(engine_list) - 1):
        engine_list[i].next_engine = engine_list[i + 1]
        engine_list[i].main_engine = self
    engine_list[-1].main_engine = self
    engine_list[-1].is_last_engine = True
    self.next_engine = engine_list[0]
    self.main_engine = self
    self.active_qubits = weakref.WeakSet()
    self._measurements = dict()
    self.dirty_qubits = set()


def measure_register(qureg):
    if not len(qureg):
        return 0
    eng = [q.engine for q in qureg][0]
    Measure | qureg
    eng.flush()
    return sum(int(qureg[i]) << i for i in range(len(qureg)))


def measure_qubit(qubit):
    Measure | qubit
    qubit.engine.flush()
    return bool(qubit)


def simulator_receive(self, command_list):
    if self.is_last_engine:
        for cmd in command_list:
            self._handle(cmd)
    else:
        for cmd in command_list:
            self._handle(cmd)
            self.send([cmd])


original_handle = Simulator._handle
_x_list = [[0, 1], [1, 0]]


def sim_handle(self, cmd):
    if cmd.gate.__class__ is XGate:
        target = [cmd._qubits[0][0].id]
        controls = [qb.id for qb in cmd.control_qubits]
        self._simulator.apply_controlled_gate(_x_list, target, controls)
        if not self._gate_fusion:
            self._simulator.run()
    elif cmd.gate.__class__ is FlushGate:
        self._simulator.run()
    else:
        original_handle(self, cmd)


# Well well well, isn't this a terrifying little block of code.
Command.__str__ = command_str
Command.__repr__ = command_str
Qureg.__str__ = qureg_str
Qureg.__repr__ = qureg_str
ResourceCounter._add_cmd = resource_ctr_add_cmd
Qubit.__del__ = lambda x: None
Qureg.__int__ = lambda x: sum(int(x[i]) << i for i in range(len(x)))
BasicEngine.__del__ = lambda x: None
MainEngine.__init__ = MainEngine_init
Qureg.measure = measure_register
Qubit.measure = measure_qubit
Simulator.receive = simulator_receive
XGate.__and__ = gate_and
ZGate.__and__ = gate_and
XGate.__eq__ = lambda self, other: other.__class__ is XGate
XGate.__hash__ = lambda self: hash((XGate,))
Simulator._handle = sim_handle
XGate.get_math_function = lambda self, _: lambda x: (x[0] ^ 1,)
