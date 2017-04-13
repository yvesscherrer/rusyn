#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, collections


def evaluateLexicon(lexiconfile, distributionValues=[]):
	results = collections.defaultdict(int)
	uniqueLgFound = collections.defaultdict(int)
	lgFound = collections.defaultdict(int)
	valueDistribution = collections.defaultdict(int)

	f = open(lexiconfile, "r", encoding="utf-8")
	for line in f:
		elements = line.strip().split("\t")
		word_fields = elements[1].split(" ")
		lemma_fields = elements[2].split(" ")
		tag_fields = elements[3].split(" ")
		results["total"] += 1
		if tag_fields[0] == "---":
			results["notfound"] += 1
		else:
			results["found"] += 1
			if (elements[-1] == "E") or (elements[-1] == "0.0"):
				results["exact"] += 1
			
			words = [x.rsplit(":", 1)[1] for x in word_fields]
			lemmas = [x.rsplit(":", 1)[1] for x in lemma_fields]
			tags = [x.rsplit(":", 1)[1] for x in tag_fields]
			languages = set([y for x in tag_fields for y in x.rsplit(":", 1)[0].split(",")])
			results["nbAmbigLg"] += len(languages)
			results["nbAmbigWord"] += len(set(words))
			results["nbAmbigLemma"] += len(set(lemmas))
			results["nbAmbigTag1"] += len(set([x[0] for x in tags]))
			results["nbAmbigTag2"] += len(set([x[:2] for x in tags]))
			results["nbAmbigTagCompat"] += len(set(tags))
			
			if len(languages) == 1:
				for l in languages:
					uniqueLgFound[l] += 1
			for l in languages:
				lgFound[l] += 1
		
		if len(distributionValues) > 0:
			dist = float(elements[-1].replace("*", "").replace("E", "0"))
			prevthresh = -1
			for thresh in sorted(distributionValues):
				if (dist <= thresh) and (dist > prevthresh):
					valueDistribution[thresh] += 1
					break
			prevthresh = thresh
	f.close()

	print("*** {} ***".format(lexiconfile))
	print()
	print("Total distinct tokens:  {:>4}".format(results["total"]))
	print("Unmatched tokens:       {:>4}  ({:>5.2f}%)".format(results["notfound"], 100*results["notfound"]/results["total"]))
	print("Matched tokens:         {:>4}  ({:>5.2f}%)".format(results["found"], 100*results["found"]/results["total"]))
	print("Exact matches:          {:>4}  ({:>5.2f}%)".format(results["exact"], 100*results["exact"]/results["total"]))
	print()
	print("Average src language ambiguity:    {:.2f}".format(results["nbAmbigLg"]/results["found"]))
	print("Average word ambiguity:            {:.2f}".format(results["nbAmbigWord"]/results["found"]))
	print("Average lemma ambiguity:           {:.2f}".format(results["nbAmbigLemma"]/results["found"]))
	print("Average tag-1 ambiguity:           {:.2f}".format(results["nbAmbigTag1"]/results["found"]))
	print("Average tag-2 ambiguity:           {:.2f}".format(results["nbAmbigTag2"]/results["found"]))
	print("Average tag-compat ambiguity:      {:.2f}".format(results["nbAmbigTagCompat"]/results["found"]))
	print()
	for l in sorted(lgFound):
		print("Words induced from {}:            {:>4}  ({:>5.2f}%)  ({:>5.2f}%)".format(l, lgFound[l], 100*lgFound[l]/results["found"], 100*lgFound[l]/results["total"]))
		print("Words uniquely induced from {}:   {:>4}  ({:>5.2f}%)  ({:>5.2f}%)".format(l, uniqueLgFound[l], 100*uniqueLgFound[l]/results["found"], 100*uniqueLgFound[l]/results["total"]))
	print()
	for thresh in sorted(valueDistribution):
		print("Matched tokens with distance <= {:>4}:    {:>5.2f}%".format(thresh, 100*valueDistribution[thresh]/results["found"]))
	print()

if __name__ == "__main__":
	evaluateLexicon("exact.unif.txt")
	#evaluateLexicon("soundex.unif.txt")
	evaluateLexicon("levenshtein.unif.txt", [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 1])
	evaluateLexicon("rules.unif.txt")
	evaluateLexicon("rules_leven.unif.txt")
	evaluateLexicon("leven_rules.unif.txt", [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 1])
	