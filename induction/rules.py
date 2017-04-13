#! /usr/bin/env python
# -*- coding: utf-8 -*-

import foma, codecs, collections, multiprocessing, sys


fsm = {}
corpus = set()
nbThreads = 10
maxWordLength = 25	# higher values block

def loadCorpus(paths):
	global corpus
	for path in paths:
		f = codecs.open(path, 'r', 'utf-8')
		for line in f:
			elements = line.strip().split("\t")
			word = elements[0].replace(u"́", u"").replace(u"”", u"").replace(u"„", u"")
			if (word != u"") and (word != u"|"):
				if word != elements[0]:
					print elements[0].encode('utf-8'), "==>", word.encode('utf-8')
				corpus.add(word.lower())
		f.close()


def match(lexdescriptions):
	global fsm
	exactMatches = collections.defaultdict(set)
	transformedMatches = collections.defaultdict(set)
	
	for lexid in lexdescriptions:
		transducerfile = lexdescriptions[lexid][1]
		print "Reading transducer", transducerfile
		if transducerfile == "":
			fsm[lexid] = None
		else:
			fsm[lexid] = foma.read_binary(transducerfile)
	
	if nbThreads > 1:
		pool = multiprocessing.Pool(processes=nbThreads)
	
	for lexid in lexdescriptions:
		lexfile = lexdescriptions[lexid][0]
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
			if len(word) > maxWordLength:
				print "Skip word (too long)", word.encode('utf-8')
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
					if item[-1] == "E":
						exactMatches[word].add(tuple(item[:-1]))
					elif item[-1] == "T":
						transformedMatches[word].add(tuple(item[:-1]))
		del allresults
		print "Done", lexid
		
	return exactMatches, transformedMatches


def matchWord(item):
	global corpus
	global fsm
	result = collections.defaultdict(set)
	word = item[1]
	#print word.encode('utf-8')
	#sys.stdout.flush()
	if word in corpus:
		result[word].add((item[0], item[1], item[2], item[3], "E"))
	if fsm[item[0]]:
		transformations = fsm[item[0]].apply_down(word)
		for tword in transformations:
			if tword in corpus:
				result[tword].add((item[0], item[1], item[2], item[3], "T"))
	return result


# extend to multiple languages and multiprocessing
def convert():
	loadCorpus(("../harmonizeddata/corpus_ud/RUE80000.txt", "../harmonizeddata/corpus_mte/RUE1000.gold.txt"))
	lex = {"RU1": ("../harmonizeddata/lexicons_mte/ru-mte.txt", "../fomarules/rurulesC.fsm"),
		"RU2": ("../harmonizeddata/lexicons_mte/ru-tnt.txt", "../fomarules/rurulesC.fsm"),
		"UK1": ("../harmonizeddata/lexicons_mte/uk-mte.txt", "../fomarules/ukrulesC.fsm"),
		"UK2": ("../harmonizeddata/lexicons_mte/uk-ugtag.txt", "../fomarules/ukrulesC.fsm"),
		"SK1": ("../harmonizeddata/lexicons_mte/sk-mte-cy.txt", "../fomarules/skrulesC.fsm"),
		"PL1": ("../harmonizeddata/lexicons_mte/pl-mte-cy.txt", "../fomarules/plrulesC.fsm"),
		"PL2": ("../harmonizeddata/lexicons_mte/pl-mte.txt", "")
	}
	exactMatches, transformedMatches = match(lex)
	
	outfile = codecs.open("rules2.txt", "w", "utf-8")
	for word in sorted(list(corpus)):
		if word in exactMatches:
			outfile.write(u"{}\t{}\tE\n".format(word, " ".join([u":".join(x) for x in sorted(list(exactMatches[word]))])))
		elif word in transformedMatches:
			outfile.write(u"{}\t{}\tT\n".format(word, " ".join([u":".join(x) for x in sorted(list(transformedMatches[word]))])))
		else:
			outfile.write(u"{}\t---\t-\n".format(word))
	outfile.close()


if __name__ == "__main__":
	convert()
