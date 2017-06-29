This directory contains the latex source and assets used to generate the paper.


# Producing the PDF

These instructions explain how to produce a pdf from the latex source, on a fresh Ubuntu machine. The example commands have been tested and confirmed to work on Ubuntu 16.10 booted from a live CD.


0. Have [git](https://git-scm.com/) and [texlive](https://www.tug.org/texlive/) installed.

    `sudo add-apt-repository universe`

    `sudo apt-get update`

    `sudo apt-get install --yes git texlive`

0. Clone this repository.

    `git clone https://github.com/Strilanc/PaperImpl-2017-DirtyPeriodFinding.git`

0. Produce `paper.pdf`.

    `cd PaperImpl-2017-DirtyPeriodFinding/doc`

    `pdflatex paper`

    `bibtex paper`

    `pdflatex paper`

    `pdflatex paper`

0. View the output.

    `firefox paper.pdf`
