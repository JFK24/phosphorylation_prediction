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
import os
import pandas as pd


def enrich_csv(file1, file2):
    a = pd.read_csv(file1, sep=";")
    b = pd.read_csv(file2, sep=";")
    b = b.dropna(axis=1)
    merged = a.merge(b, on=['uniprotID', 'position'])
    name = '%s/%s+%s.csv' % (os.path.dirname(file1),
                             os.path.basename(file1)[:-4],
                             os.path.basename(file2)[:-4])
    merged.to_csv(name, index=False, sep=';')
    return name