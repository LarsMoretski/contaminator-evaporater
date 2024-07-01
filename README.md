Contaminator-Evaporator is a simple Python script that uses Minimap2 and Samtools to filter out unwanted data by mapping it against a reference genome
Contaminator-Evaporator works on long read data, although Nanopore R10.4 is tested by removing prokaryotic reads from eukaryotic data.
If you suspect that your data is contaminated with reads from another sample, try to predict the best "suitable" contaminant and fetch the fasta file of that genome. 
Contaminator-Evaporator maps all given reads (fastq) against the suspected contaminant's genome and bins reads that are not aligned. The script's output is a .fastq file of the original data without the mapped reads.

To run the script, fetch the script and run it with "python3 filtercontaminants.py [options]"


usage: filtercontaminants.py [-h] --reference REFERENCE --samples SAMPLES [SAMPLES ...] [--threads THREADS]                                                                                     
                                                                                                                                                                                                                                                                                                                              
options:                                                                                                                                                                                              
  -h, --help                                                               show this help message and exit                                                                                                                                               
  --reference REFERENCE                                                    Reference genome file (fasta format)                                                                                                                                          
  --samples SAMPLES [SAMPLES ...]                                          List of sample fastq(.gz) files or directories containing fastq(.gz) files                                                                                                    
  --threads THREADS                                                        Number of threads to use                 
