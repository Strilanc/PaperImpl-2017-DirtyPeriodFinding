# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import BasicEngine
from projectq.ops import BasicMathGate, ClassicalInstructionGate, XGate


class LimitedCapabilityEngine(BasicEngine):
    """
    An engine that restricts the available operations, on top of any
    restrictions for later engines.

    Only commands that meet as least one of the 'allow' criteria and NONE of
    the 'ban' criteria given to the constructor are considered available. Also
    gates are not considered available if the underlying engine can't receive
    them.
    """
    def __init__(self,
                 allow_classical_instructions=True,
                 allow_all=False,
                 allow_arithmetic=False,
                 allow_toffoli=False,
                 allow_nots_with_many_controls=False,
                 allow_single_qubit_gates=False,
                 allow_single_qubit_gates_with_controls=False,
                 allow_classes=(),
                 allow_custom_predicate=lambda cmd: False,
                 ban_classes=(),
                 ban_custom_predicate=lambda cmd: False):
        """
        Constructs a LimitedCapabilityEngine that accepts commands based on
        the given criteria arguments.

        Note that a command is accepted if it meets *none* of the ban criteria
        and *any* of the allow criteria.

        Args:
            allow_classical_instructions (bool):
                Enabled by default. Marks classical instruction commands like
                'Allocate', 'Flush', etc as available.

            allow_all (bool):
                Defaults to allowing all commands.
                Any ban criteria will override this default.

            allow_arithmetic (bool):
                Allows gates with the BasicMathGate type.

            allow_toffoli (bool):
                Allows NOT gates with at most 2 controls.

            allow_nots_with_many_controls (bool):
                Allows NOT gates with arbitrarily many controls.

            allow_single_qubit_gates (bool):
                Allows gates that affect only a single qubit
                (counting controls).

            allow_single_qubit_gates_with_controls (bool):
                Allows gates that target only a single qubit.

            allow_classes (list[type]):
                Allows any gates matching the given class.

            allow_custom_predicate (function(Command) : bool):
                Allows any gates that cause the given function to return True.

            ban_classes (list[type]):
                Bans any gates matching the given class.

            ban_custom_predicate (function(Command) : bool):
                Bans gates that cause the given function to return True.
        """
        BasicEngine.__init__(self)
        self.allow_arithmetic = allow_arithmetic
        self.allow_all = allow_all
        self.allow_nots_with_many_controls = allow_nots_with_many_controls
        self.allow_single_qubit_gates = allow_single_qubit_gates
        self.allow_single_qubit_gates_with_controls = (
            allow_single_qubit_gates_with_controls)
        self.allow_toffoli = allow_toffoli
        self.allow_classical_instructions = allow_classical_instructions
        self.allowed_classes = tuple(allow_classes)
        self.allow_custom_predicate = allow_custom_predicate
        self.ban_classes = tuple(ban_classes)
        self.ban_custom_predicate = ban_custom_predicate

    def is_available(self, cmd):
        return (self._allow_command(cmd) and
                not self._ban_command(cmd) and
                (self.next_engine is None or
                 self.next_engine.is_available(cmd)))

    def receive(self, command_list):
        for cmd in command_list:
            if not self._allow_command(cmd):
                raise ValueError("Command not allowed: " + str(cmd))
            if self._ban_command(cmd):
                raise ValueError("Command banned: " + str(cmd))
        if not self.is_last_engine:
            self.send(command_list)

    def _ban_command(self, cmd):
        if any(isinstance(cmd.gate, c) for c in self.ban_classes):
            return True

        return self.ban_custom_predicate(cmd)

    def _allow_command(self, cmd):
        if (self.allow_classical_instructions and
                isinstance(cmd.gate, ClassicalInstructionGate)):
            return True

        if self.allow_arithmetic and isinstance(cmd.gate, BasicMathGate):
            return True
        if self.allow_arithmetic and isinstance(cmd.gate, XGate):
            return True

        if (self.allow_toffoli and isinstance(cmd.gate, XGate) and
                len(cmd.control_qubits) <= 2):
            return True

        if (self.allow_single_qubit_gates and
                sum(len(reg) for reg in cmd.all_qubits) == 1 and
                hasattr(cmd.gate, 'matrix') and
                len(cmd.gate.matrix) == 2):
            return True

        if self.allow_single_qubit_gates_with_controls and sum(
                len(reg) for reg in cmd.qubits) == 1:
            return True

        if self.allow_nots_with_many_controls and isinstance(cmd.gate, XGate):
            return True

        if any(isinstance(cmd.gate, c) for c in self.allowed_classes):
            return True

        if self.allow_custom_predicate(cmd):
            return True

        return self.allow_all
