# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

from projectq.ops import Command, Allocate, Deallocate, SwapGate, XGate, FlushGate


# TODO: Make this not be a horrible pile of half-correct hacks.

def _between_wire_pattern(cur_role, next_role):
    cur_in = 'register' in cur_role
    next_in = 'register' in next_role
    change = next_role != cur_role

    if change and cur_in and next_in:
        return '├──┤'
    if change and next_in:
        return '┌─┴┐'
    if change and cur_in:
        return '└─┬┘'
    if cur_in:
        return '│  │'
    return '  │ '


def _on_wire_pattern(role):
    return ('──•─' if 'control' in role
            else '┤  ├' if 'register' in role
            else '──┼─')


def _between_wire_cols(has_controls,
                       used_indices,
                       swap_line,
                       roles,
                       index_to_id,
                       w,
                       border):
    between_wires = []
    prev_role = {}
    n = len(index_to_id)
    for i in range(n + 1):
        role = set() if i >= n else roles[index_to_id[i]]

        spacing_w = w - 3 if border else w - 1
        w1 = spacing_w // 2
        w2 = spacing_w - w1

        has_control_line = (has_controls and
                            min(used_indices) < i <= max(used_indices))
        if swap_line[0] < i <= swap_line[1]:
            has_control_line = True
        pattern = _between_wire_pattern(prev_role, role)
        space = pattern[1] if border else ' '
        mid = (space if not has_control_line
               else '│' if not border
               else pattern[2])
        center = space * w1 + mid + space * w2
        full = pattern[0] + center + pattern[3] if border else center
        between_wires.append(full)
        prev_role = role
    return between_wires


def _on_wire_cols(labels,
                  has_controls,
                  used_indices,
                  swap_line,
                  roles,
                  notes,
                  index_to_id,
                  w,
                  border):
    label_positions = {}
    for i in range(len(labels)):
        found = [j
                 for j in range(len(index_to_id))
                 if 'register'+str(i) in roles[j] and j not in label_positions]
        if border:
            if found:
                label_positions[found[len(found)//2]] = labels[i]
        else:
            for f in found:
                label_positions[f] = labels[i]

    on_wires = []
    for i in range(len(index_to_id)):
        role = roles[index_to_id[i]]
        notes_here = notes[index_to_id[i]]
        if not border and i in label_positions:
            on_wires.append(label_positions[i])
            continue
        pattern = _on_wire_pattern(role)
        has_control_line = (has_controls and
                            min(used_indices) <= i <= max(used_indices))
        if swap_line[0] <= i <= swap_line[1]:
            has_control_line = True

        space = pattern[1] if border else '─'
        control_line = pattern[2]
        mid = control_line if has_control_line else ''
        if i in label_positions:
            mid = label_positions[i]

        spacing_w = w - (2 if border else 0) - len(mid)
        w1 = spacing_w // 2
        w2 = spacing_w - w1
        center = space * w1 + mid + space * w2
        if border and notes_here:
            center = str(notes_here[0]) + center[1:]
        full = pattern[0] + center + pattern[3] if border else center
        on_wires.append(full)
    return on_wires


def _labels_border(cmd):
    if cmd.gate is Allocate:
        return ['|0⟩'], False
    if cmd.gate is Deallocate:
        return ['┤  '], False
    if isinstance(cmd.gate, SwapGate):
        return ['×', '×'], False
    if isinstance(cmd.gate, XGate):
        return ['⊕'], False

    border = not hasattr(cmd.gate, 'ascii_borders') or cmd.gate.ascii_borders()
    if hasattr(cmd.gate, 'ascii_register_labels'):
        return cmd.gate.ascii_register_labels(), border
    return [unicode(cmd.gate)], border


def _wire_col(cmd, id_to_index, index_to_id):
    roles = defaultdict(set)
    notes = defaultdict(list)

    used_indices = [id_to_index[c.id]
                    for reg in cmd.all_qubits
                    for c in reg]

    for c in cmd.control_qubits:
        roles[c.id].add('control')
    for i in range(len(cmd.qubits)):
        m = min(id_to_index[q.id] for q in cmd.qubits[i])
        for j in range(len(cmd.qubits[i])):
            q = cmd.qubits[i][j]
            roles[q.id].add('register')
            roles[q.id].add('register' + str(i))
            if id_to_index[q.id] - j != m:
                notes[q.id].append(str(j)[-1])

    labels, border = _labels_border(cmd)
    w = max(len(e) for e in labels) + (
        0 if not border
        else 2 if sum(len(reg) for reg in cmd.qubits) == 1
        else 6)

    swap_line = [-1, -1] if cmd.gate.__class__ != SwapGate else [
        min(id_to_index[cmd.qubits[0][0].id],
            id_to_index[cmd.qubits[1][0].id]),
        max(id_to_index[cmd.qubits[0][0].id],
            id_to_index[cmd.qubits[1][0].id]),
    ]

    between_wires = _between_wire_cols(len(cmd.control_qubits) > 0,
                                       used_indices,
                                       swap_line,
                                       roles,
                                       index_to_id,
                                       w,
                                       border)
    on_wires = _on_wire_cols(labels,
                             len(cmd.control_qubits) > 0,
                             used_indices,
                             swap_line,
                             roles,
                             notes,
                             index_to_id,
                             w,
                             border)
    col = []
    for i in range(len(id_to_index)):
        col.append(between_wires[i])
        col.append(on_wires[i])
    col.append(between_wires[-1])
    return col


def commands_to_ascii_circuit(commands, ascii_only=False):
    """
    Args:
        commands (list[Command]): Commands making up the circuit.
        ascii_only (bool):
    Returns:
        str:
            Fixed-width text drawing using ascii and unicode characters.
    """
    commands = list(cmd
                    for cmd in commands
                    if not isinstance(cmd.gate, FlushGate))

    qubit_ids = set(qubit.id
                    for cmd in commands
                    for qureg in cmd.all_qubits
                    for qubit in qureg)
    n = len(qubit_ids)
    index_to_id = {}
    id_to_index = {}
    for id in sorted(qubit_ids):
        index = len(index_to_id)
        index_to_id[index] = id
        id_to_index[id] = index

    empty_col = ([' ', '─'] * (n + 1))[:-1]
    init_col = (['    ', '|0⟩─'] * (n + 1))[:-1]

    cols = [init_col]
    skipping_allocs = True
    for cmd in commands:
        if skipping_allocs and cmd.gate is Allocate:
            continue
        skipping_allocs = False
        cols.append(_wire_col(cmd, id_to_index, index_to_id))
        cols.append(empty_col)

    rows = [''.join(col[row] for col in cols).rstrip()
            for row in range(len(empty_col))]
    result = '\n'.join(row for row in rows if row).rstrip()
    if ascii_only:
        result = (result
                  .replace('─', '-')
                  .replace('┐', '.')
                  .replace('┌', '.')
                  .replace('┘', '`')
                  .replace('└', '`')
                  .replace('┼', '|')
                  .replace('│', '|')
                  .replace('┬', '|')
                  .replace('┴', '|')
                  .replace('┤', '|')
                  .replace('├', '|')
                  .replace('•', '@')
                  .replace('⊕', 'X')
                  .replace('×', '*')
                  .replace('·', '*')
                  .replace('÷', '/')
                  .replace('⟩', '>'))
    return result
