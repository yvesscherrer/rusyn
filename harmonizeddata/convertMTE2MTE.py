#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import collections, sys, csv, os


punctuationTag = "Z"
residualTag = "Y"
unknown = collections.defaultdict(int)
changes = collections.defaultdict(int)


def loadCorrespondences(correspondencefile, targetID):
	maxLengths = {}
	correspondences = {}
	cfile = open(correspondencefile, 'r')
	reader = csv.reader(cfile, delimiter=";")
	first = True
	for line in reader:
		if first:
			languages = {name: number for number, name in enumerate(line) if name != "" and number >= 2}
			print(languages, languages[targetID])
			first = False
		elif (line[0] != "") and (line[languages[targetID]] != ""):
			mainCat = line[0]
			target = int(line[languages[targetID]])
			if mainCat not in maxLengths:
				maxLengths[mainCat] = 0
			if target > maxLengths[mainCat]:
				maxLengths[mainCat] = target
			
			for language, index in languages.items():
				if language == targetID:
					continue
				if line[index] == "":
					continue
				if "," in line[index]:
					print("Skip line:", line)
					continue
				if language not in correspondences:
					correspondences[language] = {}
				if mainCat not in correspondences[language]:
					correspondences[language][mainCat] = {}
				correspondences[language][mainCat][int(line[index])] = target
	cfile.close()
	return correspondences, maxLengths


def additionalHarmonization(tag):
	global changes
	s = "".join(tag)
	# an adjective with aspect is a participle (2 Polish occurrences - required for following rule)
	if tag[0] == "A" and tag[1] == "-" and tag[10] in ("p", "e", "a", "b"):
		tag[1] = "p"
	# participles are not adjective forms, but verb forms
	if tag[0] == "A" and tag[1] == "p":
		newtag = ["V", "-", tag[1], tag[12], "-", tag[4], tag[3], tag[11], tag[9], tag[6], "-", tag[5], tag[10], tag[8]]
		tag = newtag
		changes["{} => {}".format(s, "".join(tag))] += 1
	# transgressive => gerund
	if tag[0] == "V" and tag[2] == "t":
		tag[2] = "g"
		changes["{} => {}".format(s, "".join(tag))] += 1
	# relative (ordinal) adjectives => possessive
	if tag[0] == "A" and tag[1] == "o":
		tag[1] = "s"
		changes["{} => {}".format(s, "".join(tag))] += 1
	# gerund nouns should not be annotated as such
	if tag[0] == "N" and tag[1] == "g":
		tag[1] = "c"
		tag[7] = "-"	# aspect and negation should not be annotated
		tag[8] = "-"
		changes["{} => {}".format(s, "".join(tag))] += 1
	# ambivalent => biaspectual
	if tag[0] == "V" and tag[12] == "a":
		tag[12] = "b"
	
	if tag[0] == "A":
		if tag[10] != "-" or tag[11] != "-" or tag[12] != "-":
			print("Residual information to be deleted:", "".join(tag))
		tag = tag[:10]
	elif tag[0] == "N":
		if tag[7] != "-" or tag[8] != "-":
			print("Residual information to be deleted:", "".join(tag))
		tag = tag[:7]
	return tag


def convertTag(tag, lg, correspondences, maxLengths):
	global unknown
	postag = tag[0]
	if postag not in maxLengths:
		return postag
	
	newtag = ["-"] * (maxLengths[postag]+1)
	for position, value in enumerate(tag):
		if position == 0:
			newtag[position] = value
		else:
			if (postag in correspondences[lg]) and (position in correspondences[lg][postag]):
				newposition = correspondences[lg][postag][position]
				newtag[newposition] = tag[position]
			elif value != "-":
				unknown[(lg, postag, position, value)] += 1
	
	if lg == "UK-UGTAG" and tag[0] == "M":
		if (len(tag) > 4) and tag[4] in ("p", "s"):
			#print("Dispatch UK {} as number".format(tag[4]))
			newtag[3] = tag[4]
			unknown[(lg, tag[0], 4, tag[4])] -= 1
		elif (len(tag) > 4) and tag[4] in ("a", "d", "g", "i", "l", "n", "v"):
			#print("Dispatch UK {} as case".format(tag[4]))
			newtag[4] = tag[4]
			unknown[(lg, tag[0], 4, tag[4])] -= 1
	
	newtag2 = additionalHarmonization(newtag)
	return "".join(newtag2)


def convertLexicon(infilename, outfilename, correspondences, maxLengths, language):
	infile = open(infilename, "r", encoding="utf-8")
	outfile = open(outfilename, "w", encoding="utf-8")
	for line in infile:
		elements = line.strip().split("\t")
		if len(elements) < 3:
			print("wrong format:", "||".join(elements))
		word, lemma, tag = elements
		if (tag == ",") or (tag == "SENT") or (tag == "?"):
			newtag = punctuationTag
		else:
			newtag = convertTag(tag, language, correspondences, maxLengths)
		outfile.write("{}\t{}\t{}\n".format(word, lemma, newtag))
	infile.close()
	outfile.close()


def convertCorpus(infilename, outfilename, correspondences, maxLengths, language):
	infile = open(infilename, "r", encoding="utf-8")
	outfile = open(outfilename, "w", encoding="utf-8")
	for line in infile:
		elements = line.split("\t")
		word = elements[0].strip()
		tag = elements[-1].strip()
		if word == "":
			outfile.write("\n")
		elif (tag == ",") or (tag == "SENT") or (tag == "?"):
			outfile.write(word + "\t" + punctuationTag + "\n")
		elif tag == "":
			outfile.write(word + "\tX\n")
		else:
			newtag = convertTag(tag, language, correspondences, maxLengths)
			outfile.write(word + "\t" + newtag + "\n")
	infile.close()
	outfile.close()


def convertTntFiles(infileid, outfileid, correspondences, maxLengths):
	# 123 file
	infile = open(infileid + ".123", "r", encoding="utf-8")
	outfile = open(outfileid + ".123", "w", encoding="utf-8")
	for line in infile:
		if line.startswith("%%"):
			outfile.write(line)
		else:
			elements = line.split("\t")
			newelements = []
			for e in elements[:-1]:
				if e == "":
					newelements.append("")
				elif (e == ",") or (e == "SENT"):
					newelements.append(punctuationTag)
				elif e == "-":
					newelements.append(residualTag)
				else:
					newelements.append(convertTag(e, "RU-TNT", correspondences, maxLengths))
			newelements.append(elements[-1])
			outfile.write("\t".join(newelements))
	infile.close()
	outfile.close()
	
	# lex file
	infile = open(infileid + ".lex", "r", encoding="utf-8")
	outfile = open(outfileid + ".lex", "w", encoding="utf-8")
	for line in infile:
		if line.startswith("%%"):
			outfile.write(line)
		else:
			elements = line.split("\t")
			newelements = [elements[0]]
			for e in elements[1:]:
				e = e.strip()
				if e == "":
					newelements.append("")
				elif e.isnumeric():
					newelements.append(e)
				elif (e == ",") or (e == "SENT"):
					newelements.append(punctuationTag)
				elif e == "-":
					newelements.append(residualTag)
				else:
					newelements.append(convertTag(e, "RU-TNT", correspondences, maxLengths))
			outfile.write("\t".join(newelements) + "\n")
	infile.close()
	outfile.close()


def displayUnknown():
	global unknown
	print("UNKNOWN ASSIGNMENTS:")
	for item in sorted(unknown, key=unknown.get, reverse=True):
		if unknown[item] > 0:
			print(item, unknown[item])
	print ("ADDITIONAL HARMONIZATION:")
	for item in sorted(changes, key=changes.get, reverse=True):
		if changes[item] > 0:
			print(item, changes[item])


if __name__ == "__main__":
	corr, ml = loadCorrespondences("tagcorresp-2017-02.csv", "MTEcompact")
	print(corr)
	print(ml)
	
	if "lexicons_mte" not in os.listdir("."):
		os.mkdir("lexicons_mte")
	if "corpus_mte" not in os.listdir("."):
		os.mkdir("corpus_mte")
	
	convertLexicon("../data/wfl-pl-cyrillic.txt", "lexicons_mte/pl-mte-cy.txt", corr, ml, "PL-MTE")
	convertLexicon("../data/wfl-pl.txt", "lexicons_mte/pl-mte.txt", corr, ml, "PL-MTE")
	convertLexicon("../data/wfl-sk-cyrillic.txt", "lexicons_mte/sk-mte-cy.txt", corr, ml, "SK-MTE")
	convertLexicon("../data/wfl-sk.txt", "lexicons_mte/sk-mte.txt", corr, ml, "SK-MTE")
	convertLexicon("../data/wfl-uk.txt", "lexicons_mte/uk-mte.txt", corr, ml, "UK-MTE")
	convertLexicon("../data/wfl-ru.txt", "lexicons_mte/ru-mte.txt", corr, ml, "RU-MTE")
	convertLexicon("../data/wfl-mte-uk.txt", "lexicons_mte/uk-ugtag-old.txt", corr, ml, "UK-UGTAG")
	convertLexicon("../data/ukdata_2017_01_24/lexicon_reordered.txt", "lexicons_mte/uk-ugtag.txt", corr, ml, "UK-UGTAG")
	convertLexicon("../data/wfl-tnt-ru.txt", "lexicons_mte/ru-tnt.txt", corr, ml, "RU-TNT")
	convertTntFiles("../data/snyat-msd", "lexicons_mte/tnt-ru", corr, ml)
	convertCorpus("../data/rusyndata_2016_12_22/1000tokens_corrected_AR_punctuation_AS_2_YS.txt", "corpus_mte/RUE1000.gold.txt", corr, ml, "RUE")
	convertCorpus("../data/ukdata_2017_01_24/train_reordered.txt", "corpus_mte/uk2.train.txt", corr, ml, "UK-UGTAG")
	
	displayUnknown()
	
