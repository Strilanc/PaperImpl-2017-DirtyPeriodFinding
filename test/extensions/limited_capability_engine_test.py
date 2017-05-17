import pytest
from projectq import MainEngine
from projectq.cengines import DummyEngine
from projectq.ops import CNOT, H, Y, Z, X, FlushGate, Measure, BasicMathGate
from projectq.types import Qubit

from dirty_period_finding.extensions import LimitedCapabilityEngine


def test_limited_capability_engine_default():
    eng = LimitedCapabilityEngine()
    m = MainEngine(backend=DummyEngine(), engine_list=[eng])
    q = m.allocate_qureg(2)

    assert eng.is_available(Measure.generate_command(q))
    assert not eng.is_available(H.generate_command(q))
    assert not eng.is_available(Z.generate_command(q))
    assert not eng.is_available(CNOT.generate_command(tuple(q)))


def test_limited_capability_engine_classes():
    eng = LimitedCapabilityEngine(allow_classes=[H.__class__, X.__class__],
                                  ban_classes=[X.__class__, Y.__class__])
    m = MainEngine(backend=DummyEngine(), engine_list=[eng])
    q = m.allocate_qureg(5)

    assert eng.is_available(Measure.generate_command(q))  # Default.
    assert eng.is_available(H.generate_command(q))  # Allowed.
    assert not eng.is_available(X.generate_command(q))  # Ban overrides allow.
    assert not eng.is_available(Y.generate_command(q))  # Banned.
    assert not eng.is_available(Z.generate_command(q))  # Not mentioned.


def test_limited_capability_engine_arithmetic():
    default_eng = LimitedCapabilityEngine()
    eng = LimitedCapabilityEngine(allow_arithmetic=True)
    m = MainEngine(backend=DummyEngine(), engine_list=[eng])
    q = m.allocate_qureg(5)

    inc = BasicMathGate(lambda x: x + 1)
    assert not default_eng.is_available(inc.generate_command(q))
    assert eng.is_available(inc.generate_command(q))


def test_limited_capability_engine_classical_instructions():
    default_eng = LimitedCapabilityEngine()
    eng = LimitedCapabilityEngine(allow_classical_instructions=False,
                                  allow_classes=[FlushGate])
    m = MainEngine(backend=DummyEngine(), engine_list=[eng])
    with pytest.raises(ValueError):
        _ = m.allocate_qubit()
    q = Qubit(m, 0)

    assert default_eng.is_available(Measure.generate_command(q))
    assert not eng.is_available(Measure.generate_command(q))


def test_limited_capability_engine_allow_toffoli():
    default_eng = LimitedCapabilityEngine()
    eng = LimitedCapabilityEngine(allow_toffoli=True)
    m = MainEngine(backend=DummyEngine(), engine_list=[eng])
    q = m.allocate_qureg(4)

    assert not default_eng.is_available(Z.generate_command(q))
    assert not default_eng.is_available(X.generate_command(q))
    assert not default_eng.is_available((X & q[1:2]).generate_command(q[0]))
    assert not default_eng.is_available((X & q[1:3]).generate_command(q[0]))
    assert not default_eng.is_available((X & q[1:4]).generate_command(q[0]))

    assert not eng.is_available(Z.generate_command(q))
    assert eng.is_available(X.generate_command(q))
    assert eng.is_available((X & q[1:2]).generate_command(q[0]))
    assert eng.is_available((X & q[1:3]).generate_command(q[0]))
    assert not eng.is_available((X & q[1:4]).generate_command(q[0]))
