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

from ._addition import Add, Subtract, AdditionGate, SubtractionGate
from ._comparison import (
    PredictOffsetOverflowGate,
    XorOffsetCarrySignalsGate,
    LessThanConstantGate,
)
from ._increment import Increment, Decrement, IncrementGate, DecrementGate
from ._modular_addition import (
    ModularAdditionGate, ModularSubtractionGate, ModularOffsetGate
)
from ._modular_bimultiplication import ModularBimultiplicationGate
from ._modular_double import ModularDoubleGate, ModularUndoubleGate
from ._modular_negate import ModularNegate
from ._modular_scaled_addition import ModularScaledAdditionGate
from ._multi_not import MultiNot, MultiNotGate
from ._negate import NegateGate, Negate
from ._offset import OffsetGate
from ._phase_gradient import PhaseGradientGate, PhaseGradient
from ._pivot_flip import PivotFlipGate, ConstPivotFlipGate, PivotFlip
from ._reverse_bits import ReverseBitsGate, ReverseBits
from ._rotate_bits import RotateBitsGate, LeftRotateBits, RightRotateBits
from ._scale import ScaleGate
from ._scaled_addition import ScaledAdditionGate
from ._vector_phaser import VectorPhaserGate, XPowGate, ZPowGate
