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
from Bio import AlignIO
from Bio.Align import AlignInfo
from Bio.Alphabet import IUPAC


def print_trace(i, length, request):
    print("%s %s/%s = %s"
          % (request, str(i + 1), str(length),
             str(round(((i + 1) / length) * 100, 2)) + "%"))


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
    alignment = AlignIO.read(open(file), "fasta", alphabet=IUPAC.extended_protein)
    return AlignInfo.SummaryInfo(alignment)


def get_pssm(summary_align):
    consensus = summary_align.dumb_consensus()
    my_pssm = summary_align.pos_specific_score_matrix(consensus, chars_to_ignore=['-'])
    return my_pssm