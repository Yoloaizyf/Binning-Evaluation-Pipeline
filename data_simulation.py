import os
import argparse
import sys
import CAMISIM_simulation
import coverage
import file_operations


def parse_options():
    parser = argparse.ArgumentParser(description="Fist step of an evaluation tool for binning methods. "
                                                 "Create the common data set and coverage file for binner comparison.")

    helptext = "Taxonomic profile to simulate metagenome data. Biom-format or CAMI-format."
    parser.add_argument("-p", "--profile", help=helptext)

    helptext = "Config file with optional settings."
    parser.add_argument("-c", "--config", help=helptext)

    helptext = "Mapping and coverage value calculation. True/False"
    parser.add_argument("-m", "--mapping", default=False, type=bool, help=helptext)

    if not len(sys.argv) > 1:
        parser.print_help()
        return None
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_options()

    #####################
    # CAMISIM simulation
    # Input: config.ini / tax_profile.biom
    # Using tool: CAMISIM
    # Output: simulated samples & gold standards by CAMISIM
    #####################
    project_dir = os.path.abspath(os.path.dirname("data_simulation.py"))
    camisim_wd = os.path.join(project_dir, "Using_tools/CAMISIM-master")
    CAMISIM_command = CAMISIM_simulation.camisim_simulate(args)
    os.chdir(camisim_wd)
    print("############################## START CAMISIM SIMULATION ##########################")
    os.system(CAMISIM_command)
    os.chdir(project_dir)

    # extract the file that will be needed later to folder CAMISIM_output in current directory ####
    # preparations: storing needed files for mapping from CAMISIM_output
    file_operations.make_dir("preparations")
    preparation_wd = os.path.join(project_dir, "preparations")
    # CAMISIM_output: storing all the output from CAMISIM
    file_operations.make_dir("CAMISIM_output")
    camisim_output_path = os.path.join(project_dir, "CAMISIM_output")
    print("############################## FILE EXTRACTING ##########################")
    CAMISIM_simulation.file_extraction(camisim_wd, camisim_output_path, preparation_wd)

    #######################
    # Mapping with bowtie2 & coverm
    # Input: gold assembly & reads of samples
    # Using tool: bowtie2 & coverm
    # Output: coverage file
    #######################
    gsa_file = os.path.join(preparation_wd, "anonymous_gsa_pooled.fasta")
    if args.mapping:
        print("############################## START MAPPING ##########################")
        coverage.mapping(gsa_file, preparation_wd, project_dir)
        print("############################## COVERAGE CALCULATION FINISHED ##########################")









