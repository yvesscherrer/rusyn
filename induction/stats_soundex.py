#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, collections, unify

# evaluate without recursive unification (takes too long and is not worth the hassle)

def evaluateLexicon(lexiconfile, backuplex, distributionValues=[]):
	results = collections.defaultdict(int)
	uniqueLgFound = collections.defaultdict(int)
	lgFound = collections.defaultdict(int)
	valueDistribution = collections.defaultdict(int)

	f = open(lexiconfile, "r", encoding="utf-8")
	for line in f:
		elements = line.strip().split("\t")
		analyses = elements[1].split(" ")
		results["total"] += 1
		if analyses[0] == "---":
			if elements[0] in backuplex:
				results["found"] += 1
				results["exact"] += 1
				results["nbAmbigLg"] += 1
				results["nbAmbigWord"] += 1
				results["nbAmbigLemma"] += 1
				results["nbAmbigTag1"] += 1
				results["nbAmbigTag2"] += 1
				results["nbAmbigTagExact"] += 1
				results["nbAmbigTagCompat"] += 1
			else:
				results["notfound"] += 1
		else:
			results["found"] += 1
			if (elements[2] == "E") or (elements[2] == "0.0"):
				results["exact"] += 1
			
			# if x contains more than 3 occurrences of :, the word contains a : itself => skip analysis
			analyses2 = [tuple(x.split(":")) for x in analyses if x.count(":") == 3]
			# print(elements[0], analyses2)
			results["nbAmbigLg"] += len(set([x[0][:2] for x in analyses2]))
			results["nbAmbigWord"] += len(set([x[1] for x in analyses2]))
			results["nbAmbigLemma"] += len(set([x[2] for x in analyses2]))
			results["nbAmbigTag1"] += len(set([x[3][0] for x in analyses2]))
			results["nbAmbigTag2"] += len(set([x[3][:2] for x in analyses2]))
			#results["nbAmbigTagExact"] += len(set([x[3] for x in analyses2]))
			tagdict = collections.defaultdict(set)
			for x in analyses2:
				tagdict[x[3]].add(x[0][:2])
			results["nbAmbigTagCompat"] += len(unify.unifySetOfTags(tagdict))
			
			languages = set([x[0][:2] for x in analyses2])
			if len(languages) == 1:
				for l in languages:
					uniqueLgFound[l] += 1
			for l in languages:
				lgFound[l] += 1
		
		if len(distributionValues) > 0:
			dist = float(elements[2].replace("*", ""))
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
	#print("Average tag-exact ambiguity:       {:.2f}".format(results["nbAmbigTagExact"]/results["found"]))
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
	bl = unify.loadBackupLexicon("../harmonizeddata/lexicons_mte/tnt-ru.lex")
	evaluateLexicon("soundex.txt", bl)
	