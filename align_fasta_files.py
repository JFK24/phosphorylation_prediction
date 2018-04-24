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


import sys
from convert_id import import_ortholog, parse_args_align
from utils import *


def align_file(path, string, file_name, max_window):
    pattern = r"%s" % string
    path2fastas = '%s/fastas' % path
    gene_list = import_ortholog(path, file_name, pattern)
    for gene in gene_list:
        if str(gene._get_code()) in pattern:
            cluster_name = "%s.fasta" % gene._get_cluster()
            path2file = '%s/%s' % (path2fastas, cluster_name)
            score = score_in_window(path2file,
                                    gene, max_window,
                                    pattern)
            print(score)
        # remove_useless_file = "rm %s" % path2file
        # os.system(remove_useless_file)


args = parse_args_align(sys.argv[1:])
align_file(args.path, args.pattern, args.file, args.max_window)