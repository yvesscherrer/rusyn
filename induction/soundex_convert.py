#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import csv, sys, os


def convertWord(word, conversions, vowels):
	start = True
	newword = []
	while word != "":
		for c in sorted(conversions, key=lambda x: len(x), reverse=True):
			if word.startswith(c):
				if start:
					newword.append(conversions[c][0])
					start = False
				elif conversions[c][1] == conversions[c][2]:
					if (len(newword) == 0) or (newword[-1] != conversions[c][2]) or (conversions[c][2] == "6"):
						newword.append(conversions[c][2])
				else:
					for v in vowels:
						if word.startswith(c+v):
							if (len(newword) == 0) or (newword[-1] != conversions[c][2]) or (conversions[c][2] == "6"):
								newword.append(conversions[c][1])
							break
					else:
						if (len(newword) == 0) or (newword[-1] != conversions[c][2]) or (conversions[c][2] == "6"):
							newword.append(conversions[c][2])
				word = word[len(c):]
				break
		else:
			print("remove character:", word[0])
			word = word[1:]
	newword2 = "".join(newword)
	return newword2
	

def convertFile(conversionfile, language, inputfile, outputfile):
	print("load conversion table")
	conversions = {}
	f = open(conversionfile, 'r', encoding='utf_16_le')
	r = csv.reader(f, delimiter="\t")
	first = True
	for line in r:
		if first:
			column = line.index(language.upper())
			first = False
		else:
			if (len(line) >= column) and (line[column] != ""):
				conversions[line[column].lower()] = (line[0].replace("N/C", ""), line[1].replace("N/C", ""), line[2].replace("N/C", ""))
	f.close()
	vowels = [x for x in conversions if conversions[x][0] in ("0", "1")]

	for c in sorted(conversions, key=lambda x: len(x), reverse=True):
		print(c, conversions[c])
	print(vowels)
	#sys.exit(0)

	print("load inputfile")
	f = open(inputfile, 'r', encoding='utf-8')
	f2 = open(outputfile, 'w', encoding='utf-8')
	for line in f:
		elements = line.strip().split("\t")
		word = elements[0].replace("́", "").replace("”", "").replace("„", "")
		if (word != "") and (word != "|"):
			if word != elements[0]:
				print(elements[0], "==>", word)
			word2 = convertWord(word.lower(), conversions, vowels)
			if word2 == "":
				print("unconverted:", word)
				f2.write("*" + word + "\t" + line)
			else:
				f2.write(word2 + "\t" + line)
	f.close()
	f2.close()


def test(conversionfile, language, testwords):
	print("load conversion table")
	conversions = {}
	f = open(conversionfile, 'r', encoding='utf_16_le')
	r = csv.reader(f, delimiter="\t")
	first = True
	for line in r:
		if first:
			column = line.index(language.upper())
			first = False
		else:
			if (len(line) >= column) and (line[column] != ""):
				conversions[line[column].lower()] = (line[0].replace("N/C", ""), line[1].replace("N/C", ""), line[2].replace("N/C", ""))
	f.close()
	vowels = [x for x in conversions if conversions[x][0] in ("0", "1")]

	for c in sorted(conversions, key=lambda x: len(x), reverse=True):
		print(c, conversions[c])
	print(vowels)
	
	for word in testwords:
		word2 = convertWord(word.lower(), conversions, vowels)
		if word2 == "":
			print("unconverted:", word)
		else:
			print("==>", word2)


if __name__ == "__main__":
	if "soundex" not in os.listdir("."):
		os.mkdir("soundex")
	convertFile("soundex_daitch_mokotoff_expanded_YS_AR.txt", "cy", "../harmonizeddata/lexicons_mte/pl-mte-cy.txt", "soundex/PL1.txt")
	convertFile("soundex_daitch_mokotoff_expanded_YS_AR.txt", "cy", "../harmonizeddata/lexicons_mte/sk-mte-cy.txt", "soundex/SK1.txt")
	convertFile("soundex_daitch_mokotoff_expanded_YS_AR.txt", "cy", "../harmonizeddata/lexicons_mte/ru-mte.txt", "soundex/RU1.txt")
	convertFile("soundex_daitch_mokotoff_expanded_YS_AR.txt", "cy", "../harmonizeddata/lexicons_mte/ru-tnt.txt", "soundex/RU2.txt")
	convertFile("soundex_daitch_mokotoff_expanded_YS_AR.txt", "cy", "../harmonizeddata/lexicons_mte/uk-mte.txt", "soundex/UK1.txt")
	convertFile("soundex_daitch_mokotoff_expanded_YS_AR.txt", "cy", "../harmonizeddata/lexicons_mte/uk-ugtag.txt", "soundex/UK2.txt")
	convertFile("soundex_daitch_mokotoff_expanded_YS_AR.txt", "cy", "../harmonizeddata/corpus_mte/RUE1000.gold.txt", "soundex/RN1.txt")
	convertFile("soundex_daitch_mokotoff_expanded_YS_AR.txt", "cy", "../harmonizeddata/corpus_ud/RUE80000.txt", "soundex/RN2.txt")
