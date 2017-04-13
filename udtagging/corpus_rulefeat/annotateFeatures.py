#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import re, collections, os

correspondences = {}

def loadCorrespondences():
	global correspondences
	f = open("rules-new.txt", 'r', encoding='utf-8')
	first = True
	columns = ("NAME", "RUE", "RU", "UK", "SK", "PL")
	correspondences = {c: collections.defaultdict(set) for c in columns[1:]}
	for line in f:
		if first:
			first = False
			continue
		if line.strip() == "":
			continue
		elements = line.split("\t")
		for i in range(1, len(columns)):
			if elements[i].strip() != "":
				correspondences[columns[i]][elements[i].strip()].add(elements[0])
	f.close()


def getFeatures(word, language):
	global correspondences
	features = set()
	for c in correspondences[language]:
		if re.search(c, word):
			features.update(correspondences[language][c])
	return features


def annotateCorpus(inputfilename, outputfilename, language):
	f = open(inputfilename, 'r', encoding="utf8")
	f2 = open(outputfilename, "w", encoding="utf8")
	for line in f:
		if line.strip() == "":
			f2.write("\n")
		else:
			elements = line.split("\t")
			wordno, token, lemma, tag1, tag2, morph = elements[:6]
			feats = getFeatures(token, language)
			f2.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(wordno, token, lemma, tag1, tag2, morph, "#".join(feats)))
	f.close()
	f2.close()


def annotateRawCorpus(inputfilename, outputfilename, language):
	f = open(inputfilename, 'r', encoding="utf8")
	f2 = open(outputfilename, "w", encoding="utf8")
	for line in f:
		if line.strip() == "":
			f2.write("\n")
		else:
			token = line.strip()
			feats = getFeatures(token, language)
			f2.write("{}\t{}\n".format(token, "#".join(feats)))
	f.close()
	f2.close()


def annotateLexicon(inputfilename, outputfilename, language):
	f = open(inputfilename, 'r', encoding="utf8")
	f2 = open(outputfilename, "w", encoding="utf8")
	for line in f:
		if line.strip() == "":
			f2.write("\n")
		else:
			elements = line.split("\t")
			token, lemma, tag, morph = elements[:4]
			morph = morph.strip()
			feats = getFeatures(token, language)
			f2.write("{}\t{}\t{}\t{}\t{}\n".format(token, lemma, tag, morph, "#".join(feats)))
	f.close()
	f2.close()


def annotateCorpora(srcdir, tgtdir):
	loadCorrespondences()
	for filename in os.listdir(srcdir):
		if filename[:2] in ("pl", "ru", "sk", "uk"):
			if ("gold" in filename) or ("train" in filename):
				annotateCorpus("{}/{}".format(srcdir, filename), "{}/feat.{}".format(tgtdir, filename), filename[:2].upper())
			else:
				annotateRawCorpus("{}/{}".format(srcdir, filename), "{}/feat.{}".format(tgtdir, filename), filename[:2].upper())
		elif filename == "RUE1000.gold.txt":
			annotateCorpus("{}/{}".format(srcdir, filename), "{}/feat.{}".format(tgtdir, filename), "RUE")
		elif filename == "RUE1000.txt" or filename == "RUE80000.txt":
			annotateRawCorpus("{}/{}".format(srcdir, filename), "{}/feat.{}".format(tgtdir, filename), "RUE")
	os.system("head -n 89886 {0}/feat.ru2.train.txt > {0}/temp.txt".format(tgtdir))
	os.system("cat {0}/feat.pl.train.txt {0}/feat.sk.train.txt {0}/feat.uk.train.txt {0}/feat.ru1.train.txt {0}/temp.txt > {0}/feat.all.train.txt".format(tgtdir))
	os.remove("{0}/temp.txt".format(tgtdir))


if __name__ == "__main__":
	annotateCorpora("../../harmonizeddata/corpus_ud", ".")