#!/bin/sh
query=test_0.fasta
db=sin_train_0.fasta
t=48

(/usr/bin/time -v ~/raxtax/target/ultra/raxtax -i $query -d $db -o rx -t $t --pin -qq) &> raxtax.time.log

(/usr/bin/time -v ~/vsearch/bin/vsearch --makeudb_usearch $db --output train.udb) &> sintax_db.time.log
(/usr/bin/time -v ~/vsearch/bin/vsearch --sintax $query --db train.udb --tabbedout sintax.out --threads $t) &> sintax_query.time.log

(/usr/bin/time -v Rscript idtaxa.Rscript) &> idtaxa.time.log

(/usr/bin/time -v Rscript bayesant.Rscript) &> bayesant.time.log

(/usr/bin/time -v java -Xmx64g -jar ~/miniconda3/envs/r_env/share/rdp_classifier-2.14-0/classifier.jar train -o rdp_trained -s rdp_train_0.fasta -t ../rdp_taxonomy.txt) &> rdp_train.time.log
cp rRNAClassifier.properties rdp_trained
(/usr/bin/time -v java -Xmx64g -jar ~/miniconda3/envs/r_env/share/rdp_classifier-2.14-0/classifier.jar -q $query -t rdp_trained/rRNAClassifier.properties -o rdp.out) &> rdp_query.time.log
