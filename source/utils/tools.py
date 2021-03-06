# This file is part of a program that make prediction of active
# protein phosphorylation sites using machine learning
# Copyright (C) 2018  Zoé Brunet
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import re
from Bio import Alphabet
from Bio import AlignIO
from Bio.Align import AlignInfo
from Bio.Alphabet import IUPAC
from threading import Thread


global hydrophobicity
hydrophobicity = {"A": 0.62, "C": 0.29, "D": -0.90, "E": -0.74, "F": 1.19,
                  "G": 0.48, "H": -0.40, "I": 1.38, "K": -1.50, "L": 1.06,
                  "M": 0.64, "N": -0.78, "P": 0.12, "Q": -0.85, "R": -2.53,
                  "S": -0.18, "T": -0.05, "V": 1.08, "W": 0.81, "Y": 0.26,
                  "Z": -0.79, "B": -0.84, "-": 0}


def function_in_thread(que, args, func):
    t = Thread(target=lambda q, arg: q.put(func(*arg)), args=(que, args[:]))
    t.start()
    t.join()
    result = None
    while not que.empty():
        result = que.get()
    return result


def find_pattern(pattern, seq):
    p = re.compile(pattern)
    result = []
    for m in p.finditer(seq):
        result.append(m)
    return result


def fill_score_table(score, m, align, max_window):
    window_length = m.end() - m.start()
    upper = round((window_length / 2))
    if window_length > 0 & window_length <= max_window:
        for i in range(0, upper + 1):
            coef = (i + 1) / (align.__len__() * window_length)
            if m.start() + i <= m.end() - i - 1:
                score[m.start() + i] += coef
            if m.end() - i - 1 > m.start() + i:
                score[m.end() - i - 1] += coef


def get_align_info(file):
    alpha = Alphabet.Gapped(IUPAC.extended_protein)
    alignment = AlignIO.read(open(file), "fasta", alphabet=alpha)
    return AlignInfo.SummaryInfo(alignment)


def get_pssm(summary_align):
    consensus = summary_align.dumb_consensus()
    my_pssm = summary_align.pos_specific_score_matrix(consensus, chars_to_ignore=['-'])
    return my_pssm
