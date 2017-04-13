#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, collections

id = sys.argv[1]

clusters = collections.defaultdict(set)

for language in ("pl", "ru1", "ru2", "sk", "uk"):
	for corpus in ("train", "dev.gold", "test.gold"):
		if language == "uk" and corpus == "test.gold":
			continue
		f = open("{}.{}.{}.txt".format(id, language, corpus), 'r', encoding='utf-8')
		for line in f:
			if line.strip() == "":
				continue
			elements = line.split("\t")
			c = elements[-1].strip()
			if c != "":
				clusters[language].add(c)
		f.close()

for corpus in ("RUE1000", "RUE80000"):
	f = open("{}.{}.txt".format(id, corpus), 'r', encoding='utf-8')
	for line in f:
		if line.strip() == "":
			continue
		elements = line.split("\t")
		c = elements[-1].strip()
		if c != "":
			clusters["rue"].add(c)
	f.close()

for lg in clusters:
	print(lg, len(clusters[lg]))

for lg1 in clusters:
	monolingual, plurilingual = 0, 0
	for c in clusters[lg1]:
		cInOthers = [c in clusters[lg2] for lg2 in clusters if lg2 != lg1]
		#print(cInOthers)
		exists = any(cInOthers)
		if exists:
			plurilingual += 1
		else:
			monolingual += 1
	print(id, lg1.upper(), monolingual, monolingual+plurilingual, "{:.2f}%".format(100*monolingual/(monolingual+plurilingual)))
