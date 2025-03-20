# Context

This repository contains the scripts used for the experimental evaulation of [`raxtax`](https://github.com/noahares/raxtax).
The preprint with the results of these analyses is available at [BioRxiv](https://www.biorxiv.org/content/10.1101/2025.03.11.642618v1).
The databases we used are too big to host them on GitHub.
The files in the `summarized_results` folder were used for creating figures and tables for the manuscript.
To reproduce these results, the databases are available at [Zenodo](https://doi.org/10.5281/zenodo.15057027).

# Resource and Speedup Experiments

All python scripts have `--help` options for arguments.
Plotting scripts will output PDF figures and write tables to stdout.
Install python dependencies via `pip install < requirements.txt`.

## Time and Memory Experiments for Competing Tools

To run one cross validation, place query and reference FASTA files into the desired directory along with:

- bayesant.Rscript
- idtaxa.Rscript
- rRNAClassifier.properties
- rdp_taxonomy.txt (choose from its, gg or bold depending on the database to run)
- run_single_cross_validation.sh

Make sure to name the input files as stated in the scripts or change the names in the script.
The run `./run_single_cross_validation.sh`.

This will produce `*.time.log` files containing the output of `/usr/bin/time -v` for each tool.
For the paper we split each database into 90% references and 10% queries 10 times.

For classification results, see the generated `*.out` files for each tool, respectively.

## Raxtax vs Sintax Scaling Experiments

As a database we use the BOLD database without removing duplicate sequences.
To reproduce the experiments to evaluate the runtime and memory scaling of raxtax and sintax with increasing numbers of sequences run:

```sh
python runtime_memory.py -i database.fasta --raxtax <path/to/raxtax> --sintax <path/to/vsearch> -s 100000 200000 300000 400000 500000 600000 700000 800000 900000 1000000 -r 3 -o <path/to/outputdir>
```

This generates a csv file containing time and memory usage for raxtax and sintax from 100,000 to 1,000,000 sequences (90% references, 10% queries) with 48 threads.

Plotting is done via:

```sh
python plot_runtime_memory.py -i scaling.csv -f SampleSize -y MaxMemoryBytes -o memory.pdf # Memory
python plot_runtime_memory.py -i scaling.csv -f SampleSize -y RuntimeSeconds -o runtime.pdf # Time
```

## Raxtax Parallel Performance

We evaluate strong and weak parallel speedup.
As a database we use the BOLD database with removing duplicate sequences to evaluate real speedups of actual work instead of just hash table lookups for exact matches.

```sh
python speedup.py -i database.fasta --raxtax <path/to/raxtax> --sintax <path/to/vsearch> -f true -w true -t 1 2 4 8 16 24 32 48 -s 250000 -r 5 -o <path/to/outputdir> # weak
python speedup.py -i database.fasta --raxtax <path/to/raxtax> --sintax <path/to/vsearch> -t 1 2 4 8 16 24 32 48 -s 500000 -r 5 -o <path/to/outputdir> # strong
```

Plotting:

```sh
python plot_runtime_memory.py -i weak_tp.csv -f Threads -y RuntimeSeconds -o speedup_weak.pdf # Weak
python plot_runtime_memory.py -i weak_tp.csv -j weak_no_tp.csv -f Threads -y RuntimeSeconds -o speedup_weak.pdf # Weak, compare 2 runs
python plot_runtime_memory.py -i strong.csv -f Threads -y RuntimeSeconds -w -o efficiency_strong.pdf # Strong
```

# 10x Cross Validation (F1 Scores)

## Create 10x cross validation tests
Within `tenxval.py:91ff` set rdp_classifier paths, properties and java memory (optional):
```sh
mkdir unite_test gg_test bold_test
cd unite_test ; tenxval.py -f unite_db.gz -m unite ; cd ..
cd gg_test ; tenxval.py -f greengenes_db.gz -m greengenes ; cd ..
cd bold_test ; tenxval.py -f BOLD_db.gz -m bold ; cd ..
```
This will create a file named cmds.sh within each folder.

## Run cmds.sh

Within each test folder:
```sh
./cmds.sh
```

## Convert all output to tsv

Within each test folder
```sh
results_to_tsv.py -k [kingdom]
```

## Get the ranks present in test/rain and classify them

```sh
present_in_test.py test*fasta sin_train*fasta > present_in_test.txt
for b in *res.tsv ; do binary_classify.pl present_in_test.txt $b > $b.binclass ; done
```

## Calculate stats
Outside the test folders:
```sh
for a in t*/*binclass ; do parse_binary_classify.pl $a f >> plot_toR_family; done
for a in t*/*binclass ; do parse_binary_classify.pl $a g >> plot_toR_genus; done
for a in t*/*binclass ; do parse_binary_classify.pl $a s >> plot_toR_species; done
```
Plotting is done via the R commands from `f1_scores.Rscript` on the respective `plot_toR_*` files.

# Wilcoxon Signed Rank Test

The reported p-values for the Wilcoxon test were generated using `ttest.py plot_toR_*`.
