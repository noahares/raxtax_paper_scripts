For details on the scripts used to generate these files, see the `scripts` directory.
The classification outputs are not included in this result directory.
All result files are summaries from the classification outputs and used for creating figures and tables.

# Runtime and Memory Results

`time_memory.csv` contains the results from the single cross validation runs to evaluate time and memory requirements for all tools on different databases.
The time and memory requirements were recorded using `/usr/bin/time -v`.
The results of `bold_diff` are with fixed query and reference sequences from the setup described in the paper.

# No. of Sequences Scaling Results

`scaling.csv` contains results from the scaling experiments comparing raxtax and sintax runtime and memory requirements with different total number of sequences.

# Parallel Scaling Results

`strong_tp.csv` contains results of strong parallel speedup experiments for different thread numbers using thread-pinning.
`weak_tp.csv` contains results of strong parallel speedup experiments for different thread numbers using thread-pinning.
`weak_no_tp.csv` contains results of weak parallel speedup experiments for different thread numbers *without* thread-pinning.

# 10x Cross Valdidation Results

- unite_toR
- gg_toR
- bold_toR
- bold_diff_toR

Contain the F1 scores on Species, Genus and Family level for all Tools on the respective databases.
