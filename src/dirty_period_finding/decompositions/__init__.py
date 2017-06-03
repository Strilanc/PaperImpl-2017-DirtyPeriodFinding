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

import addition_rules
import bootstrap_ancilla_rules
import increment_rules
import modular_addition_rules
import modular_bimultiplication_rules
import modular_double_rules
import modular_negate_rules
import modular_scaled_addition_rules
import multi_not_rules
import offset_rules
import phase_gradient_rules
import pivot_flip_rules
import comparison_rules
import reverse_bits_rules
import rotate_bits_rules
from projectq.setups.decompositions import swap2cnot as _swap2cnot

all_defined_decomposition_rules = [
    rule
    for module in [
        addition_rules,
        bootstrap_ancilla_rules,
        increment_rules,
        modular_addition_rules,
        modular_bimultiplication_rules,
        modular_double_rules,
        modular_negate_rules,
        modular_scaled_addition_rules,
        multi_not_rules,
        offset_rules,
        phase_gradient_rules,
        pivot_flip_rules,
        comparison_rules,
        reverse_bits_rules,
        rotate_bits_rules,
        _swap2cnot,
    ]
    for rule in module.all_defined_decomposition_rules
]
