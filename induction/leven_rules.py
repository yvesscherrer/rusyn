#! /usr/bin/env python
# -*- coding: utf-8 -*-

import foma, codecs, stringdiff


fsm = {"RU1": foma.read_binary("../fomarules/rurulesC.fsm"),
		"RU2": foma.read_binary("../fomarules/rurulesC.fsm"),
		"UK1": foma.read_binary("../fomarules/ukrulesC.fsm"),
		"UK2": foma.read_binary("../fomarules/ukrulesC.fsm"),
		"SK1": foma.read_binary("../fomarules/skrulesC.fsm"),
		"PL1": foma.read_binary("../fomarules/plrulesC.fsm")
	}


def createVowelSensitiveLevenshtein(vowels, vowelWeight):
	insertmap = {v: vowelWeight for v in vowels}
	deletemap = {v: vowelWeight for v in vowels}
	replacemap = {(v1, v2): vowelWeight for v1 in vowels for v2 in vowels if v1 != v2}
	print len(insertmap), len(deletemap), len(replacemap)
	L = stringdiff.LevenshteinCustomWeights(insert_map=insertmap, delete_map=deletemap, replace_map=replacemap)
	return L

L = createVowelSensitiveLevenshtein(u"аеиоуэюяёыіїєьъй'", 0.5)


def findMinimalRelDistanceAfterTransform(origword, candword, lg):
	if lg not in fsm:
		return 1000
	transformedwords = fsm[lg].apply_down(candword.lower())
	minDist = len(origword)
	minWord = u""
	for w in transformedwords:
		if w == origword:
			#print "transformation found", lg, candword, w, origword
			return 0.0
		else:
			leven = L.levenshtein(origword, w, case_sensitive=1, max_distance=minDist+1)
			if leven < minDist:
				minWord = w
				minDist = leven
	#print "dist after transformation", lg, candword, minWord, origword,  minDist / float(len(origword))
	return minDist / float(len(origword))


def filter(lexfilename, outfilename):
	lexfile = codecs.open(lexfilename, "r", "utf-8")
	outfile = codecs.open(outfilename, "w", "utf-8")
	for line in lexfile:
		elements = line.strip().split(u"\t")
		origword = elements[0].replace(u"́", u"").replace(u"”", u"").replace(u"„", u"")
		print origword.encode('utf-8')
		if elements[-1] == "1.0":
			outfile.write(line)
		elif elements[-1] == "0.0":
			outfile.write(line)
		else:
			analyses = [tuple(x.split(u":")) for x in elements[1].split(u" ")]
			words = [x[0:2] for x in analyses]
			if len(set(words)) == 1:
				outfile.write(line)
			else:
				minDist = len(origword)
				minWords = []
				for lg, word in set(words):
					dist = findMinimalRelDistanceAfterTransform(origword, word, lg)
					if dist == minDist:
						minWords.append((lg, word))
					elif dist < minDist:
						minDist = dist
						minWords = [(lg, word)]
				if minWords == []:
					print "No transformation for word:", line.strip().encode('utf-8')
					# this only happens for 4 words of PL2, for which there is no transducer
					outfile.write(line)
				else:
					s = []
					for lg, word in minWords:
						for a in analyses:
							if (a[0] == lg) and (a[1] == word):
								s.append(u"{}:{}:{}:{}".format(lg, word, a[2], a[3]))
					outfile.write(u"{}\t{}\t*{}\n".format(elements[0], " ".join(s), minDist))
	lexfile.close()
	outfile.close()




if __name__ == "__main__":
	filter("levenshtein.txt", "leven_rules.txt")
