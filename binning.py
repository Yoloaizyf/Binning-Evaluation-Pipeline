import os
import file_operations


def maxbin_pre(preparation_dir, maxbin_output_dir):
    """
    preparation of maxbin2 command, list of all reads fastq file
    :param preparation_dir: preparation folder
    :param maxbin_output_dir: output folder
    :return: list of all reads fastq file
    """
    file_operations.get_list_file(preparation_dir, "_reads.fq")
    reads_list = os.path.join(maxbin_output_dir, "reads_list.txt")
    return reads_list


def maxbin_pipeline(gsa_file, preparation_dir, project_dir):
    """
    pipeline of run maxbin2
    :param gsa_file: gold standard file
    :param preparation_dir: preparation folder
    :param project_dir:
    """
    file_operations.make_dir("maxbin2_output")
    maxbin_output_dir = os.path.join(project_dir, "maxbin2_output")
    os.chdir(maxbin_output_dir)
    reads_list = maxbin_pre(preparation_dir, maxbin_output_dir)
    maxbin_wd = os.path.join(project_dir, "Using_tools/MaxBin2/")
    command = "%srun_MaxBin.pl -thread 16 -contig %s -reads_list %s -out maxbin" % (maxbin_wd, gsa_file, reads_list)
    os.system(command)
    os.chdir(project_dir)


def create_depth_file(preparation_dir):
    command = "jgi_summarize_bam_contig_depths --outputDepth depth.txt %s/*_sorted.bam" % preparation_dir
    os.system(command)


def metabat_pipeline(gsa_file, preparation_dir, project_dir):
    # jgi_summarize_bam_contig_depths --outputDepth depth.txt *.bam
    # metabat2 -t 16 -i assembly.fasta -a depth.txt -o bins_dir/bin
    file_operations.make_dir("metabat2_output")
    metabat_output_dir = os.path.join(project_dir, "metabat2_output")
    os.chdir(metabat_output_dir)
    create_depth_file(preparation_dir)
    depth_file = os.path.join(metabat_output_dir, "depth.txt")
    command = "metabat2 -i %s -a %s -o metabat2_bins" % (gsa_file, depth_file)
    os.system(command)
    os.chdir(project_dir)


def concoct_pipeline(gsa_file, preparation_dir, project_dir):
    file_operations.make_dir("concoct_output")
    concoct_output_dir = os.path.join(project_dir, "concoct_output")
    concoct_wd = os.path.join(project_dir, "Using_tools/CONCOCT/scripts")
    os.chdir(concoct_output_dir)

    cut_up_fasta = os.path.join(concoct_wd, "cut_up_fasta.py")
    cut_up_command = "%s %s -c 10000 -o 0 --merge_last -b contigs_10K.bed > contigs_10K.fa" % (cut_up_fasta, gsa_file)
    os.system(cut_up_command)

    cov_table = os.path.join(concoct_wd, "concoct_coverage_table.py")
    cov_table_command = "%s contigs_10K.bed %s/*_sorted.bam > coverage_table.tsv" % (cov_table, preparation_dir)
    os.system(cov_table_command)

    concoct_command = "conda run -n concoct_env concoct --composition_file contigs_10K.fa -t 16 " \
                      "--coverage_file coverage_table.tsv"
    os.system(concoct_command)

    cluster = os.path.join(concoct_wd, "merge_cutup_clustering.py")
    cluster_command = "%s clustering_gt1000_s.csv > clustering_merged.csv" % cluster
    os.system(cluster_command)

    file_operations.make_dir("bins")
    bin_dir = os.path.join(concoct_output_dir, "bins")
    extract_bin = os.path.join(concoct_wd, "extract_fasta_bins.py")
    cluster_command = "%s %s clustering_merged.csv --output_path %s" % (extract_bin, gsa_file, bin_dir)
    os.system(cluster_command)

    os.chdir(project_dir)


def binning(gsa_file, preparation_dir, project_dir, binner_list):
    """
    run chosen binners according to the input of parameters.
    :param gsa_file: gold standard file
    :param preparation_dir: preparation folder contains all needed file for binners
    :param project_dir:
    :param binner_list: input choices from users
    """

    # --------------------------------------- MaxBin2 -----------------------------------
    if "maxbin2" in binner_list:
        print("############################## START MAXBIN2 BINNING ##########################")
        maxbin_pipeline(gsa_file, preparation_dir, project_dir)

    # --------------------------------------- MetaBAT2 -----------------------------------
    if "metabat2" in binner_list:
        print("############################## START METABAT2 BINNING ##########################")
        metabat_pipeline(gsa_file, preparation_dir, project_dir)

    # --------------------------------------- CONCOCT -----------------------------------
    if "concoct" in binner_list:
        print("############################## START CONCOCT BINNING ##########################")
        concoct_pipeline(gsa_file, preparation_dir, project_dir)



