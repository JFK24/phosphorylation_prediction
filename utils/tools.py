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
from biothings_client import get_client
from Bio import Alphabet
from Bio import AlignIO
from Bio import SeqIO
from Bio.Align import AlignInfo
from Bio.Alphabet import IUPAC
import math


global hydrophobicity
hydrophobicity = {"A": 0.62, "C": 0.29, "D": -0.90, "E": -0.74, "F": 1.19,
                  "G": 0.48, "H": -0.40, "I": 1.38, "K": -1.50, "L": 1.06,
                  "M": 0.64, "N": -0.78, "P": 0.12, "Q": -0.85, "R": -2.53,
                  "S": -0.18, "T": -0.05, "V": 1.08, "W": 0.81, "Y": 0.26,
                  "Z": -0.79, "B": -0.84, "-": 0}


def is_metazoan(taxID, mt):
    if not math.isnan(taxID) and taxID is not None:
        info = mt.gettaxon(int(taxID))
        if info is not None:
            if "lineage" in info:
                if 33208 in info["lineage"]:
                    return True
                else:
                    return False
    return "nan"


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
    alpha = Alphabet.Gapped(IUPAC.extended_protein)
    alignment = AlignIO.read(open(file), "fasta", alphabet=alpha)
    return AlignInfo.SummaryInfo(alignment)


def get_pssm(summary_align):
    consensus = summary_align.dumb_consensus()
    my_pssm = summary_align.pos_specific_score_matrix(consensus, chars_to_ignore=['-'])
    return my_pssm


def find_seq(align, taxID):
    for record in align:
        if len(find_pattern(str(taxID), str(record.id))):
            return str(record.seq).replace('-', '')
    return None


def split_fasta(file):
    path2metazoa = "%s_metazoa.fasta" % file[:-6]
    path2nonmetazoa = "%s_non_metazoa.fasta" % file[:-6]
    for record in SeqIO.parse(open(file), "fasta"):
        mt = get_client("taxon")
        position = str(record.id).find(":")
        taxID = record.id[:position]
        metazoa = is_metazoan(float(taxID), mt)
        f_out = path2metazoa if metazoa else path2nonmetazoa
        SeqIO.write([record], open(f_out, 'a'), "fasta")