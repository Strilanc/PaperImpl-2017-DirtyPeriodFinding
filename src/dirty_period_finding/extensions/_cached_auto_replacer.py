# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import BasicEngine, DummyEngine, MainEngine
from projectq.cengines._replacer import NoGateDecompositionError
from projectq.ops import get_inverse, FlushGate
from projectq.types import WeakQubitRef, Qureg

from ._command_ex import CommandEx


class AutoReplacerEx(BasicEngine):
    def __init__(self,
                 decomposition_rule_set,
                 decomposition_chooser=
                     lambda cmd, decomposition_list: decomposition_list[0]):
        BasicEngine.__init__(self)
        self._cached_results = dict()
        self.decomposition_rule_set = decomposition_rule_set
        self.decomposition_chooser = decomposition_chooser

    def is_available(self, cmd):
        return (isinstance(cmd, FlushGate) or
                self.is_last_engine or
                self.next_engine.is_available(cmd))

    def _all_decomps_for(self, cmd):
        key = cmd.gate.__class__.__name__
        inv_key = get_inverse(cmd.gate).__class__.__name__
        ds = self.decomposition_rule_set.decompositions

        forward = ds[key] if key in ds else []
        backward = [
            d.get_inverse_decomposition()
            for d in ds[inv_key]
        ] if inv_key in ds else []

        return [d for d in forward + backward if d.check(cmd)]

    def _pick_decomp_for(self, cmd):
        choices = self._all_decomps_for(cmd)
        if not choices:
            raise NoGateDecompositionError(
                'No decomposition for {}.'.format(cmd))
        return self.decomposition_chooser(cmd, choices)

    def _translate(self, original_command, flat_commands, id_map):
        rev_id_map = {val: key for key, val in id_map.iteritems()}
        return [
            CommandEx(
                engine=original_command.engine,
                gate=cmd.gate,
                qubits=self.remap_quregs(cmd.qubits, rev_id_map),
                controls=self.remap_qureg(cmd.control_qubits, rev_id_map),
                tags=original_command.tags + cmd.tags)
            for cmd in flat_commands
        ]

    def remap_quregs(self, quregs, id_map):
        return tuple(self.remap_qureg(qureg, id_map) for qureg in quregs)

    def remap_qureg(self, qureg, id_map):
        return Qureg(WeakQubitRef(q.engine, id_map[q.id]) for q in qureg)

    def _canonicalize(self, cmd):
        id_map = {}
        for qureg in cmd.all_qubits:
            for q in qureg:
                if q.id not in id_map:
                    id_map[q.id] = len(id_map)
        num_used = len(id_map)

        for q in self.main_engine.active_qubits:
            if q.id not in id_map:
                id_map[q.id] = len(id_map)
        num_available = len(id_map) - num_used

        new_cmd = CommandEx(
            engine=cmd.engine,
            gate=cmd.gate,
            qubits=self.remap_quregs(cmd.qubits, id_map),
            controls=self.remap_qureg(cmd.control_qubits, id_map),
            tags=cmd.tags)

        key = (new_cmd.gate, tuple(tuple(q.id for q in qureg)
                                   for qureg in new_cmd.all_qubits))
        return new_cmd, id_map, key, num_used, num_available

    def _recursive_decompose(self, cmd):
        if self.is_available(cmd):
            return [cmd]

        canonical_cmd, id_map, key, used, avail = self._canonicalize(cmd)
        if key in self._cached_results:
            if self._cached_results == 'IN PROGRESS':
                raise NoGateDecompositionError(
                    'Cyclic decomposition for {}.'.format(cmd))
            return self._translate(cmd, self._cached_results[key], id_map)
        self._cached_results[key] = 'IN PROGRESS'

        rec = DummyEngine(save_commands=True)
        eng = MainEngine(backend=rec, engine_list=[])
        involved = eng.allocate_qureg(used)
        workspace = eng.allocate_qureg(avail)
        rec.received_commands = []
        canonical_cmd.engine = eng

        self._pick_decomp_for(cmd).decompose(canonical_cmd)
        intermediate_result = rec.received_commands

        assert involved is not None
        assert workspace is not None

        flattened_result = [leaf
                            for child in intermediate_result
                            for leaf in self._recursive_decompose(child)]

        self._cached_results[key] = flattened_result
        return self._translate(cmd, flattened_result, id_map)

    def receive(self, command_list):
        for cmd in command_list:
            self.send(self._recursive_decompose(cmd))
