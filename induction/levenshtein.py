#! /usr/bin/python
# -*- coding: utf-8 -*-

import stringdiff, codecs, collections, multiprocessing

threshold = 0.25


def createVowelSensitiveLevenshtein(vowels, vowelWeight):
	insertmap = {v: vowelWeight for v in vowels}
	deletemap = {v: vowelWeight for v in vowels}
	replacemap = {(v1, v2): vowelWeight for v1 in vowels for v2 in vowels if v1 != v2}
	print len(insertmap), len(deletemap), len(replacemap)
	L = stringdiff.LevenshteinCustomWeights(insert_map=insertmap, delete_map=deletemap, replace_map=replacemap)
	return L


L = createVowelSensitiveLevenshtein(u"аеиоуэюяёыіїєьъй'", 0.5)


def loadLexicons(pathdict):
	lexicon = collections.defaultdict(list)
	for lg, path in pathdict.items():
		print lg
		f = codecs.open(path, 'rU', 'utf-8')
		for line in f:
			elements = line.strip().split("\t")
			if len(elements) != 3:
				print "Wrong line format in", lg
				print line.encode('utf-8')
				continue
			word = elements[0].lower()
			lemma = elements[1].lower()
			tag = elements[2]
			if word != "":
				lexicon[word].append((lg, lemma, tag))
		f.close()
	return lexicon


def loadCorpus(paths):
	words = set()
	for path in paths:
		f = codecs.open(path, 'r', 'utf-8')
		for line in f:
			elements = line.strip().split("\t")
			word = elements[0].replace(u"́", u"").replace(u"”", u"").replace(u"„", u"")
			if (word != u"") and (word != u"|"):
				if word != elements[0]:
					print elements[0].encode('utf-8'), "==>", word.encode('utf-8')
				words.add(word.lower())
		f.close()
	return words


def convert(word):
	global lex
	print word.encode('utf-8')
	if word in lex:
		maxDist = 0
		maxWords = [word]
	else:
		maxDist = threshold*len(word)
		maxWords = []
		for candidate in lex:
			leven = L.levenshtein(word, candidate, case_sensitive=1, max_distance=maxDist+1)
			if leven == maxDist:
				maxWords.append(candidate)
			elif leven < maxDist:
				maxDist = leven
				maxWords = [candidate]
	
	if maxDist >= threshold*len(word):
		return (word, "---", 1.0)
	else:
		results = set()
		for maxWord in maxWords:
			for lg, lemma, tag in lex[maxWord]:
				results.add(u"{}:{}:{}:{}".format(lg, maxWord, lemma, tag))
		return (word, u" ".join(sorted(results)), maxDist/float(len(word)))


def convertMulti(nbThreads):
	global lex
	
	print "load lexicons"
	lex = loadLexicons({"RU1": "../harmonizeddata/lexicons_mte/ru-mte.txt", "RU2": "../harmonizeddata/lexicons_mte/ru-tnt.txt", "UK1": "../harmonizeddata/lexicons_mte/uk-mte.txt", "UK2": "../harmonizeddata/lexicons_mte/uk-ugtag.txt", "SK1": "../harmonizeddata/lexicons_mte/sk-mte-cy.txt", "PL1": "../harmonizeddata/lexicons_mte/pl-mte-cy.txt", "PL2": "../harmonizeddata/lexicons_mte/pl-mte.txt"}) 
	
	print "load corpus"
	corp = loadCorpus(("../harmonizeddata/corpus_ud/RUE80000.txt", "../harmonizeddata/corpus_mte/RUE1000.gold.txt"))
	#corp = corp[:10]
	
	if nbThreads > 1:
		print "launch multiprocessing"
		pool = multiprocessing.Pool(processes=nbThreads)
		results = pool.map(convert, corp)
	else:
		results = [convert(word) for word in corp]
	
	print "write results to file"
	f = codecs.open("levenshtein.txt", "w", "utf-8")
	for word, analysis, dist in sorted(results, key=lambda x: x[0]):
		f.write(u"{}\t{}\t{}\n".format(word, analysis, dist))
	f.close()
	del corp
	del pool
	del results
	print "done"



def verify():
	print "Verifying custom Levenshtein edit distance:"
	l = stringdiff.LevenshteinCustomWeights()
	assert l.levenshtein(u"аNT", u"ауNT") == 1
	l = stringdiff.LevenshteinCustomWeights(delete_map={u"а": 10})
	assert l.levenshtein(u"аNT", u"ауNT", case_sensitive=1) == 1
	l = stringdiff.LevenshteinCustomWeights(insert_map={u"у": 10}, w_replace=20)
	assert l.levenshtein(u"аNT", u"ауNT", case_sensitive=1) == 10
	l = stringdiff.LevenshteinCustomWeights(replace_map={(u"а", u"B"): 0.25})
	assert l.levenshtein(u"ааа", u"BB", case_sensitive=1) == 1.5
	l = stringdiff.LevenshteinCustomWeights(replace_map={(u"а", u"B"): 0.25}, w_insert=0.5)
	assert l.levenshtein(u"аа", u"BBB", case_sensitive=1) == 1
	l = stringdiff.LevenshteinCustomWeights(replace_map={(u"а", u"B"): 0.5})
	assert l.levenshtein(u"ааа", u"BBB", case_sensitive=1) == 1.5
	print "No errors with custom Levenshtein edit distance."
	
	
if __name__ == "__main__":
	convertMulti(10)
	#verify()
