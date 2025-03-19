#!/usr/bin/env python

"""
Usage:
  tenxval -f <FILE> -m <STR> [-t <INT>]

Options:
  -h, --help                show help.
  -f, --db_file <FILE>      The database file
  -m, --mode <STR>          Database mode (bold, unite, greengenes)
  -t, --threads <INT>       Num of threads [default: 8]
"""

import sys
import os
import re
import gzip
import shutil
from sklearn.model_selection import KFold
from docopt import docopt

from Bio import SeqIO

def check_programs(*programs):
    """Check if program is in path."""
    error_list = []
    for program in programs:
        if not shutil.which(program):
            error_list.append(f"\t[!] {program} not found! Please install and add to it to $PATH")
    if len(error_list)>0:
        print("\n".join(error_list))
        sys.exit()

def open_file(fname):
    """Can open gzip files."""
    if fname.endswith('.gz'):
        return gzip.open(fname, 'rt')
    return open(fname, 'r', encoding = "UTF-8")

def get_outdir(out_directory, add_dir=""):
    """generates output directory in case it does not exist."""
    if type(out_directory) != str:
        print(f"\t[!] {out_directory} is NOT a directory! Please specify an output directory")
        sys.exit()
    elif os.path.isfile(out_directory):
        print(f"\t[!] {out_directory} is a File! Please specify an output directory")
        sys.exit()
    elif not os.path.exists(os.path.join(out_directory, add_dir)):
        os.mkdir(os.path.join(out_directory, add_dir))
        return os.path.abspath(os.path.join(out_directory, add_dir))
    else:
        return os.path.abspath(os.path.join(out_directory, add_dir))


def create_rdp_taxonomy(rdp_data, taxonomy, id_i):
    tax_lineage = {
        "k" : "kingdom",
        "p" : "phylum",
        "c" : "class",
        "o" : "order",
        "f" : "family",
        "g" : "genus",
        "s" : "species"
        }
    #tax_lineage = ["kingdom", "phylum", "class" , "order", "family", "genus", "species"]
    rdp_data_strings = []
    i = 1
    while i < len(taxonomy):
        if taxonomy[i] not in rdp_data:
            id_i += 1
            rdp_data[taxonomy[i]] = {}
            rdp_data[taxonomy[i]]["taxid"] = id_i
            rdp_data[taxonomy[i]]["parentTax"] = rdp_data[taxonomy[i-1]]["taxid"]
            rdp_data[taxonomy[i]]["depth"] = i
            rdp_data[taxonomy[i]]["rank"] = tax_lineage[taxonomy[i].split(":")[0]]
            rdp_data_string = f'{rdp_data[taxonomy[i]]["taxid"]}*{taxonomy[i]}*{rdp_data[taxonomy[i]]["parentTax"]}*{rdp_data[taxonomy[i]]["depth"]}*{rdp_data[taxonomy[i]]["rank"]}'
            rdp_data_strings.append(rdp_data_string)
        i += 1


    return rdp_data, rdp_data_strings, id_i

def main():

    args = docopt(__doc__)
    db_file = args['--db_file']
    mode = args['--mode']
    num_threads = int(args['--threads'])
    k = 10

    # Set rdp_classifier paths for jar and properties
    java_mem = "-Xmx16g"
    classifier_jar_path = "<path/to/classifier.jar>"
    sample_properties_path = "<path/to/rRNAClassifier.properties>"

    check_programs("raxtax", "vsearch", "rdp_classifier")


    ## RDP taxonomy
    if mode == "unite":
        root_species = "k:Fungi"
    elif mode == "bold":
        root_species = "k:Animalia"
    elif mode == "greengenes":
        root_species = "k:Bacteria"
    else:
        sys.exit("No proper mode")

    id_i = 0
    rdp_data = {}
    rdp_data[root_species] = {}
    rdp_data[root_species]["taxid"] = 0
    rdp_data[root_species]["parentTax"] = -1
    rdp_data[root_species]["depth"] = 0
    rdp_data[root_species]["rank"] = "rootrank"

    rdp_data_root_string = f'{rdp_data[root_species]["taxid"]}*{root_species}*{rdp_data[root_species]["parentTax"]}*{rdp_data[root_species]["depth"]}*{rdp_data[root_species]["rank"]}'
    rdp_data_lst = [rdp_data_root_string]

    db_seqs = {}
    db_seqs_tax = {}

    with open_file(db_file) as handle:
        for record in SeqIO.parse(handle, "fasta"):
            seq =str(record.seq).replace("A","1").replace("C","1").replace("G","1").replace("T","1")
            if not re.search('[a-zA-Z]', seq):
                if mode in ('bold', 'greengenes'):
                    seq_id, taxonomy_str = record.id.split(";", 1)
                    taxonomy_str = taxonomy_str.replace("tax=","").replace(";","")
                    kingdom, phylum, class_t, order, family, genus, species =taxonomy_str.split(",")

                    if mode == "bold" and order == "o:":
                        order = "o:Thecostraca_order"
                    taxonomy = [kingdom, phylum, class_t, order, family, genus, species]
                elif mode == "unite":
                    seq_id, taxonomy_str = record.id.rsplit("|", 1)
                    kingdom, phylum, class_t, order, family, genus, species =taxonomy_str.split(";")
                    kingdom = kingdom.replace("k__","k:")
                    phylum = phylum.replace("p__","p:")
                    class_t = class_t.replace("c__","c:")
                    order = order.replace("o__","o:")
                    family = family.replace("f__","f:")
                    genus = genus.replace("g__","g:")
                    species = species.replace("s__","s:")
                    if species.endswith("_sp"):
                        species = ""
                    old_taxonomy = [kingdom, phylum, class_t, order, family, genus, species]
                    inc_string = "Incertae_sedis"
                    changed_taxonomy = ["" if i.endswith(inc_string) else i for i in old_taxonomy]
                    taxonomy = []
                    for tax_r in changed_taxonomy:
                        if tax_r != "":
                            taxonomy.append(tax_r)
                db_seqs[seq_id] = str(record.seq)
                db_seqs_tax[seq_id] = taxonomy
                rdp_data, rdp_data_strings, id_i = create_rdp_taxonomy(rdp_data, taxonomy, id_i)
                for rdp_string in rdp_data_strings:
                    rdp_data_lst.append(rdp_string)


    dir_path = os.getcwd()
    rdp_taxonomy_path = os.path.join(dir_path,"rdp_taxonomy.txt")
    with open(rdp_taxonomy_path, "w", encoding = "UTF-8") as f:
        for rdp_string in rdp_data_lst:
            f.write(rdp_string + "\n")


    keys = list(db_seqs.keys())

    kf = KFold(n_splits = 10, shuffle = True, random_state = 42)

    bash_commands_lst = []

    for i, (train_index, test_index) in enumerate(kf.split(keys)):

        test_path = os.path.join(dir_path, "t" + str(i))
        get_outdir(test_path)

        sintax_file_db_path = os.path.join(test_path, "sin_train_" + str(i) + ".fasta")
        rdp_file_db_path = os.path.join(test_path, "rdp_train_" + str(i) + ".fasta")
        idtaxa_file_db_path = os.path.join(test_path, "idtaxa_train_" + str(i) + ".fasta")


        with (open(sintax_file_db_path, "w", encoding = "UTF-8") as sintax_file_db,
              open(rdp_file_db_path, "w", encoding = "UTF-8") as rdp_file_db,
              open(idtaxa_file_db_path, "w", encoding = "UTF-8") as idtaxa_file_db):
            for k in train_index:
                seq_id = keys[k]
                seq_str = db_seqs[seq_id]
                # Sintax_header + RAxTAx header
                header = seq_id + ";tax=" + ",".join(db_seqs_tax[seq_id]) + ";"
                sintax_file_db.write(">" + header + "\n" + seq_str + "\n")
                # RDP_header + BAYESANT_header
                header = seq_id + " " + ";".join(db_seqs_tax[seq_id])
                rdp_file_db.write(">" + header + "\n" + seq_str + "\n")
                # IDTAXA header
                header = seq_id + " " + "Root;" + ";".join(db_seqs_tax[seq_id])
                idtaxa_file_db.write(">" + header + "\n" + seq_str + "\n")


        test_file_path = os.path.join(test_path, "test_" + str(i) + ".fasta")
        with open(test_file_path, "w", encoding = "UTF-8") as test_file:
            for k in test_index:
                seq_id = keys[k]
                header = seq_id + ";tax=" + ",".join(db_seqs_tax[seq_id]) + ";"
                test_file.write(">" + header + "\n" + db_seqs[seq_id] + "\n")



        #BAYESANT R script
        bayesian_rscript_path = os.path.join(test_path, "bayesant.Rscript")
        bayesant_output_path = os.path.join(test_path, "bayesant.out")
        with open(bayesian_rscript_path, "w", encoding = "UTF-8") as f:
            f.write('library(BayesANT)\n')
            f.write(f'file.train <- file("{rdp_file_db_path}")\n')
            f.write('rank <- 6\n')
            f.write('rank_names <- c( "Phylum", "Class", "Order", "Family", "Genus", "Species")\n')
            f.write('data <- read.BayesANT.data(fasta.file = file.train, rank = rank, rank_names = rank_names)\n')
            f.write('classifier <- BayesANT(data = data, typeseq = "not aligned", type_location = "single", newtaxa = TRUE, verbose = TRUE)\n')
            f.write(f'file.test <- file("{test_file_path}")\n')
            f.write('testDNA <- read.BayesANT.testDNA(file.test)\n')
            f.write('options(max.print = .Machine$integer.max)\n')
            f.write(f'out <- predict(classifier, DNA = testDNA, rho = 0.1, verbose = T, cores = {num_threads})\n')
            f.write(f'sink("{bayesant_output_path}")\n')
            f.write('out\n')
            f.write('sink()\n')
        command = f'Rscript {bayesian_rscript_path}'
        bash_commands_lst.append(command)

        #IDTAXA R script
        idtaxa_rscript_path = os.path.join(test_path, "idtaxa.Rscript")
        idtaxa_output_path = os.path.join(test_path, "idtaxa.out")
        with open(idtaxa_rscript_path, "w", encoding = "UTF-8") as f:
            f.write('library(DECIPHER)\n')
            f.write(f'dna = readDNAStringSet("{idtaxa_file_db_path}",format="fasta")\n')
            f.write('s <- strsplit(names(dna), " ")\n')
            f.write('taxonomy <- sapply(s, `[`, 2)\n')
            f.write('trainingSet <- LearnTaxa(dna, taxonomy)\n')
            f.write(f'test = readDNAStringSet("{test_file_path}",format="fasta")\n')
            f.write(f'ids <- IdTaxa(test,trainingSet, threshold = 1, processors = {num_threads}, strand = "top")\n')
            f.write('options(max.print = .Machine$integer.max)' + "\n")
            f.write(f'sink("{idtaxa_output_path}")\n')
            f.write('print.default(ids)\n')
            f.write('sink()\n')
        command = f'Rscript {idtaxa_rscript_path}'
        bash_commands_lst.append(command)

        # Bash commands
        # RAxTAx
        raxtax_out = os.path.join(test_path, "rx")
        command =  f'raxtax -d {sintax_file_db_path} -i {test_file_path} -o {raxtax_out} -t {num_threads} --redo --tsv'
        bash_commands_lst.append(command)

        # Sintax
        sintax_udb = os.path.join(test_path, "train.udb")
        sintax_out = os.path.join(test_path, "sintax.out")
        command = f'vsearch -makeudb_usearch {sintax_file_db_path} -output {sintax_udb} ; vsearch --sintax {test_file_path} --db {sintax_udb} --tabbedout {sintax_out} --threads {num_threads}'
        bash_commands_lst.append(command)

        # RDP
        rdp_trained_path = os.path.join(test_path, "rdp_trained")
        properties_path = os.path.join(rdp_trained_path, "rRNAClassifier.properties")
        rdp_out = os.path.join(test_path, "rdp.out")
        command = f'java {java_mem} -jar {classifier_jar_path} train -o {rdp_trained_path} -s {rdp_file_db_path} -t {rdp_taxonomy_path} ; cp {sample_properties_path} {rdp_trained_path} ; rdp_classifier {java_mem} -q {test_file_path} -t {properties_path} -o {rdp_out}'
        bash_commands_lst.append(command)

    with open("cmds.sh", "w", encoding = "UTF-8") as f:
        for cmd in bash_commands_lst:
            f.write(f"{cmd}\n")

if __name__ == '__main__':
    main()
