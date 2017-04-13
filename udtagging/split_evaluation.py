#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, collections


def evaluate(goldfilename, sysfilename, goldtokenpos=1, goldtagpos=3, goldmorphpos=5, systokenpos=1, systagpos=5, sysmorphpos=7, lenient=False):
	results = collections.defaultdict(int)
	goldfile = open(goldfilename, 'r', encoding="utf-8")
	sysfile = open(sysfilename, 'r', encoding="utf-8")
	sentenceNumber = 0
	for goldline in goldfile:
		if goldline.startswith("#"):
			continue
		if goldline.strip() == "":
			sentenceNumber += 1
			continue
		sysline = sysfile.readline()
		while sysline.startswith("#") or sysline.strip() == "":
			sysline = sysfile.readline()
		split = 1 if sentenceNumber % 2 == 0 else 2

		goldelem = goldline.strip().split("\t")
		syselem = sysline.strip().split("\t")
		if goldelem[goldtokenpos] != syselem[systokenpos]:
			print("Word mismatch:", goldelem[goldtokenpos], syselem[systokenpos])
			continue
		else:
			results["comparedTokens{}".format(split)] += 1
			if goldtagpos == goldmorphpos:
				goldtag = goldelem[goldtagpos].split("|")[0]
				goldmorph = goldelem[goldtagpos].split("|")[1:]
			else:
				goldtag = goldelem[goldtagpos]
				goldmorph = goldelem[goldmorphpos].split("|")
			if goldmorph == ["_"]:
				goldmorph = {}
			else:
				goldmorph = {x.split("=")[0]: x.split("=")[1] for x in goldmorph}
			
			if systagpos == sysmorphpos:
				systag = syselem[systagpos].split("|")[0]
				sysmorph = syselem[sysmorphpos].split("|")[1:]
			else:
				systag = syselem[systagpos]
				sysmorph = syselem[sysmorphpos].split("|")
			if sysmorph == ["_"]:
				sysmorph = {}
			else:
				sysmorph = {x.split("=")[0]: x.split("=")[1] for x in sysmorph}
			
			if (goldtag == systag) or (lenient and ((goldtag, systag) in [("VERB", "AUX"), ("NOUN", "PROPN"), ("CONJ", "SCONJ")])):
				results["PosCorrect{}".format(split)] += 1
				if len(goldmorph) > 0:
					results["comparedMorph{}".format(split)] += 1
					notpredicted, predictionerror, correct = 0, 0, 0
					for k in goldmorph:
						if k not in sysmorph:
							notpredicted += 1
						elif goldmorph[k] != sysmorph[k]:
							predictionerror += 1
						else:
							correct += 1
					if predictionerror == 0:
						results["PosMorphCorrect{}".format(split)] += 1
				else:
					results["PosMorphCorrect{}".format(split)] += 1
	goldfile.close()
	sysfile.close()
	return results



rf = open("results_split.txt", 'w')
row = ["CONFIG", "Tokens", "PosCorrect", "%", "PosMorphCorrect", "%", "CorrectMorphRatio1", "CorrectMorphRatio2"]
rf.write("\t".join(row) + "\n")

for fileid in sorted(os.listdir("output")):
	if "RUE1000" not in fileid:
		continue
	if "brown_token" in fileid:
		continue
	res = evaluate("{}/{}.gold.txt".format("../harmonizeddata/corpus_ud", "RUE1000"), "{}/{}".format("output", fileid), lenient=True)
	for split in (1, 2):
		row = ["{} - {}".format(fileid.upper(), split), "{}".format(res["comparedTokens{}".format(split)]), "{}".format(res["PosCorrect{}".format(split)]), "{:.2f}%".format(100*res["PosCorrect{}".format(split)]/res["comparedTokens{}".format(split)]), "{}".format(res["PosMorphCorrect{}".format(split)]), "{:.2f}%".format(100*res["PosMorphCorrect{}".format(split)]/res["comparedTokens{}".format(split)])]
		rf.write("\t".join(row) + "\n")
	p1 = abs((100*res["PosCorrect1"]/res["comparedTokens1"]) - (100*res["PosCorrect2"]/res["comparedTokens2"]))
	p2 = abs((100*res["PosMorphCorrect1"]/res["comparedTokens1"]) - (100*res["PosMorphCorrect2"]/res["comparedTokens2"]))
	row = ["{} - diff".format(fileid.upper()), "", "{:.2f}%".format(p1), "", "{:.2f}%".format(p2)]
	rf.write("\t".join(row) + "\n")

rf.close()
