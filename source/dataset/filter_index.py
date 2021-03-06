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
import pandas as pd
from Bio import SeqIO
import os
import csv


def remove_redundancy(index_file, suffix):
    path = os.path.dirname(index_file)
    file_name = "filter_%s" % os.path.basename(index_file)
    path2file = "%s/%s%s.csv" % (path, file_name.split(".")[0], suffix)
    if not os.path.exists(path2file):
        if os.path.exists(index_file):
            genes = pd.read_csv(index_file, sep=';')
            orthologs = set([])
            with open(path2file, 'a+', newline='') as g:
                writer = csv.writer(g, delimiter=";")
                g.seek(0)
                first_char = g.read(1)
                if not first_char:
                    writer.writerow(['uniprotID', 'geneID', 'taxID', 'metazoan', 'code',
                                     'seq_in_window', 'pos_sites', 'clusterID', 'sequence'])
                l = len(genes)
                for i, (uniprotID, geneID, taxID, metazoan, code, \
                    seq_in_window, pos_sites, clusterID, \
                    sequence) in enumerate(zip(genes['uniprotID'], genes['geneID'], genes['taxID'], genes['metazoan'], \
                                               genes['code'], genes['seq_in_window'], genes['pos_sites'], \
                                               genes['clusterID'], genes['sequence'])):
                    print("process %s, %s" % (uniprotID, str(round(((i + 1) / l) * 100, 2)) + "%"))
                    clustername = "%s.fasta" % clusterID
                    path2cluster = "%s/fastas/%s" % (os.path.dirname(os.path.dirname(path)), clustername)
                    if sequence not in orthologs:
                        print("add %s" % uniprotID)
                        writer.writerow([uniprotID, geneID, taxID, metazoan, code,
                                         seq_in_window, pos_sites, clusterID, sequence])
                        if os.path.exists(path2cluster):
                            for record in SeqIO.parse(open(path2cluster), "fasta"):
                                seq = record.seq
                                orthologs.add(seq)
                    else:
                        print("remove %s" % uniprotID)
    return path2file
