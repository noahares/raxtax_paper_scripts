#!/usr/bin/env python

import sys
from Bio import SeqIO

file_test = sys.argv[1]
file_train = sys.argv[2]

rank = {}

with open(file_test) as handle:
	for record in SeqIO.parse(handle, "fasta"):
		header_lst = record.id.split("=")
		ranks = header_lst[1].split(",")
		for rankt in ranks:
			rankt = rankt.replace(";","")
			rank[rankt] = 0


with open(file_train) as handle:
	for record in SeqIO.parse(handle, "fasta"):
		header_lst = record.id.split("=")
		ranks = header_lst[1].split(",")
		for rankt in ranks:
			rankt = rankt.replace(";","")
			if rankt in rank:
				rank[rankt] += 1

for r in rank:
	print(r + "\t" + str(rank[r]))