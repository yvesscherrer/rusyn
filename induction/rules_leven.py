#! /usr/bin/env python3
# -*- coding: utf-8 -*-


levenfile = open("levenshtein.txt", "r", encoding="utf-8")
rulesfile = open("rules.txt", "r", encoding="utf-8")
outfile = open("rules_leven.txt", "w", encoding="utf-8")
levenline = levenfile.readline()
rulesline = rulesfile.readline()

while levenline and rulesline:
	leven = levenline.strip().split("\t")
	rules = rulesline.strip().split("\t")
	if leven[0] != rules[0]:
		rulesline = rulesfile.readline()
		rules = rulesline.strip().split("\t")
	
	if rules[-1] == "T":
		outfile.write(rulesline)
	elif rules[-1] == "E":
		outfile.write(rulesline)
	else:
		outfile.write(levenline)
	
	levenline = levenfile.readline()
	rulesline = rulesfile.readline()

levenfile.close()
rulesfile.close()
outfile.close()
