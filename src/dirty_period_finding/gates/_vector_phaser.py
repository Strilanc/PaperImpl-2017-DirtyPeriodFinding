# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import abc
import cmath
import math

import numpy as np

from dirty_period_finding.extensions import BasicGateEx


def _exp_pi_i(f):
    f %= 2
    if f == 0.5:
        return 1j
    if f == 1:
        return -1
    if f == 1.5:
        return -1j
    return cmath.exp(1j * math.pi * f)


def _superscriptify(text):
    normal = '-01234567890'
    superscript = '⁻⁰¹²³⁴⁵⁶⁷⁸⁹'
    for n, s in zip(normal, superscript):
        text = text.replace(n, s)
    return text


class VectorPhaserGate(BasicGateEx):
    def __init__(self, vector, half_turns=1.0):
        BasicGateEx.__init__(self)
        self.vector = vector
        self.half_turns = half_turns

    @property
    def matrix(self):
        v = np.mat(self.vector, np.float64)
        d = np.dot(np.conj(np.transpose(v)), v)
        d /= np.trace(d)
        p = _exp_pi_i(self.half_turns)
        return np.identity(len(self.vector)) + (p - 1) * d

    def get_inverse(self):
        return VectorPhaserGate(self.vector, -self.half_turns)

    def __pow__(self, power):
        """

        Args:
            power (int|float|fractions.Fraction):
        Returns:
            VectorPhaserGate:
        """
        return self.with_half_turns(self.half_turns * power)

    @abc.abstractmethod
    def base_str(self):
        raise NotImplementedError()

    def with_half_turns(self, turns):
        raise NotImplementedError()

    def _exponent_str(self):
        if self.half_turns % 2 == 0:
            return '0'
        h = abs(self.half_turns)
        k = int(math.floor(0.5 + math.log(float(h), 2)))
        if 2**k == h:
            return '{}2{}'.format(
                    '-' if self.half_turns < 0 else '',
                    _superscriptify(str(k)))
        return str(self.half_turns)

    def _exponent_repr(self):
        if self.half_turns % 2 == 0:
            return '0'
        h = abs(self.half_turns)
        k = int(math.floor(0.5 + math.log(float(h), 2)))
        if 2**k == h:
            return '{}(2**{})'.format(
                '-' if self.half_turns < 0 else '', repr(k))
        return repr(self.half_turns)

    def __str__(self):
        if self.half_turns % 2 == 1:
            return self.base_str()
        return '{}^{}'.format(self.base_str(), self._exponent_str())

    def __repr__(self):
        if self.half_turns % 2 == 1:
            return self.base_str()
        return '{}**({})'.format(self.base_str(), self._exponent_repr())

    def __eq__(self, other):
        return (isinstance(other, VectorPhaserGate) and
                np.array_equal(self.vector, other.vector) and
                self.half_turns == other.half_turns)

    def __hash__(self):
        return hash((VectorPhaserGate, self.half_turns, tuple(self.vector)))


class ZGate(VectorPhaserGate):
    def __init__(self, half_turns=1.0):
        VectorPhaserGate.__init__(self, [0, 1], half_turns)

    def with_half_turns(self, half_turns):
        return ZGate(half_turns)

    def base_str(self):
        return "Z"

    def __str__(self):
        if self.half_turns == 0.5:
            return "S"
        if self.half_turns == 0.25:
            return "T"
        if self.half_turns == -0.5:
            return "S⁻¹"
        if self.half_turns == -0.25:
            return "T⁻¹"
        return VectorPhaserGate.__str__(self)


class XGate(VectorPhaserGate):
    def __init__(self, half_turns=1.0):
        VectorPhaserGate.__init__(self, [1, -1], half_turns)

    def with_half_turns(self, half_turns):
        return XGate(half_turns)

    def base_str(self):
        return 'X'


X = XGate()
Z = ZGate()
