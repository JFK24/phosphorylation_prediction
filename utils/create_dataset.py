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
import ast
from utils.import_csv import *
from utils.score import *
from utils.align_ortholog import *
from utils.window import create_window, find_pos_in_alignment


def create_training_set(string, file, max_window, phospho_ELM=True):
    # Initialisation

    file_name = os.path.basename(file)
    path = "%s/data" % os.path.abspath(os.path.dirname
                                       (os.path.dirname(__file__)))
    pattern = r"%s" % string
    path2fastas = '%s/fastas' % path
    path2align = '%s/align' % path
    path2csv = '%s/csv/%s' % (path, string)

    # Data importation

    index_file = import_ortholog(file, pattern, phospho_ELM)
    genes = pd.read_csv(index_file, sep=';')

    # Creation of csv

    with open('%s/%s_%s_phospho_sites.csv' % (path2csv, file_name[:-4], string),
              'w', newline='') as g:
        writer = csv.writer(g, delimiter=";")

        # Header

        header_freq = ["freq_%s" % i for i in range(0, max_window)]
        header_se = ["shanon_entropy_%s" % i for i in range(0, max_window)]
        writer.writerow((['uniprotID', 'geneID', 'position',
                          'taxID', 'clusterID', 'sequence', 'seq_in_window',
                          'nb_orthologs', 'phosphorylation_site',
                          'ACH_left', 'ACH_right', 'ACH_tot', 'IC_left',
                          'IC_right', 'IC_tot', "metazoa"]
                         + header_freq + header_se))
        length = len(genes)
        gene_seq = genes["sequence"] if phospho_ELM else genes["seq_in_window"]
        gene_pos = zip(genes["pos_sites"], genes["neg_sites"]) if phospho_ELM else genes["pos_sites"]
        for i, (uniprotID, geneID, taxID,
                metazoan, sequence, sites, clusterID) in enumerate(zip(genes["uniprotID"], genes["geneID"],
                                                       genes["taxID"], genes["metazoan"],
                                                       gene_seq, gene_pos, genes["clusterID"])):
            window_seq = None if phospho_ELM else sequence
            if clusterID is not None:
                input = "%s.fasta" % clusterID
                path2input = '%s/%s' % (path2fastas, input)
                path2cluster = "%s/%s.fasta" % (path2fastas, input[:-6])
                path2aligncluster = "%s/%s_align.fasta" % (path2align, input[:-6])

                # align fasta

                pssm = None
                ortholog = False
                if os.path.exists(path2cluster):
                    if not os.path.exists(path2aligncluster):
                        run_muscle(path2input)
                    summary_align = get_align_info(path2aligncluster)
                    pssm = get_pssm(summary_align)
                    ortholog = True

                # fill csv
                phospho_bool = [True, False] if phospho_ELM else [True]
                if not phospho_ELM:
                    sites = [sites]
                for position_list, phosphorylation_site in zip(sites, phospho_bool):
                    for position in ast.literal_eval(position_list):
                        print_trace(i, length, "filling CSV file ")
                        window = create_window(sequence, position, max_window, phospho_ELM)
                        rel_window = []
                        nb_orthologs = 0
                        if not phospho_ELM:
                            sequence = None
                        rel_sequence = sequence
                        if ortholog:
                            with open(path2aligncluster) as f:
                                alpha = Alphabet.Gapped(IUPAC.protein)
                                align = AlignIO.read(f, "fasta", alphabet=alpha)
                                nb_orthologs = align.__len__()
                                if not phospho_ELM:
                                    sequence = find_seq(align, taxID)
                                finder = find_pos_in_alignment(align, sequence, taxID,
                                                               position, phospho_ELM) if phospho_ELM \
                                    else find_pos_in_alignment(align, window_seq, taxID,
                                                               position, phospho_ELM)
                                rel_pos = finder["position"]
                                rel_sequence = finder["sequence"]
                                rel_window = create_window(rel_sequence, rel_pos, max_window, True)

                        # Score orthologs

                        freq = get_freq_of_pattern(pattern, rel_window, path2aligncluster, max_window)
                        shanon_entropy = get_shanon_entropy(rel_window, pssm, max_window)
                        IC = get_information_content(rel_window, path2aligncluster)

                        # Score sequence

                        ACH = get_ACH(window, sequence) if sequence is not None \
                            else get_ACH(create_window(window_seq, 6, 13, phospho_ELM), window_seq)

                        # Fill csv
                        if window_seq is None:
                            window_seq = sequence[window[0][0]: window[1][1] + 1]
                        writer.writerow([uniprotID, geneID, position, taxID, clusterID,
                                         sequence, window_seq, nb_orthologs,
                                         phosphorylation_site, ACH[0], ACH[1], ACH[2], IC[0], IC[1], IC[2],
                                         metazoan] + freq + shanon_entropy)

                        # Print infos

                        if not len(rel_window):
                            rel_window = window
                            rel_sequence = sequence
                        if sequence is None:
                            rel_window = create_window(window_seq, 6, 13, phospho_ELM)
                            rel_sequence = window_seq

                        print("\n\033[31;4mInfo\033[0m :")
                        print("\n\033[;4mUniprotID\033[0m : %s   \033[;4mGeneID\033[0m : %s   "
                              "\033[;4mTaxID\033[0m : %s   \033[;4mPosition\033[0m : %s"
                              "   \033[;4mMetazoa\033[0m : %s   \033[;4mPhosphorylation\033[0m : %s"
                              % (uniprotID, geneID, taxID, position, metazoan, phosphorylation_site))

                        half_window = int((max_window - 1) / 2)
                        space = [20, 5*half_window, 5, 5*half_window]

                        # Print sequence

                        seq_left = (' ' * 4).join(rel_sequence[rel_window[0][0]:
                                                               rel_window[0][1] + 1])+(" " * 4)
                        phospho_site = (' ' * 4).join(rel_sequence[rel_window[0][1] + 1:
                                                                   rel_window[1][0]])+(" " * 4)
                        seq_right = (' ' * 4).join(rel_sequence[rel_window[1][0]:
                                                                rel_window[1][1] + 1]) + (" " * 4)
                        print("\nsequence%s:\033[34m%s\033[0m%s\033[32m%s\033[0m \n "
                              % (" " * (space[0] - len("sequence")), seq_left, phospho_site, seq_right))

                        # Print frequence

                        lamb = lambda n: "nan" if n == "nan" else round(float(n), 1)
                        freq_left = [lamb(element) for element in freq[0: rel_window[0][1] - rel_window[0][0] + 1]]
                        freq_phospho = lamb(freq[rel_window[0][1] - rel_window[0][0] + 1])
                        freq_right = [lamb(element) for element in freq[rel_window[0][1] -
                                                                        rel_window[0][0] + 2: max_window - 1]]
                        print("\033[37mfreq%s:\033[0m\033[34m%s\033[0m, %s ,\033[32m%s\033[0m\n "
                              % (" " * (space[0] - len("freq")),
                                 str(freq_left)[1:-1], str(freq_phospho), str(freq_right)[1:-1]))

                        # Print shanon entropy

                        se_left = [lamb(element) for element in shanon_entropy[0:
                                                                               rel_window[0][1]
                                                                               - rel_window[0][0] + 1]]
                        se_phospho = lamb(shanon_entropy[rel_window[0][1] - rel_window[0][0] + 1])
                        se_right = [lamb(element) for element in shanon_entropy[rel_window[0][1] -
                                                                                rel_window[0][0] + 2:
                                                                                max_window - 1]]
                        print("\033[37mshanon entropy%s:\033[0m\033[34m%s\033[0m, %s, \033[32m%s\033[0m \n "
                              % (" " * (space[0] - len("shanon entropy")), str(se_left)[1:-1],
                                        str(se_phospho), str(se_right)[1:-1]))

                        print("\033[37minformation content :\033[0m\033[34m%s%s\033[0m,%s%s,%s\033[32m%s\033[0m\n "
                              % (" " * (int(space[1] / 2) - 3), lamb(IC[0]), " " * (int(space[1] / 2) - 3),
                                 lamb(IC[2]), " " * (int(space[1] / 2) - 3), lamb(IC[1])))
                        print("ACH%s:\033[34m%s%s\033[0m,%s%s,%s\033[32m%s\033[0m \n "
                              % (" " * (space[0] - len("ACH")),
                                 " " * (int(space[1] / 2) - 3), lamb(ACH[0]), " " * (int(space[1] / 2) - 3),
                                 lamb(ACH[2]), " " * (int(space[1] / 2) - 3), lamb(ACH[1])))
        if phospho_ELM:
            df = pd.read_csv("%s/table_%s_phospho_sites.csv" %(path2csv, string), sep=';')
            df = df[df['phosphorylation_site'] == False]
            for row in df:
                writer.writerow(row)
