#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import re, os, csv, collections


def loadCorrespondences():
	correspondences = {}
	cf = open("tagcorrespUD-2017-02.csv", "r")
	cr = csv.reader(cf, delimiter=";")
	for line in cr:
		postag, position, symbol, _, _, kvpair = line[:6]
		if postag != "":
			correspondences[postag, int(position), symbol] = kvpair
	cf.close()
	return correspondences


maincorrespondences = {"N": "NOUN", "V": "VERB", "A": "ADJ", "P": "PRON", "R": "ADV", "S": "ADP", "C": "CONJ", "M": "NUM", "Q": "PART", "I": "INTJ", "Y": "SYM", "X": "X", "Z": "PUNCT"}
unknown = collections.defaultdict(int)
changes = collections.defaultdict(int)


def convertTag(tag, correspondences, maincorrespondences):
	global unknown, changes
	
	if tag == "":
		return None, None
	elif tag in ("SENT", ",", ":", "?", "!", ";", "-"):
		return "PUNCT", "_"
	else:
		pos = tag[0]
		newmorph = set()
		newpos = ""
		
		if pos in maincorrespondences:
			if pos == "C" and len(tag) > 1 and tag[1] == "s":	# default is CCONJ
				changes["Cs => SCONJ"] += 1
				newpos = "SCONJ"
			elif pos == "N" and len(tag) > 1 and tag[1] == "p":	# default is NOUN
				changes["Np => PROPN"] += 1
				newpos = "PROPN"
			elif pos == "V" and len(tag) > 1 and tag[1] == "a":	# default is VERB
				changes["Va => AUX"] += 1
				newpos = "AUX"
			elif pos == "V" and len(tag) > 1 and tag[1] == "c":	# default is VERB
				changes["Vc => AUX"] += 1
				newpos = "AUX"
			elif pos == "P" and len(tag) > 9 and tag[9] == "r":	# default is PRON
				changes["Pr => ADV"] += 1
				newpos = "ADV"
			elif pos == "P" and len(tag) > 9 and tag[9] == "a":	# default is PRON
				changes["Pa => DET"] += 1
				newpos = "DET"
			else:
				newpos = maincorrespondences[pos]
			
			for index, symbol in enumerate(tag[1:]):
				if (pos, index+1, symbol) in correspondences:
					if "|" in correspondences[pos, index+1, symbol]:
						newmorph.update(set(correspondences[pos, index+1, symbol].split("|")))
					elif correspondences[pos, index+1, symbol] != "":
						newmorph.add(correspondences[pos, index+1, symbol])
					else:
						unknown[(pos, index+1, symbol)] += 1
				elif symbol != "-":
					unknown[(pos, index+1, symbol)] += 1
			
			# PL has three values: Anim (=Hum), Nhum, Inan
			if "Animacy=Hum" in newmorph:
				newmorph.add("Animacy=Anim")
				newmorph.discard("Animacy=Hum")
			if "Animacy=Nhum" in newmorph:
				newmorph.discard("Animacy=Anim")	# Animacy=Nhum should remain
			morphstr = "|".join(sorted(newmorph))
			if morphstr == "":
				morphstr = "_"
			return newpos, morphstr
		else:
			changes["{} (unknown) => X".format(tag)] += 1
			return "X", "_"


def convertLexicon(inputfile, outputfile):
	correspondences = loadCorrespondences()
	f = open(inputfile, 'r', encoding="utf8")
	f2 = open(outputfile, "w", encoding="utf8")
	for line in f:
		elements = line.strip().split("\t")
		token, lemma, tag = elements
		postag, morph = convertTag(tag, correspondences, maincorrespondences)
		if postag != None:
			f2.write("{}\t{}\t{}\t{}\n".format(token, lemma, postag, morph))
	f.close()
	f2.close()


def convertCorpus(inputfilename, outputfilename, rawfilename=""):
	correspondences = loadCorrespondences()
	f = open(inputfilename, 'r', encoding="utf8")
	goldfile = open(outputfilename, "w", encoding="utf8")
	if rawfilename:
		rawfile = open(rawfilename, "w", encoding="utf8")
	wordcount = 1
	for line in f:
		if line.strip() == "":
			goldfile.write("\n")
			if rawfilename:
				rawfile.write("\n")
			wordcount = 1
		else:
			elements = line.split("\t")
			token = elements[0].lower()
			tag = elements[-1].strip()
			postag, morph = convertTag(tag, correspondences, maincorrespondences)
			if postag != None:
				goldfile.write("{}\t{}\t_\t{}\t{}\t{}\t_\t_\t_\t_\n".format(wordcount, token, postag, "{}|{}".format(postag, morph), morph))
				if rawfilename:
					rawfile.write("{}\n".format(token))
				wordcount += 1
	f.close()
	goldfile.close()
	if rawfilename:
		rawfile.close()


def convertInducedLexicon(inputfile, outputfile):
	correspondences = loadCorrespondences()
	lexfile = open(inputfile, "r", encoding="utf-8")
	f2 = open(outputfile, "w", encoding="utf8")
	for line in lexfile:
		elements = line.strip().split("\t")
		origword = elements[0]
		if elements[3] == "---":
			continue
		tags = {}
		for x in elements[3].split(" "):
			xelements = x.split(":")
			if xelements[1] in tags:
				tags[xelements[1]].add(xelements[0])
			else:
				tags[xelements[1]] = set([xelements[0]])
		for t in tags:
			postag, morph = convertTag(t, correspondences, maincorrespondences)
			f2.write("{}\t_\t{}\t{}\n".format(origword, postag, morph))
	lexfile.close()
	f2.close()


def displayUnknown():
	global unknown, changes
	print("Unknown assignments")
	for item in sorted(unknown, key=unknown.get, reverse=True):
		print(item, unknown[item])
	print("Assignment changes")
	for item in sorted(changes, key=changes.get, reverse=True):
		print(item, changes[item])


if __name__ == "__main__":
	# if "lexicons_ud" not in os.listdir("."):
		# os.mkdir("lexicons_ud")
	# for filename in ("pl-mte-cy", "pl-mte", "ru-mte", "ru-tnt", "sk-mte-cy", "sk-mte", "uk-mte", "uk-ugtag-old", "uk-ugtag"):
		# convertLexicon("lexicons_mte/{}.txt".format(filename), "lexicons_ud/{}.txt".format(filename))
	
	# if "corpus_ud" not in os.listdir("."):
		# os.mkdir("corpus_ud")
	# convertCorpus("corpus_mte/RUE1000.gold.txt", "corpus_ud/RUE1000.gold.txt", rawfilename="corpus_ud/RUE1000.txt")
	# convertCorpus("corpus_mte/uk2.train.txt", "corpus_ud/uk2.train.txt")
	
	# if "inducedlexicons_ud" not in os.listdir("."):
		# os.mkdir("inducedlexicons_ud")
	# for id in ("exact", "rules", "levenshtein", "leven_rules", "rules_leven"):
		# convertInducedLexicon("../induction/{}.unif.txt".format(id), "inducedlexicons_ud/{}.txt".format(id))
	convertCorpus("corpus_mte/ukwiki1M.train.txt", "corpus_ud/ukwiki1M.train.txt")
	displayUnknown()

