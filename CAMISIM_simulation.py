import os
import file_operations


def camisim_simulate(args):
    # Original command: python metagenome_from_profile.py -c config.ini -p tax_profile.biom
    """
    Using CAMISIM to simulate a data set
    :param args: argparse from the command line.
    profile: input of taxonomic profile that will be given to CAMISIM
    config: input config file to define the parameter of dataset such as sample size or sequencing techs.
    :return: command to run CAMISIM
    """
    if args.profile:
        tax_profile = args.profile
        camisim_command = "python metagenome_from_profile.py -p %s" % tax_profile
    elif args.config:
        config_file = args.config
        camisim_command = "python metagenomesimulation.py -c %s" % config_file
    else:
        camisim_command = None

    return camisim_command


def file_extraction(camisim_wd, camisim_output_path, preparation_wd):
    """
    Extract the file that will be needed later from current project folder to folder CAMISIM_output
    :param camisim_output_path: A folder that store output reads and gsa
    :param preparation_wd: A folder that storing needed files for mapping from CAMISIM_output
    :param camisim_wd: Using_tools/CAMISIM-master
    """
    file_operations.move_dir(camisim_wd + "/out", camisim_output_path)
    # Files for preparations: anonymous_gsa_pooled.fasta.gz (gold standard file) & mapping file
    gsa_name = "anonymous_gsa_pooled.fasta.gz"
    mapping_name = "gsa_pooled_mapping.tsv.gz"
    gsa_unzipped_name = "anonymous_gsa_pooled.fasta"
    mapping_unzipped_name = "gsa_pooled_mapping.tsv"
    gsa_path = os.path.join(camisim_output_path, gsa_name)
    mapping_path = os.path.join(camisim_output_path, mapping_name)

    file_operations.unzip_gz(gsa_path)
    file_operations.move_file(gsa_unzipped_name, camisim_output_path, preparation_wd)
    file_operations.unzip_gz(mapping_path)
    file_operations.move_file(mapping_unzipped_name, camisim_output_path, preparation_wd)

    # Files for preparations: samples/reads/anonymous_reads.fq.gz
    file_operations.move_reads_samples(camisim_output_path, preparation_wd)


