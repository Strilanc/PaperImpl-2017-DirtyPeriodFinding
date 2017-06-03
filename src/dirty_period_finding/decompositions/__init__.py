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

from __future__ import absolute_import

from projectq.setups.decompositions import swap2cnot as _swap2cnot

from . import addition_rules
from . import bootstrap_ancilla_rules
from . import comparison_rules
from . import increment_rules
from . import modular_addition_rules
from . import modular_bimultiplication_rules
from . import modular_double_rules
from . import modular_negate_rules
from . import modular_scaled_addition_rules
from . import multi_not_rules
from . import negate_rules
from . import offset_rules
from . import phase_gradient_rules
from . import pivot_flip_rules
from . import reverse_bits_rules
from . import rotate_bits_rules
from . import scale_rules
from . import scaled_addition_rules

all_defined_decomposition_rules = [
    rule
    for module in [
        _swap2cnot,
        addition_rules,
        bootstrap_ancilla_rules,
        increment_rules,
        modular_addition_rules,
        modular_bimultiplication_rules,
        modular_double_rules,
        modular_negate_rules,
        modular_scaled_addition_rules,
        multi_not_rules,
        negate_rules,
        offset_rules,
        phase_gradient_rules,
        pivot_flip_rules,
        comparison_rules,
        reverse_bits_rules,
        rotate_bits_rules,
        scale_rules,
        scaled_addition_rules,
    ]
    for rule in module.all_defined_decomposition_rules
]
