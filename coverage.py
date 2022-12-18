import os
import file_operations
import pandas as pd


def bowtie_build(gsa):
    """
    running command for bowtie2-build gsa_file gsa
    :param gsa: gold standard assembly file
    """
    bowtie_build_command = "bowtie2-build %s gold_assembly" % gsa
    os.system(bowtie_build_command)


def bowtie_sam(reads_dir):
    """
    for each reads sample run command such as
    bowtie2 -q --threads 30 --fr -x gsa --interleaved reads_dir/sample{i}.fq -S sample_${i}.sam
    :param reads_dir: folder of reads samples
    """
    filelist = os.listdir(reads_dir)
    split_point = "."
    file_str = "_reads.fq"
    command = "bowtie2 -q --threads 30 -x gold_assembly --interleaved %s -S %s.sam"
    file_operations.batch_operations(filelist, reads_dir, file_str, command, split_point)


def sam_to_bam(reads_dir):
    """
    for each reads sample run command such as
    samtools view -b sample_${i}.sam -o sample_${i}.bam
    :param reads_dir: folder of reads samples
    """
    filelist = os.listdir(reads_dir)
    split_point = "."
    file_str = ".sam"
    command = "samtools view -b %s -o %s.bam"
    file_operations.batch_operations(filelist, reads_dir, file_str, command, split_point)


def sort_bam(reads_dir):
    """
    for each reads sample run command such as
    samtools sort sample_${i}.bam -o sample_${i}_sorted.bam
    :param reads_dir:  folder of reads samples
    """
    filelist = os.listdir(reads_dir)
    split_point = "."
    file_str = ".bam"
    command = "samtools sort %s -o %s_sorted.bam"
    file_operations.batch_operations(filelist, reads_dir, file_str, command, split_point)


def bam_index(reads_dir):
    """
    for each reads sample run command such as
    samtools index sample_${i}_sorted.bam
    :param reads_dir: folder of reads samples
    """
    filelist = os.listdir(reads_dir)
    file_str = "_sorted.bam"
    command = "samtools index %s"
    file_operations.batch_operations(filelist, reads_dir, file_str, command, samtools_index=True)


def coverm_coverage():
    """
    Using coverm to generate the coverage file
    """
    command = "coverm contig --no-zeros -b *_sorted.bam --output-file coverage_coverm.txt"
    os.system(command)


def calculate_mean_cov(reads_dir):
    """
    Edit coverage file: calculate average value for each column in the file and add it to the first row
    :param reads_dir: folder of reads samples
    """
    coverage_file = os.path.join(reads_dir, "coverage_coverm.txt")
    data = pd.read_csv(coverage_file, sep="\t", encoding="utf8", index_col=0)

    row_name = data.index.tolist()
    row_name.insert(0, "Coverage_Mean")
    data = data.reindex(index=row_name)
    for col in data.columns:
        data[col][0] = data[col].mean()

    data.to_csv("coverage_coverm.txt", sep='\t')


def run_mapping(gsa_file, reads_dir, coverm_dir):
    """
    Running bowtie2 and create *_sorted.bam file of each reads sample, then calculate the coverage.
    :param coverm_dir: coverm output folder
    :param gsa_file: gold standard assembly file created by CAMISIM (path)
    :param reads_dir: folder that contains every reads file. here folder: preparation (path)
    """
    # -------------bowtie2--------------
    bowtie_build(gsa_file)
    bowtie_sam(reads_dir)

    # -------------samtools-------------
    sam_to_bam(reads_dir)
    sort_bam(reads_dir)
    bam_index(reads_dir)

    # --------------coverm--------------
    print("############################## START CALCULATE COVERAGE WITH COVERM ##########################")
    coverm_coverage()

    calculate_mean_cov(reads_dir)
    cov_file = "coverage_coverm.txt"
    file_operations.move_file(cov_file, reads_dir, coverm_dir)


def mapping(gsa_file, preparation_dir, project_dir):
    """
    mapping pipeline
    :param project_dir:
    :param preparation_dir:
    :param gsa_file: gold standard assembly file created by CAMISIM (path)
    """
    file_operations.make_dir("CoverM_output")
    coverm_dir = os.path.join(project_dir, "CoverM_output")

    os.chdir(preparation_dir)
    run_mapping(gsa_file, preparation_dir, coverm_dir)
    os.chdir(project_dir)

