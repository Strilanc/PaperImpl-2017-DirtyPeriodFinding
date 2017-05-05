from __future__ import unicode_literals

from projectq.ops import Command
from projectq.types import Qubit, Qureg
from projectq.backends import ResourceCounter


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


Command.__str__ = command_str
Command.__repr__ = command_str
Qureg.__str__ = qureg_str
Qureg.__repr__ = qureg_str
ResourceCounter._add_cmd = resource_ctr_add_cmd
Qubit.__del__ = lambda x: None
Qureg.__int__ = lambda x: sum(int(x[i]) << i for i in range(len(x)))
