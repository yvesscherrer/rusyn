#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import collections, sys


def loadLexicon(lexfilename):
	data = collections.defaultdict(set)
	lexfile = open(lexfilename, "r", encoding="utf-8")
	for line in lexfile:
		elements = line.strip().split("\t")
		origword = elements[0]
		if elements[3] == "---":
			continue
		tags = {}
		for x in elements[3].split(" "):
			xelements = x.split(":")
			data[origword].add(xelements[1])
	lexfile.close()
	return data


def transfer(lexfilename, textfilename, outfilename):
	#print(lexfilename, textfilename, "===>", outfilename)
	lexdata = loadLexicon(lexfilename)
	textfile = open(textfilename, "r", encoding="utf-8")
	outfile = open(outfilename, "w", encoding="utf-8")
	for line in textfile:
		if line.strip() == "":
			outfile.write("\n")
		else:
			elements = line.split("\t")
			word = elements[0]
			goldtag = elements[-1].strip()
			if goldtag == "":
				goldtag = "*"
			if word.lower() in lexdata:
				predtags = lexdata[word.lower()]
				outfile.write("{}\t{}\t{}\n".format(word, goldtag, " ".join(sorted(predtags))))
			else:
				outfile.write("{}\t{}\t*\n".format(word, goldtag))
	textfile.close()
	outfile.close()


def unifyTags(t1, t2):
	if t1[0] != t2[0]:
		return False
	for v1, v2 in zip(t1, t2):
		if (v1 != v2) and (v1 != "-") and (v2 != "-"):
			return False
	return True


def evaluate(textfilename):
	total, tagged, induced, correctUnified, correctSubCat, correctMainCat, nbTags = 0, 0, 0, 0, 0, 0, 0
	textfile = open(textfilename, "r", encoding="utf-8")
	for line in textfile:
		if line.strip() == "":
			continue
		elements = line.split("\t")
		origtag = elements[1]
		total += 1
		if origtag[0] == "*":
			continue
		if origtag[0] not in "CIQRXYSNAMPVZ":
			# print("Unknown gold tag:", line.strip())
			continue
		tagged += 1
		if elements[2].strip() == "*":
			continue
		induced += 1
		predtags = elements[2].strip().split(" ")
		nbTags += len(predtags)
		if origtag in predtags:
			correctMainCat += 1
			correctSubCat += 1
			correctUnified += 1
		elif origtag[0] in [x[0] for x in predtags]:
			correctMainCat += 1
			if any([unifyTags((origtag+"-")[:2], (x+"-")[:2]) for x in predtags]):
				correctSubCat += 1
			if any([unifyTags(origtag, x) for x in predtags]):
				correctUnified += 1
	textfile.close()
	print("***", textfilename, "***")
	print("Total tokens:                   {}".format(total))
	print("Tokens with existing tags:      {}".format(tagged))
	print("Tokens with induced tags:       {}  ({:.2f}%)".format(induced, 100*induced/tagged))
	print("Tag matches after unification:  {}  ({:.2f}%)".format(correctUnified, 100*correctUnified/tagged))
	print("Subcategory matches:            {}  ({:.2f}%)".format(correctSubCat, 100*correctSubCat/tagged))
	print("Main category matches:          {}  ({:.2f}%)".format(correctMainCat, 100*correctMainCat/tagged))
	print("Avg number of tags per word:    {:.2f}".format(nbTags/tagged))
	print()


if __name__ == "__main__":
	for exp in ("exact", "levenshtein", "rules", "rules_leven", "leven_rules"):
		transfer("{}.unif.txt".format(exp), "../harmonizeddata/corpus_mte/RUE1000.gold.txt", "{}.transferred.txt".format(exp))
		evaluate("{}.transferred.txt".format(exp))
	