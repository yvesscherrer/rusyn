#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os


outfile = open("alltext.txt", 'w', encoding='utf-8')
for fileid in ("pl.train", "pl.dev", "pl.test", "ru1.train", "ru1.dev", "ru1.test", "ru2.train", "ru2.dev", "ru2.test", "sk.train", "sk.dev", "sk.test", "uk.train", "uk.dev", "RUE1000", "RUE80000"):
	infile = open("../../harmonizeddata/corpus_ud/{}.txt".format(fileid), 'r', encoding='utf-8')
	sentence = []
	for line in infile:
		if line.strip() == "":
			outfile.write(" ".join(sentence) + "\n")
			sentence = []
		else:
			elements = line.strip().split("\t")
			if len(elements) > 2:
				sentence.append(elements[1])
			else:
				sentence.append(elements[0])
	if sentence != []:
		outfile.write(" ".join(sentence) + "\n")
	infile.close()
outfile.close()
