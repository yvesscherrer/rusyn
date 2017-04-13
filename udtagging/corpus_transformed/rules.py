#! /usr/bin/python
# -*- coding: utf-8 -*-

import foma, codecs, collections, multiprocessing, os, sys, random

corpusdir = "../../harmonizeddata/corpus_ud"
lexicondir = "../../harmonizeddata/lexicons_ud"
transducerdir = "../../fomarules"
transducers = {x: foma.read_binary("{}/{}rulesC.fsm".format(transducerdir, x)) for x in ("ru", "uk", "sk", "pl")}


def convert(data):
	global rusynWords
	word, lg = data
	
	if word in rusynWords:
		return word, [word], 0
	elif len(word) > 25:
		return word, [], -1
	else:
		transformations = transducers[lg].apply_down(word)
		transformations = [x for x in transformations if x in rusynWords]
		if transformations == []:
			return word, [], -1
		else:
			return word, transformations, 1


def loadRusynWords():
	global rusynWords
	rusynWords = collections.defaultdict(int)
	f = codecs.open("{}/RUE80000.txt".format(corpusdir), "r", "utf-8")
	for line in f:
		word = line.strip().lower()
		rusynWords[word] += 1
	f.close()
	f = codecs.open("{}/RUE1000.txt".format(corpusdir), "r", "utf-8")
	for line in f:
		word = line.strip().lower()
		rusynWords[word] += 1
	f.close()


def loadRLWords(corpusid):
	global rlWords
	f = codecs.open("{}/{}.txt".format(corpusdir, corpusid), "r", "utf-8")
	for line in f:
		if line.startswith("#"):
			continue
		elif line.strip() == "":
			continue
		else:
			elements = line.strip().split("\t")
			rlWords.add(elements[1])


def loadRLDict(dictid):
	global rlWords
	f = codecs.open("{}/{}.txt".format(lexicondir, dictid), "r", "utf-8")
	for line in f:
		if line.startswith("#"):
			continue
		elif line.strip() == "":
			continue
		else:
			elements = line.strip().split("\t")
			rlWords.add(elements[0].lower())


def filterResults(d):
	d2 = d.copy()
	for rlword1 in d:
		for rlword2 in d2:
			if rlword1 == rlword2:
				continue
			if d2[rlword2][1] < d[rlword1][1]:
				for x in d2[rlword2][0]:
					if x in d[rlword1][0]:
						d[rlword1][0].remove(x)
	return d

	
def convertMulti(corpusid, outid, nbThreads, filter=False, randomSelect=False, dictid=None):
	print "load data"
	loadRusynWords()
	global rlWords
	rlWords = set()
	loadRLWords(corpusid)
	if dictid:
		loadRLDict(dictid)
	rlWords = [(w, corpusid[:2]) for w in rlWords]
	stats = collections.defaultdict(int)
	
	if nbThreads > 1:
		print "launch multiprocessing"
		pool = multiprocessing.Pool(processes=nbThreads)
		results = pool.map(convert, rlWords)
	else:
		results = [convert(word_lg) for word_lg in rlWords]
	results = {x[0]: (x[1], x[2]) for x in results}

	if filter:
		print "filtering results"
		results = filterResults(results)
		
	stats["analyzedTypes"] = len(results)
	stats["identicalTypes"] = len([x for x in results if results[x][1] == 0])
	stats["differentTypes"] = len([x for x in results if results[x][1] > 0])
	
	print "write results to file"
	f = codecs.open("{}/{}.txt".format(corpusdir, corpusid), "r", "utf-8")
	of = codecs.open("{}.{}.txt".format(outid, corpusid), "w", "utf-8")
	for line in f:
		if line.startswith("#"):
			of.write(line)
		elif line.strip() == "":
			of.write(line)
		else:
			stats["analyzedTokens"] += 1
			elements = line.strip().split("\t")
			bestCandidates, bestDistance = results[elements[1]]
			if len(bestCandidates) == 0:	# happens if all candidates are filtered away
				of.write(line)
			elif bestDistance == 0:
				stats["identicalTokens"] += 1
				of.write(line)
			elif bestDistance > 0:
				stats["differentTokens"] += 1
				if len(bestCandidates) == 1:
					stats["changedTokens"] += 1
					print elements[1].encode('utf-8'), "===>", bestCandidates[0].encode('utf-8'), bestDistance
					of.write("\t".join([elements[0], bestCandidates[0]] + elements[2:]) + "\n")
				elif randomSelect:
					stats["changedTokens"] += 1
					bestCandidate = random.choice(bestCandidates)
					print elements[1].encode('utf-8'), "===>", bestCandidate.encode('utf-8'), "(selected from {})".format(len(bestCandidates)), bestDistance
					of.write("\t".join([elements[0], bestCandidate] + elements[2:]) + "\n")
				else:
					of.write(line)
			else:
				of.write(line)
	f.close()
	of.close()
	
	if dictid:
		print "write lexicon results to file"
		f = codecs.open("{}/{}.txt".format(lexicondir, dictid), "r", "utf-8")
		of = codecs.open("{}.{}.txt".format(outid, dictid), "w", "utf-8")
		for line in f:
			if line.startswith("#"):
				of.write(line)
			elif line.strip() == "":
				of.write(line)
			else:
				stats["analyzedDictTokens"] += 1
				elements = line.strip().split("\t")
				bestCandidates, bestDistance = results[elements[0]]
				if len(bestCandidates) == 0:	# happens if all candidates are filtered away
					of.write(line)
				elif bestDistance == 0:
					stats["identicalDictTokens"] += 1
					of.write(line)
				elif bestDistance > 0:
					stats["differentDictTokens"] += 1
					if len(bestCandidates) == 1:
						stats["changedDictTokens"] += 1
						print elements[0].encode('utf-8'), "===>", bestCandidates[0].encode('utf-8'), bestDistance
						of.write("\t".join([bestCandidates[0]] + elements[1:]) + "\n")
					elif randomSelect:
						stats["changedDictTokens"] += 1
						bestCandidate = random.choice(bestCandidates)
						print elements[0].encode('utf-8'), "===>", bestCandidate.encode('utf-8'), "(selected from {})".format(len(bestCandidates)), bestDistance
						of.write("\t".join([bestCandidate] + elements[1:]) + "\n")
					else:
						of.write(line)
				else:
					of.write(line)
		f.close()
		of.close()
	
	s = open("{}.stats.txt".format(outid), "a")
	s.write("{} ==> {}.{}\n".format(corpusid, outid, corpusid))
	for i in ("analyzedTypes", "identicalTypes","differentTypes", "analyzedTokens", "identicalTokens", "differentTokens", "changedTokens", "analyzedDictTokens", "identicalDictTokens", "differentDictTokens", "changedDictTokens"):
		if i.endswith("Types"):
			base = stats["analyzedTypes"]
		elif i.endswith("DictTokens"):
			base = stats["analyzedDictTokens"]
		else:
			base = stats["analyzedTokens"]
		if stats[i] > 0:
			s.write("{}\t{}\t{:.2f}%\n".format(i, stats[i], 100*stats[i]/float(base)))
	s.close()

	
if __name__ == "__main__":
	id = sys.argv[1]
	nbThreads = int(sys.argv[2])
	filter = "filter" in sys.argv[3:]
	randomSelect = "random" in sys.argv[3:]
	if "1lex" in id:
		lglist = (("pl", None), ("sk", None), ("uk", "uk-ugtag"), ("ru1", None), ("ru2", None))
	elif "nolex" in id:
		lglist = (("pl", None), ("sk", None), ("uk", None), ("ru1", None), ("ru2", None))
	for lg, lex in lglist:
		convertMulti("{}.train".format(lg), id, nbThreads, filter=filter, randomSelect=randomSelect, dictid=lex)
	os.system("head -n 89886 {0}.ru2.train.txt > {0}.temp.txt".format(id))
	os.system("cat {0}.pl.train.txt {0}.sk.train.txt {0}.uk.train.txt {0}.ru1.train.txt {0}.temp.txt > {0}.all.train.txt".format(id))
	os.remove("{}.temp.txt".format(id))
