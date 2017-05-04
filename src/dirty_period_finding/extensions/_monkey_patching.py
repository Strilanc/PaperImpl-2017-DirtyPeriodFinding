from __future__ import unicode_literals

from projectq.ops import Command
from projectq.types import Qureg


def command_str(cmd):
    if len(cmd.control_qubits) > 0:
        return "Command({} & {} | {})".format(
            cmd.gate,
            Qureg(cmd.control_qubits),
            tuple(Qureg(e) for e in cmd.qubits))

    return "Command({} | {})".format(
        cmd.gate,
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


Command.__str__ = command_str
Command.__repr__ = command_str
Qureg.__str__ = qureg_str
Qureg.__repr__ = qureg_str
