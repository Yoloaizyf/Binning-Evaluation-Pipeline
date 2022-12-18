import os
import file_operations
import pandas as pd


def set_gsa_binning(gsa_command, gsa_mapping_file, amber_output_dir):
    """
    create .binning format file of gold standard for AMBER
    :param gsa_command: the command to create a gsa.binning
    :param gsa_mapping_file: mapping file that contains sequence_id and Bin_id
    :param amber_output_dir: output folder of AMBER
    """
    # set up gsa .binning file and mapping and add length
    os.system(gsa_command)
    gsa_binning_file = os.path.join(amber_output_dir, "gsa.binning")

    # set the right BINID
    df = pd.read_table("%s" % gsa_mapping_file)
    map_info = dict(zip(df['#anonymous_contig_id'], df['genome_id']))

    gsa = pd.read_table("%s" % gsa_binning_file, header=3)
    map_list = []
    for id in gsa['@@SEQUENCEID']:
        bin = map_info[id]
        map_list.append(bin)
    gsa['BINID'] = map_list

    table = pd.read_table("%s" % gsa_binning_file, nrows=2)

    column_one = [table.columns[0]]
    column_two = ['', '', '', gsa.columns[1]]

    for i in table[table.columns[0]]:
        column_one.append(i)
    column_one.append(gsa.columns[0])
    for i in gsa[gsa.columns[0]]:
        column_one.append(i)
    for i in gsa[gsa.columns[1]]:
        column_two.append(i)

    mergedf = pd.DataFrame(column_one)
    mergedf = pd.concat((mergedf, pd.DataFrame(column_two, columns=[""])), axis=1)
    mergedf.to_csv("tmp_gsa.csv", index=False, header=False, sep='\t')
    os.rename("tmp_gsa.csv", "tmp_gsa.binning")


def add_gsa_length(gsa_file, add_length_gsa_dir, amber_output_dir):
    """
    add length to gold standard .binning file using function from amber
    :param gsa_file: gold standard file
    :param add_length_gsa_dir: path of add length file of amber
    :param amber_output_dir: output folder of amber
    :return: final gsa.binning file
    """
    # add length
    add_length_command = "%s -g tmp_gsa.binning -f %s >> Goldstandard.binning" % (add_length_gsa_dir, gsa_file)
    os.system(add_length_command)
    os.remove("tmp_gsa.binning")
    os.remove("gsa.binning")
    gsa_binning_file = os.path.join(amber_output_dir, "Goldstandard.binning")
    return gsa_binning_file


def binner_choice(project_dir, convert_dir, binner_list):
    """
    according to what users choose, running correspond binners
    :param project_dir:
    :param convert_dir: path of file to create .binning of amber
    :param binner_list: list contains which binner should be run
    :return: needed .binning file list
    """
    bin_res_list = []
    if "metabat2" in binner_list:
        metabat_output_dir = os.path.join(project_dir, "metabat2_output")
        metabat_convert_command = "%s %s/*.fa -o metabat2_res.binning" % (convert_dir, metabat_output_dir)
        os.system(metabat_convert_command)
        bin_res_list.append("metabat2_res.binning")

    if "maxbin2" in binner_list:
        maxbin_output_dir = os.path.join(project_dir, "maxbin2_output")
        maxbin_convert_command = "%s %s/*.fasta -o maxbin2_res.binning" % (convert_dir, maxbin_output_dir)
        os.system(maxbin_convert_command)
        bin_res_list.append("maxbin2_res.binning")

    if "concoct" in binner_list:
        concoct_output_dir = os.path.join(project_dir, "concoct_output/bins")
        concoct_convert_command = "%s %s/*.fa -o concoct_res.binning" % (convert_dir, concoct_output_dir)
        os.system(concoct_convert_command)
        bin_res_list.append("concoct_res.binning")
    return bin_res_list


def evaluation(gsa_file, gsa_mapping_file, project_dir, binner_list, test_bin_path=None):
    """
    pipeline of amber evaluation
    :param gsa_file: gold standard file
    :param gsa_mapping_file: mapping file that contains sequence_id and Bin_id
    :param project_dir:
    :param binner_list: list contains which binner should be run (from command line)
    :param test_bin_path: path of the .binning file of the binner to be tested
    """
    # first convert all fasta files into .binning file for amber
    file_operations.make_dir("Amber_output")
    amber_output_dir = os.path.join(project_dir, "Amber_output")
    amber_dir = os.path.join(project_dir, "Using_tools/AMBER")
    convert_dir = os.path.join(amber_dir, "src/utils/convert_fasta_bins_to_biobox_format.py")
    add_length_gsa_dir = os.path.join(amber_dir, "src/utils/add_length_column.py")
    evaluation_dir = os.path.join(amber_dir, "amber.py")

    os.chdir(amber_output_dir)
    print("############################## PREPARING FILES ##########################")
    gsa_command = "%s %s -o gsa.binning" % (convert_dir, gsa_file)
    set_gsa_binning(gsa_command, gsa_mapping_file, amber_output_dir)
    gsa_binning_file = add_gsa_length(gsa_file, add_length_gsa_dir, amber_output_dir)

    bin_res_list = binner_choice(project_dir, convert_dir, binner_list)
    if test_bin_path:
        bin_res_list.append(test_bin_path)
        binner_list.append("TEST_BINNER")

    # run evaluation
    print("############################## START EVALUATE ##########################")
    bin_res = " ".join(bin_res_list)
    binner_label = ", ".join(binner_list)
    evaluation_command = "%s --gold_standard_file %s %s --labels '%s' --output_dir AMBER_result" % (evaluation_dir, gsa_binning_file, bin_res, binner_label)
    os.system(evaluation_command)

    os.chdir(project_dir)



