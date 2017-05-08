# Dirty Period Finding with 2n+1 qubits

This repository contains code for generating and validating the
constructions from my [work in progress]
"Factoring with n+2 clean qubits and n-1 dirty qubits".

# Build Instructions

[Work in Progress]

0. Have git and pip installed.
1. Clone the repository.
2. pip install projectq
3. `pytest`
4. [fiddle with python path?]
5. `cd src`, `python dirty_period_finding/find_period.py`

# Table of Circuit Constructions

| Name | In Paper | In Source | In [Quirk](http://algassert.com/quirk) |
| --- | --- | --- | --- |
| Find Period | ![3][3] <br> fig [1][1], [2][2], [3][3] | ??? | [period-finding R=55 B=26 p=10](http://algassert.com/quirk#circuit=%7B%22cols%22%3A%5B%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22~mdaf%22%2C1%2C1%2C1%2C%22~h1nm%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%7B%22id%22%3A%22setR%22%2C%22arg%22%3A55%7D%2C1%2C1%2C1%2C%7B%22id%22%3A%22setB%22%2C%22arg%22%3A26%7D%5D%2C%5B%5D%2C%5B%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22X%22%5D%2C%5B%22inputA10%22%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22*BToAmodR6%22%5D%2C%5B%22QFT%E2%80%A010%22%5D%2C%5B%22Chance10%22%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22Chance6%22%5D%5D%2C%22gates%22%3A%5B%7B%22id%22%3A%22~h1nm%22%2C%22name%22%3A%22guess%3A%22%2C%22matrix%22%3A%22%7B%7B1%2C0%2C0%2C0%7D%2C%7B0%2C1%2C0%2C0%7D%2C%7B0%2C0%2C1%2C0%7D%2C%7B0%2C0%2C0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~mdaf%22%2C%22name%22%3A%22input%3A%22%2C%22matrix%22%3A%22%7B%7B1%2C0%2C0%2C0%7D%2C%7B0%2C1%2C0%2C0%7D%2C%7B0%2C0%2C1%2C0%7D%2C%7B0%2C0%2C0%2C1%7D%7D%22%7D%5D%7D) |
| Bimultiply mod R | ![4][4] <br> fig [4][4] | [modular_bimultiplication_rules.py](src/dirty_period_finding/decompositions/modular_bimultiplication_rules.py) | ??? |
| Scaled-Add mod R | ![5][5] <br> fig [5][5] | [modular_scaled_addition_rules.py](src/dirty_period_finding/decompositions/modular_scaled_addition_rules.py) | ??? |
| Double mod R | ![6][6] <br> fig [6][6] | [modular_double_rules.py](src/dirty_period_finding/decompositions/modular_double_rules.py) | [*2%R w/ Effect Display](http://algassert.com/quirk#circuit=%7B%22cols%22%3A%5B%5B%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C1%2C1%2C1%2C1%2C1%2C%22X%22%2C%22Counting4%22%5D%2C%5B%22inputA5%22%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22inputB5%22%2C1%2C1%2C1%2C1%2C%22%5EA%3E%3DB%22%5D%2C%5B%22inputA5%22%2C1%2C1%2C1%2C1%2C%22%2B%3DA5%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22%7C0%E2%9F%A9%E2%9F%A80%7C%22%5D%2C%5B%22~j9d3%22%2C%22~j9d3%22%2C%22~j9d3%22%2C%22~j9d3%22%2C%22~j9d3%22%2C1%2C1%2C1%2C1%2C1%2C%22~4o8m%22%2C%22~4o8m%22%2C%22~4o8m%22%2C%22~4o8m%22%2C%22~4o8m%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22~1bn5%22%2C%22~1bn5%22%2C%22~1bn5%22%2C%22~1bn5%22%2C%22~1bn5%22%2C1%2C1%2C1%2C1%2C1%2C%22%E2%80%A6%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22%E2%80%A6%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22-%3DA5%22%2C1%2C1%2C1%2C1%2C1%2C%22inputA4%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22dec5%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22%2B%3DA4%22%2C1%2C1%2C1%2C%22%E2%80%A2%22%2C1%2C%22inputA4%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22inc4%22%2C1%2C1%2C1%2C%22%E2%80%A2%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22X%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22%3C%3C5%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22%E2%80%A6%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22%E2%80%A6%22%5D%2C%5B1%2C1%2C1%2C1%2C%22~rska%22%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22~4o8m%22%5D%2C%5B%22Amps10%22%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22Chance5%22%5D%5D%2C%22gates%22%3A%5B%7B%22id%22%3A%22~4o8m%22%2C%22name%22%3A%22Mod%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~rska%22%2C%22name%22%3A%22Effect%3A%22%2C%22matrix%22%3A%22%7B%7B1%2C0%2C0%2C0%7D%2C%7B0%2C1%2C0%2C0%7D%2C%7B0%2C0%2C1%2C0%7D%2C%7B0%2C0%2C0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~j9d3%22%2C%22name%22%3A%22In%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~1bn5%22%2C%22name%22%3A%22Out%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%5D%7D) |
| Add mod R | ![8][8] <br> fig [7][7], [8][8], [9][9] | [modular_addition_rules.py](src/dirty_period_finding/decompositions/modular_addition_rules.py) | ??? |
| Pivot-flip | ![10][10] <br> fig [10][10], [11][11] | [pivot_flip_rules.py](src/dirty_period_finding/decompositions/pivot_flip_rules.py) | ??? |
| Add | ![12][12] <br> fig [12][12], [13][13], [14][14], [15][15] | [addition_rules.py](src/dirty_period_finding/decompositions/addition_rules.py) <br> [offset_rules.py](src/dirty_period_finding/decompositions/offset_rules.py) <br> [offset_rules.py](src/dirty_period_finding/decompositions/comparison_rules.py) | ??? |
| Increment | ![17][17] <br> fig [16][16], [17][17] | [increment_rules.py](src/dirty_period_finding/decompositions/increment_rules.py) | ??? |
| No-Ancilla Increment | ![18][18] <br> fig [18][18] | [bootstrap_ancilla_rules.py](src/dirty_period_finding/decompositions/bootstrap_ancilla_rules.py) <br> [phase_gradient_rules.py](src/dirty_period_finding/decompositions/phase_gradient_rules.py) | ??? |
| Rotate Bits | ![19][19] <br> fig [19][19] | [rotate_bits_rules.py](src/dirty_period_finding/decompositions/rotate_bits_rules.py) | ??? |
| Reverse Bits | ![20][20] <br> fig [20][20] | [reverse_bits_rules.py](src/dirty_period_finding/decompositions/reverse_bits_rules.py) | ??? |
| Negate mod R | ??? | [modular_negate_rules.py](src/dirty_period_finding/decompositions/modular_negate_rules.py) | ??? |
| Multi-Not | ??? | [multi_not_rules.py](src/dirty_period_finding/decompositions/multi_not_rules.py) | ??? |

[1]: doc/assets/shor-period-finding.png
[2]: doc/assets/shor-period-finding-solo-phase-qubit.png
[3]: doc/assets/shor-period-finding-solo-phase-qubit-double-register.png
[4]: doc/assets/controlled-modular-multiply.png
[5]: doc/assets/controlled-modular-multiply-accumulate.png
[6]: doc/assets/controlled-modular-double.png
[7]: doc/assets/mod-add-from-pivot-flip-bars.png
[8]: doc/assets/controlled-modular-offset.png
[9]: doc/assets/controlled-modular-offset.png
[10]: doc/assets/controlled-pivot-flip.png
[11]: doc/assets/controlled-const-pivot-flip.png
[12]: doc/assets/inline-adder.png
[13]: doc/assets/offset.png
[14]: doc/assets/inline-adder-into-large.png
[15]: doc/assets/controlled-addition.png
[16]: doc/assets/increment-many-dirty.png
[17]: doc/assets/controlled-increment-odd.png
[18]: doc/assets/ancilla-bootstrap.png
[19]: doc/assets/controlled-bit-rotate.png
[20]: doc/assets/controlled-reverse.png
