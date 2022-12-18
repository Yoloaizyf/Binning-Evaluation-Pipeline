import gzip
import os
import shutil
import traceback


def move_file(file, src_path, dst_path):
    """
    move a file from src_path to dst_path
    """
    try:
        file_src = os.path.join(src_path, file)
        if not os.path.exists(dst_path):
            os.mkdir(dst_path)
        file_dst = os.path.join(dst_path, file)
        shutil.move(file_src, file_dst)
    except Exception as e:
        traceback.print_exc()


def move_dir(src_path, dst_path):
    """
    move all files in src_path to dst_path
    """
    filelist = os.listdir(src_path)
    for file in filelist:
        move_file(file, src_path, dst_path)


def make_dir(file):
    """
    check if file already exists before make new folder
    """
    if not os.path.exists(file):
        os.mkdir(file)
    else:
        shutil.rmtree(file)  # removes all the subdirectories!
        os.mkdir(file)


def unzip_gz(file_name):
    """
    unzip .gz file
    """
    f_name = file_name.replace(".gz", "")
    g_file = gzip.GzipFile(file_name)
    open(f_name, "wb+").write(g_file.read())
    g_file.close()
    return f_name


def move_reads_samples(CAMISIM_output_path, preparation_wd):
    """
    move the .fq file of reads in every sample folders to preparation folder.
    :param CAMISIM_output_path:
    :param preparation_wd:
    """
    filelist = os.listdir(CAMISIM_output_path)
    for file in filelist:
        file = os.path.join(CAMISIM_output_path, file)
        split_str = file.split("_")
        if os.path.isdir(file) and "sample" in file:
            reads_dir = os.path.join(file, "reads")
            sample_reads_file = os.path.join(reads_dir, "anonymous_reads.fq.gz")
            unzipped_sample_reads_file = unzip_gz(sample_reads_file)
            newname = "%s%s_reads.fq" % (split_str[-2], split_str[-1])
            newname_file = os.path.join(reads_dir, newname)
            os.rename(unzipped_sample_reads_file, newname_file)
            move_file(newname, reads_dir, preparation_wd)


def batch_operations(filelist, reads_dir, file_str, command, split_point=None, samtools_index=False):
    """
    batch operations in bowtie and samtools step
    :param filelist: all the files that will be operated
    :param reads_dir: folder of generated reads
    :param file_str: file suffixes
    :param command: operations
    :param split_point: need to recognize special files such as *.bam
    :param samtools_index: if it is samtools index step
    """
    split_str = None
    for file in filelist:
        file = os.path.join(reads_dir, file)
        if split_point:
            split_str = file.split(split_point)[-2]
        if os.path.isfile(file) and file_str in file:
            if samtools_index:
                tmp_command = command % file
            else:
                tmp_command = command % (file, split_str)
            os.system(tmp_command)


def get_list_file(reads_dir, file_str):
    """
    generate a text, contains list of all paths of reads file
    :param reads_dir: folder of reads file
    :param file_str: target name
    :return:
    """
    filelist = os.listdir(reads_dir)
    reads_list = open("reads_list.txt", "w")
    for file in filelist:
        file = os.path.join(reads_dir, file)
        if os.path.isfile and file_str in file:
            reads_list.write("%s\n" % file)
    reads_list.close()

















