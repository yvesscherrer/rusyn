#! /usr/bin/env python
# -*- coding: utf-8 -*-

import codecs, collections, sys


corpus = set()
nbThreads = 1

def loadCorpus(paths):
	global corpus
	for path in paths:
		f = codecs.open(path, 'r', 'utf-8')
		for line in f:
			elements = line.strip().split("\t")
			word = elements[0].replace(u"́", u"").replace(u"”", u"").replace(u"„", "")
			if (word != u"") and (word != u"|"):
				if word != elements[0]:
					print elements[0].encode('utf-8'), "==>", word.encode('utf-8')
				corpus.add(word.lower())
		f.close()


def match(lexdescriptions):
	exactMatches = collections.defaultdict(set)
	if nbThreads > 1:
		pool = multiprocessing.Pool(processes=nbThreads)
	
	for lexid in lexdescriptions:
		lexfile = lexdescriptions[lexid]
		print "Reading lexicon", lexfile
		lexdata = []
		f = codecs.open(lexfile, 'rU', 'utf-8')
		for line in f:
			elements = line.strip().split("\t")
			if len(elements) != 3:
				print "Wrong line format in", lexid
				print line.encode('utf-8')
				continue
			word = elements[0].lower()
			if word == u"":
				continue
			lemma = elements[1].lower()
			tag = elements[2]
			item = (lexid, word, lemma, tag)
			lexdata.append(item)
		f.close()
		
		print "Starting multiprocessing for lexicon", lexid
		if nbThreads > 1:
			allresults = pool.map(matchWord, lexdata)
		else:
			allresults = [matchWord(item) for item in lexdata]

		print "Reading results", lexid
		for result in allresults:
			for word in result:
				for item in result[word]:
					exactMatches[word].add(item)
		del allresults
		print "Done", lexid
		
	return exactMatches


def matchWord(item):
	global corpus
	result = collections.defaultdict(set)
	word = item[1]
	#print word.encode('utf-8')
	#sys.stdout.flush()
	if word in corpus:
		result[word].add((item[0], item[1], item[2], item[3]))
	return result


def convert():
	loadCorpus(("../harmonizeddata/corpus_ud/RUE80000.txt", "../harmonizeddata/corpus_mte/RUE1000.gold.txt"))
	lex = {"RU1": "../harmonizeddata/lexicons_mte/ru-mte.txt",
		"RU2": "../harmonizeddata/lexicons_mte/ru-tnt.txt",
		"UK1": "../harmonizeddata/lexicons_mte/uk-mte.txt",
		"UK2": "../harmonizeddata/lexicons_mte/uk-ugtag.txt",
		"SK1": "../harmonizeddata/lexicons_mte/sk-mte-cy.txt",
		"PL1": "../harmonizeddata/lexicons_mte/pl-mte-cy.txt",
		"PL2": "../harmonizeddata/lexicons_mte/pl-mte.txt"
	}
	exactMatches = match(lex)
	
	outfile = codecs.open("exact.txt", "w", "utf-8")
	for word in sorted(list(corpus)):
		if word in exactMatches:
			outfile.write(u"{}\t{}\tE\n".format(word, " ".join([u":".join(x) for x in sorted(list(exactMatches[word]))])))
		else:
			outfile.write(u"{}\t---\t-\n".format(word))
	outfile.close()


if __name__ == "__main__":
	convert()
