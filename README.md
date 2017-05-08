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
| Find Period | ![3][3] <br> fig [1][1], [2][2], [3][3] | ??? | [period-find-output][quirk-period-find] |
| Bimultiply mod R | ![4][4] <br> fig [4][4] | [modular_bimultiplication_rules.py](src/dirty_period_finding/decompositions/modular_bimultiplication_rules.py) | ??? |
| Scaled-Add mod R | ![5][5] <br> fig [5][5] | [modular_scaled_addition_rules.py](src/dirty_period_finding/decompositions/modular_scaled_addition_rules.py) | ??? |
| Double mod R | ![6][6] <br> fig [6][6] | [modular_double_rules.py](src/dirty_period_finding/decompositions/modular_double_rules.py) | [double-mod-effect][quirk-double-mod] |
| Add mod R | ![8][8] <br> fig [7][7], [8][8], [9][9] | [modular_addition_rules.py](src/dirty_period_finding/decompositions/modular_addition_rules.py) | ??? |
| Pivot-flip | ![10][10] <br> fig [10][10], [11][11] | [pivot_flip_rules.py](src/dirty_period_finding/decompositions/pivot_flip_rules.py) | ??? |
| Add | ![12][12] <br> fig [12][12], [13][13], [14][14], [15][15] | [addition_rules.py](src/dirty_period_finding/decompositions/addition_rules.py) <br> [offset_rules.py](src/dirty_period_finding/decompositions/offset_rules.py) <br> [comparison_rules.py](src/dirty_period_finding/decompositions/comparison_rules.py) | [big-add-test][quirk-big-add] <br> <br> [control-add-test][quirk-controlled-add] |
| Increment | ![17][17] <br> fig [16][16], [17][17] | [increment_rules.py](src/dirty_period_finding/decompositions/increment_rules.py) | ??? |
| No-Ancilla Increment | ![18][18] <br> fig [18][18] | [bootstrap_ancilla_rules.py](src/dirty_period_finding/decompositions/bootstrap_ancilla_rules.py) <br> [phase_gradient_rules.py](src/dirty_period_finding/decompositions/phase_gradient_rules.py) | [full-increment-test][quirk-bootstrap] |
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
[8]: doc/assets/controlled-modular-addition.png
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
[quirk-double-mod]: http://algassert.com/quirk#circuit=%7B%22cols%22%3A%5B%5B%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C1%2C1%2C1%2C1%2C1%2C%22X%22%2C%22Counting4%22%5D%2C%5B%22inputA5%22%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22inputB5%22%2C1%2C1%2C1%2C1%2C%22%5EA%3E%3DB%22%5D%2C%5B%22inputA5%22%2C1%2C1%2C1%2C1%2C%22%2B%3DA5%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22%7C0%E2%9F%A9%E2%9F%A80%7C%22%5D%2C%5B%22~j9d3%22%2C%22~j9d3%22%2C%22~j9d3%22%2C%22~j9d3%22%2C%22~j9d3%22%2C1%2C1%2C1%2C1%2C1%2C%22~4o8m%22%2C%22~4o8m%22%2C%22~4o8m%22%2C%22~4o8m%22%2C%22~4o8m%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22~1bn5%22%2C%22~1bn5%22%2C%22~1bn5%22%2C%22~1bn5%22%2C%22~1bn5%22%2C1%2C1%2C1%2C1%2C1%2C%22%E2%80%A6%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22%E2%80%A6%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22-%3DA5%22%2C1%2C1%2C1%2C1%2C1%2C%22inputA4%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22dec5%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22%2B%3DA4%22%2C1%2C1%2C1%2C%22%E2%80%A2%22%2C1%2C%22inputA4%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22inc4%22%2C1%2C1%2C1%2C%22%E2%80%A2%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22X%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22%3C%3C5%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22%E2%80%A6%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22%E2%80%A6%22%5D%2C%5B1%2C1%2C1%2C1%2C%22~rska%22%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22~4o8m%22%5D%2C%5B%22Amps10%22%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22Chance5%22%5D%5D%2C%22gates%22%3A%5B%7B%22id%22%3A%22~4o8m%22%2C%22name%22%3A%22Mod%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~rska%22%2C%22name%22%3A%22Effect%3A%22%2C%22matrix%22%3A%22%7B%7B1%2C0%2C0%2C0%7D%2C%7B0%2C1%2C0%2C0%7D%2C%7B0%2C0%2C1%2C0%7D%2C%7B0%2C0%2C0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~j9d3%22%2C%22name%22%3A%22In%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~1bn5%22%2C%22name%22%3A%22Out%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%5D%7D
[quirk-bootstrap]: http://algassert.com/quirk.html#circuit=%7B%22cols%22%3A%5B%5B1%2C1%2C%22~v845%22%2C%22~83kj%22%5D%2C%5B%22Counting7%22%5D%2C%5B%22QFT6%22%5D%2C%5B1%2C1%2C1%2C%22QFT4%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B1%2C%22PhaseGradient6%22%5D%2C%5B%22~ua82%22%2C1%2C1%2C1%2C1%2C1%2C%22Z%5E-%C2%BD%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C%22H%22%5D%2C%5B%22%E2%80%A2%22%2C1%2C1%2C1%2C1%2C1%2C%22X%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C%22Z%5E-%C2%BC%22%5D%2C%5B1%2C%22%E2%80%A2%22%2C%22%E2%80%A2%22%2C%22%E2%80%A2%22%2C%22%E2%80%A2%22%2C%22%E2%80%A2%22%2C%22X%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C%22Z%5E%C2%BC%22%5D%2C%5B%22%E2%80%A2%22%2C1%2C1%2C1%2C1%2C1%2C%22X%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C%22Z%5E-%C2%BC%22%5D%2C%5B1%2C%22%E2%80%A2%22%2C%22%E2%80%A2%22%2C%22%E2%80%A2%22%2C%22%E2%80%A2%22%2C%22%E2%80%A2%22%2C%22X%22%5D%2C%5B%22inc6%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C%22Z%5E%C2%BC%22%5D%2C%5B1%2C%22PhaseUngradient6%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C%22Z%5E%C2%BD%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C%22H%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B%22%E2%80%A6%22%2C1%2C%22~f3fe%22%2C%22~vbq5%22%2C%22~80k%22%5D%2C%5B%22dec7%22%5D%2C%5B1%2C1%2C1%2C%22QFT%E2%80%A04%22%5D%2C%5B%22QFT%E2%80%A06%22%5D%2C%5B%22Uncounting7%22%5D%2C%5B1%2C1%2C%22~suog%22%2C%22~2e7l%22%2C%22~vbq5%22%5D%5D%2C%22gates%22%3A%5B%7B%22id%22%3A%22~mc6d%22%2C%22name%22%3A%22Z%5E2%5E-4%22%2C%22matrix%22%3A%22%7B%7B0.9951847-0.0980171i%2C0%7D%2C%7B0%2C0.9951847%2B0.0980171i%7D%7D%22%7D%2C%7B%22id%22%3A%22~25v0%22%2C%22name%22%3A%22Z%5E2%5E-5%22%2C%22matrix%22%3A%22%7B%7B0.9987955-0.0490677i%2C0%7D%2C%7B0%2C0.9987955%2B0.0490677i%7D%7D%22%7D%2C%7B%22id%22%3A%22~ua82%22%2C%22name%22%3A%22Z%5E2%5E-6%22%2C%22matrix%22%3A%22%7B%7B0.9996988-0.0245412i%2C0%7D%2C%7B0%2C0.9996988%2B0.0245412i%7D%7D%22%7D%2C%7B%22id%22%3A%22~suog%22%2C%22name%22%3A%22Off%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~2e7l%22%2C%22name%22%3A%22Means%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~vbq5%22%2C%22name%22%3A%22Correct%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~v845%22%2C%22name%22%3A%22Test%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~83kj%22%2C%22name%22%3A%22Vecs%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~f3fe%22%2C%22name%22%3A%22Known%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~80k%22%2C%22name%22%3A%22Inverse%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%5D%7D
[quirk-controlled-add]: http://algassert.com/quirk.html#circuit=%7B%22cols%22%3A%5B%5B1%2C1%2C1%2C1%2C%22~fr5t%22%2C%22~m000%22%5D%2C%5B%22Counting11%22%5D%2C%5B%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%5D%2C%5B%22QFT8%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22QFT6%22%5D%2C%5B%22Chance11%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C%22%3C%3C5%22%5D%2C%5B1%2C%22inputA5%22%2C1%2C1%2C1%2C1%2C%22%2B%3DA5%22%5D%2C%5B%22%E2%80%A2%22%2C1%2C1%2C1%2C1%2C1%2C%22X%22%2C%22X%22%2C%22X%22%2C%22X%22%2C%22X%22%5D%2C%5B1%2C%22inputA5%22%2C1%2C1%2C1%2C1%2C%22-%3DA5%22%5D%2C%5B%22%E2%80%A2%22%2C1%2C1%2C1%2C1%2C1%2C%22X%22%2C%22X%22%2C%22X%22%2C%22X%22%2C%22X%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C%22%3E%3E5%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B%22%E2%80%A6%22%2C1%2C1%2C1%2C%22~bg74%22%2C%22~3egi%22%2C%22~vei%22%5D%2C%5B%22%E2%80%A2%22%2C%22inputA5%22%2C1%2C1%2C1%2C1%2C%22-%3DA4%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C%22QFT%E2%80%A06%22%5D%2C%5B%22QFT%E2%80%A08%22%5D%2C%5B%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%5D%2C%5B%22Uncounting11%22%5D%2C%5B1%2C1%2C1%2C1%2C%22~9re4%22%2C%22~fr5l%22%2C%22~3egi%22%5D%5D%2C%22gates%22%3A%5B%7B%22id%22%3A%22~9re4%22%2C%22name%22%3A%22Off%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~fr5l%22%2C%22name%22%3A%22Means%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~3egi%22%2C%22name%22%3A%22Correct%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~bg74%22%2C%22name%22%3A%22Known%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~vei%22%2C%22name%22%3A%22Inverse%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~fr5t%22%2C%22name%22%3A%22Test%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~m000%22%2C%22name%22%3A%22Vecs%22%2C%22matrix%22%3A%22%7B%7B1%2C0%7D%2C%7B0%2C1%7D%7D%22%7D%5D%7D
[quirk-big-add]: http://algassert.com/quirk.html#circuit=%7B%22cols%22%3A%5B%5B%22Counting13%22%5D%2C%5B%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%2C%22Y%5Et%22%5D%2C%5B%22QFT7%22%5D%2C%5B1%2C1%2C1%2C%22QFT10%22%5D%2C%5B%22Chance13%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B1%2C1%2C1%2C1%2C%22%E2%80%A2%22%2C%22dec8%22%5D%2C%5B1%2C1%2C1%2C1%2C%22%E2%80%A2%22%2C1%2C1%2C1%2C1%2C%22inc4%22%5D%2C%5B1%2C1%2C1%2C1%2C%22%E2%80%A2%22%2C%22X%22%5D%2C%5B%22Swap%22%2C1%2C1%2C1%2C%22Swap%22%2C%22%E2%80%A2%22%5D%2C%5B1%2C1%2C1%2C1%2C%22%E2%80%A2%22%2C1%2C%22X%22%5D%2C%5B1%2C%22Swap%22%2C1%2C1%2C%22Swap%22%2C1%2C%22%E2%80%A2%22%5D%2C%5B1%2C1%2C1%2C1%2C%22%E2%80%A2%22%2C1%2C1%2C%22X%22%5D%2C%5B1%2C1%2C%22Swap%22%2C1%2C%22Swap%22%2C1%2C1%2C%22%E2%80%A2%22%5D%2C%5B1%2C1%2C1%2C1%2C%22%E2%80%A2%22%2C1%2C1%2C1%2C%22X%22%5D%2C%5B1%2C1%2C1%2C%22Swap%22%2C%22Swap%22%2C1%2C1%2C1%2C%22%E2%80%A2%22%5D%2C%5B1%2C1%2C1%2C1%2C%22%E2%80%A2%22%2C1%2C1%2C1%2C1%2C%22inc4%22%5D%2C%5B1%2C1%2C1%2C%22Swap%22%2C%22Swap%22%2C1%2C1%2C1%2C%22%E2%80%A2%22%5D%2C%5B1%2C1%2C1%2C%22%E2%80%A2%22%2C1%2C1%2C1%2C1%2C%22X%22%5D%2C%5B1%2C1%2C%22Swap%22%2C1%2C%22Swap%22%2C1%2C1%2C%22%E2%80%A2%22%5D%2C%5B1%2C1%2C%22%E2%80%A2%22%2C1%2C1%2C1%2C1%2C%22X%22%5D%2C%5B1%2C%22Swap%22%2C1%2C1%2C%22Swap%22%2C1%2C%22%E2%80%A2%22%5D%2C%5B1%2C%22%E2%80%A2%22%2C1%2C1%2C1%2C1%2C%22X%22%5D%2C%5B%22Swap%22%2C1%2C1%2C1%2C%22Swap%22%2C%22%E2%80%A2%22%5D%2C%5B%22%E2%80%A2%22%2C1%2C1%2C1%2C1%2C%22X%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B%22%E2%80%A6%22%5D%2C%5B%22inputA5%22%2C1%2C1%2C1%2C1%2C%22-%3DA8%22%5D%2C%5B1%2C1%2C1%2C%22QFT%E2%80%A010%22%5D%2C%5B%22QFT%E2%80%A07%22%5D%2C%5B%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%2C%22Y%5E-t%22%5D%2C%5B%22Uncounting13%22%5D%5D%7D
[quirk-period-find]: http://algassert.com/quirk#circuit=%7B%22cols%22%3A%5B%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22~mdaf%22%2C1%2C1%2C1%2C%22~h1nm%22%5D%2C%5B1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%7B%22id%22%3A%22setR%22%2C%22arg%22%3A55%7D%2C1%2C1%2C1%2C%7B%22id%22%3A%22setB%22%2C%22arg%22%3A26%7D%5D%2C%5B%5D%2C%5B%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22H%22%2C%22X%22%5D%2C%5B%22inputA10%22%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22*BToAmodR6%22%5D%2C%5B%22QFT%E2%80%A010%22%5D%2C%5B%22Chance10%22%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C1%2C%22Chance6%22%5D%5D%2C%22gates%22%3A%5B%7B%22id%22%3A%22~h1nm%22%2C%22name%22%3A%22guess%3A%22%2C%22matrix%22%3A%22%7B%7B1%2C0%2C0%2C0%7D%2C%7B0%2C1%2C0%2C0%7D%2C%7B0%2C0%2C1%2C0%7D%2C%7B0%2C0%2C0%2C1%7D%7D%22%7D%2C%7B%22id%22%3A%22~mdaf%22%2C%22name%22%3A%22input%3A%22%2C%22matrix%22%3A%22%7B%7B1%2C0%2C0%2C0%7D%2C%7B0%2C1%2C0%2C0%7D%2C%7B0%2C0%2C1%2C0%7D%2C%7B0%2C0%2C0%2C1%7D%7D%22%7D%5D%7D
