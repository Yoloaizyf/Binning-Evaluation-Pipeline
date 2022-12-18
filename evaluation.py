import os
import argparse
import sys
import amber_evaluation
import binning


def parse_options():
    parser = argparse.ArgumentParser(description="An Evaluation tool for binning methods. "
                                                 "Compare the quality of binner to existing tools.")

    helptext = "Other binning methods to compare with. Choices: metabat, maxbin2, concoct"
    parser.add_argument("-b", "--binning", type=str, choices=["metabat2", "maxbin2", "concoct"], nargs="+",
                        required=True, help=helptext)

    parser.add_argument("-c", "--compare", type=str, help="path to .binning file of binner to be compared")

    if not len(sys.argv) > 1:
        parser.print_help()
        return None
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_options()
    binner_list = args.binning
    test_bin_path = args.compare

    project_dir = os.path.abspath(os.path.dirname("evaluation.py"))
    preparation_wd = os.path.join(project_dir, "preparations")
    gsa_file = os.path.join(preparation_wd, "anonymous_gsa_pooled.fasta")

    #####################
    # Different Binning methods and their results (Options available)
    # Input: reads of samples
    # Using tool: MaxBin & MetaBAT & CONCOCT
    # Output: each result of different binning tools
    ########################
    print("############################## START BINNING WITH CHOSEN TOOLS ##########################")
    binning.binning(gsa_file, preparation_wd, project_dir, binner_list)
    print("############################## BINNING PROCEDURE FINISHED ##########################")

    #####################
    # AMBER evaluation
    # Input: gold standard file
    # Using tool: AMBER
    # Output: report.html from AMBER
    # Original command:
    #####################
    print("############################## START EVALUATION WITH AMBER ##########################")
    gsa_mapping_file = os.path.join(preparation_wd, "gsa_pooled_mapping.tsv")
    if args.compare:
        amber_evaluation.evaluation(gsa_file, gsa_mapping_file, project_dir, binner_list, test_bin_path)
    else:
        amber_evaluation.evaluation(gsa_file, gsa_mapping_file, project_dir, binner_list)
    print("############################## EVALUATION PROCEDURE FINISHED ##########################")


