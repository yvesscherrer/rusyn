#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import collections

conversions = collections.defaultdict(set)
for lg in ("PL1", "SK1", "RU1", "RU2", "UK1", "UK2"):
	f = open("soundex/{}.txt".format(lg), "r", encoding="utf-8")
	for line in f:
		if line.strip() != "":
			elements = line.split("\t")
			conversions[elements[0]].add("{}:{}:{}:{}".format(lg, elements[1].strip(), elements[2].strip(), elements[3].strip()))
	f.close()


corpus = {}
for testlg in ("RN1", "RN2"):
	f = open("soundex/{}.txt".format(testlg), 'r', encoding='utf-8')
	for line in f:
		elements = line.strip().split("\t")
		if len(elements) < 2:
			continue
		word = elements[1].replace("́", "").replace("”", "").replace("„", "")
		if (word != "") and (word != "|"):
			if word != elements[1]:
				print(elements[1], "==>", word)
			corpus[word.lower()] = elements[0]	# word => soundex
	f.close()

nbAnnotations, nbTokens, nbFoundTokens = 0, 0, 0
f2 = open("soundex.txt", "w", encoding="utf-8")
for word in sorted(corpus):
	conv = conversions[corpus[word]]
	if len(conv) != 0:
		f2.write("{}\t{}\t{}\n".format(word, " ".join(sorted(conv)), corpus[word]))
		nbFoundTokens += 1
	else:
		f2.write("{}\t{}\t{}\n".format(word, "---", corpus[word]))
	nbTokens += 1
	nbAnnotations += len(conv)
f2.close()

print("Tokens:", nbTokens)
print("Found tokens:", nbFoundTokens)
print("Annotations:", nbAnnotations)
print("Annotations per found token:", nbAnnotations/nbFoundTokens)
