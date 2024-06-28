## Note that before running this script, minimap2 and samtools have to be installed to path or in a conda environment:
## Creating a conda environment:
## $ conda create -n filterenv
## $ conda activate filterenv
## $ conda install -c bioconda minimap2
## $ conda install -c bioconda samtools

## Input files can be either .fastq or .fastq.gz format and this script works on both single and a subset of files.

import argparse
import subprocess
import os
import gzip
import shutil

def run_command(command):
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')

def gunzip_file(gz_file, output_file):
    with gzip.open(gz_file, 'rb') as f_in:
        with open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def gzip_file(input_file, gz_file):
    with open(input_file, 'rb') as f_in:
        with gzip.open(gz_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def process_sample(reference, sample, threads):
    is_gzipped = sample.endswith('.gz')
    if is_gzipped:
        unzipped_sample = sample.replace('.gz', '')
        print(f"Unzipping {sample}...")
        gunzip_file(sample, unzipped_sample)
    else:
        unzipped_sample = sample

    sample_name = os.path.basename(unzipped_sample).replace('.fastq', '').replace('.fasta', '')

    sam_file = f"{sample_name}.sam"
    bam_file = f"{sample_name}.bam"
    sorted_bam_file = f"{sample_name}_sorted.bam"
    unmapped_bam_file = f"unmapped_{sample_name}.bam"
    unmapped_fastq_file = f"other_{sample_name}.fastq"
    unmapped_gz_file = f"other_{sample_name}.fastq.gz"

    print(f"Running Minimap2 for {sample}...")
    run_command(f"minimap2 -t {threads} -ax map-ont {reference} {unzipped_sample} > {sam_file}")

    print(f"Converting SAM to BAM for {sample}...")
    run_command(f"samtools view -@ {threads} -S -b {sam_file} > {bam_file}")

    print(f"Sorting BAM file for {sample}...")
    run_command(f"samtools sort -@ {threads} {bam_file} -o {sorted_bam_file}")

    print(f"Extracting unmapped reads for {sample}...")
    run_command(f"samtools view -@ {threads} -b -f 4 {sorted_bam_file} > {unmapped_bam_file}")

    print(f"Converting unmapped BAM to FASTQ for {sample}...")
    run_command(f"samtools fastq {unmapped_bam_file} > {unmapped_fastq_file}")

    print(f"Gzipping the output FASTQ for {sample}...")
    gzip_file(unmapped_fastq_file, unmapped_gz_file)

    print(f"Cleaning up intermediate files for {sample}...")
    os.remove(sam_file)
    os.remove(bam_file)
    os.remove(sorted_bam_file)
    os.remove(unmapped_bam_file)
    if is_gzipped:
        os.remove(unzipped_sample)
    os.remove(unmapped_fastq_file)

    print(f"Filtering complete for {sample}. Output file: {unmapped_gz_file}")

def main(reference, samples, threads):
    for sample in samples:
        process_sample(reference, sample, threads)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter contaminants from fasta reads by aligning to a reference genome.')
    parser.add_argument('--reference', required=True, help='Reference genome file (fasta format)')
    parser.add_argument('--samples', required=True, nargs='+', help='List of sample fastq(.gz) files or directories containing fastq(.gz) files')
    parser.add_argument('--threads', type=int, default=1, help='Number of threads to use')

    args = parser.parse_args()
    main(args.reference, args.samples, args.threads)
