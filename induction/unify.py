#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, collections

####### adapted from transfertags/transferTags.py #########

# - collect for each word, a list of (tag, languages) tuples, where languages is a set of all languages that voted for tag
# - first unify inside languages (to account for UK1-UK2 differences, for example)
# - then unify across languages, using the list of tuples as input; when unifying tags from different languages, all languages should be kept
# - (maybe both steps can be done at the same time)
# - take the tag that has the largest associated language list

def unifyTags(t1, t2):
	if t1[0] == t2[0]:
		new = t1[0]
		for pos1, pos2 in zip(t1[1:], t2[1:]):
			if pos1 == pos2:
				new += pos1
			elif pos1 == "-":
				new += pos2
			elif pos2 == "-":
				new += pos1
			elif pos1 != pos2:
				return ""
		return new
	else:
		return ""


def unifySetOfTags(initialTags):
	candidates = {}
	for t1, l1 in initialTags.items():
		found = False
		for t2, l2 in initialTags.items():
			if (t1 != t2) or (l1 != l2):
				result = unifyTags(t1, t2)
				if result:
					if result not in candidates:
						candidates[result] = set()
					candidates[result] |= l1
					candidates[result] |= l2
					#print(t1, t2, "===>", result)
					found = True
		if not found:
			candidates[t1] = l1
	return candidates


def unify(tags):
	previousTags = tags
	unifiedTags = unifySetOfTags(previousTags)
	while unifiedTags != previousTags:
		previousTags = unifiedTags
		unifiedTags = unifySetOfTags(previousTags)
	return unifiedTags


def loadBackupLexicon(lexiconfile):
	data = collections.defaultdict(list)
	infile = open(lexiconfile, "r", encoding="utf-8")
	for line in infile:
		if line.startswith("%%"):
			continue
		elif line.startswith("@"):
			continue
		else:
			elements = line.split("\t")
			word = elements[0]
			tags = []
			for e in elements[1:]:
				e = e.strip()
				if e in ("X", "Y", "Z"):
					tags.append(e)
			if tags != []:
				data[word].extend(tags)
	infile.close()
	return data


def unifyLexicon(infilename, outfilename, backuplex):
	infile = open(infilename, "r", encoding="utf-8")
	outfile = open(outfilename, "w", encoding="utf-8")
	for line in infile:
		words = collections.defaultdict(set)
		lemmas = collections.defaultdict(set)
		tags = collections.defaultdict(set)
		elements = line.strip().split("\t")
		word = elements[0]
		value = elements[-1]
		if len(elements) < 3:
			print("wrong format:", "||".join(elements))
		elif elements[1] == "---":
			if word in backuplex:
				print("Backuplex", word, backuplex[word])
				words[word].add("RU")
				lemmas[word].add("RU")	# lemma is same as word
				for x in backuplex[word]:
					tags[x].add("RU")
				value = "E"
		else:
			analyses = elements[1].split(" ")
			for a in analyses:
				xelements = a.split(":")
				words[xelements[1]].add(xelements[0][:2])
				lemmas[xelements[2]].add(xelements[0][:2])
				tags[xelements[3]].add(xelements[0][:2])
				tags = collections.defaultdict(set, unify(tags))
		
		if words == {}:
			wordstr = "---"
		else:
			wordstr = " ".join(["{}:{}".format(",".join(sorted(words[x])), x) for x in words])
		if lemmas == {}:
			lemmastr = "---"
		else:
			lemmastr = " ".join(["{}:{}".format(",".join(sorted(lemmas[x])), x) for x in lemmas])
		if tags == {}:
			tagstr = "---"
		else:
			tagstr = " ".join(["{}:{}".format(",".join(sorted(tags[x])), x) for x in tags])
		outfile.write(elements[0] + "\t" + wordstr + "\t" + lemmastr + "\t" + tagstr + "\t" + value + "\n")
	infile.close()
	outfile.close()


if __name__ == "__main__":
	bl = loadBackupLexicon("../harmonizeddata/lexicons_mte/tnt-ru.lex")
	
	unifyLexicon("exact.txt", "exact.unif.txt", bl)
	unifyLexicon("levenshtein.txt", "levenshtein.unif.txt", bl)
	unifyLexicon("rules.txt", "rules.unif.txt", bl)
	unifyLexicon("rules_leven.txt", "rules_leven.unif.txt", bl)
	unifyLexicon("leven_rules.txt", "leven_rules.unif.txt", bl)
	# don't unify soundex file with this procedure - is too complex due to lemma/wordform unification
	