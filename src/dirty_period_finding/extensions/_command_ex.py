from projectq.ops import Command


class CommandEx(Command):
    def __init__(self, engine, gate, qubits, controls=(), tags=()):
        Command.__init__(self, engine, gate, qubits)
        self.control_qubits = controls
        self.tags = list(tags)
