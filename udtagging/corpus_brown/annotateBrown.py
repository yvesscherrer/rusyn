#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import re, os, sys

letters = "abcdefghijklmnopqrstuvwxyz"

def loadCorrespondences(filename):
	correspondences = {}
	f = open(filename, 'r', encoding='utf-8')
	for line in f:
		if line.strip() == "":
			continue
		elements = line.strip().split("\t")
		correspondences[elements[1]] = elements[0]
	f.close()
	return correspondences


def annotateCorpus(inputfilename, outputfilename, correspondences, mode):
	f = open(inputfilename, 'r', encoding="utf8")
	f2 = open(outputfilename, "w", encoding="utf8")
	for line in f:
		if line.strip() == "":
			f2.write("\n")
		else:
			elements = line.split("\t")
			wordno, token, lemma, tag1, tag2, morph = elements[:6]
			cluster = correspondences.get(token, "0")
			if token not in correspondences:
				print("Unknown word", token, "in corpus", inputfilename)
			if mode == "atomicfeat":
				f2.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(wordno, token, lemma, tag1, tag2, morph, cluster))
			elif mode == "token":
				f2.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(wordno, cluster, lemma, tag1, tag2, morph, token))
			elif mode == "compfeat":
				s = []
				for val, letter in zip(cluster, letters):
					s.append(letter+val)
				f2.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(wordno, token, lemma, tag1, tag2, morph, "#".join(s)))
			elif mode == "decrfeat":
				s = [cluster]
				for i in range(2, len(cluster), 2):
					s.append(cluster[:i])
				f2.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(wordno, token, lemma, tag1, tag2, morph, "#".join(s)))
	f.close()
	f2.close()


def annotateRawCorpus(inputfilename, outputfilename, correspondences, mode):
	f = open(inputfilename, 'r', encoding="utf8")
	f2 = open(outputfilename, "w", encoding="utf8")
	for line in f:
		if line.strip() == "":
			f2.write("\n")
		else:
			token = line.strip()
			cluster = correspondences.get(token, "0")
			if token not in correspondences:
				print("Unknown word", token, "in corpus", inputfilename)
			if mode == "atomicfeat":
				f2.write("{}\t{}\n".format(token, cluster))
			elif mode == "token":
				f2.write("{}\t{}\n".format(cluster, token))
			elif mode == "compfeat":
				s = []
				for val, letter in zip(cluster, letters):
					s.append(letter+val)
				f2.write("{}\t{}\n".format(token, "#".join(s)))
			elif mode == "decrfeat":
				s = [cluster]
				for i in range(2, len(cluster), 2):
					s.append(cluster[:i])
				f2.write("{}\t{}\n".format(token, "#".join(s)))
	f.close()
	f2.close()


def annotateLexicon(inputfilename, outputfilename, correspondences, mode):
	f = open(inputfilename, 'r', encoding="utf8")
	f2 = open(outputfilename, "w", encoding="utf8")
	for line in f:
		if line.strip() == "":
			f2.write("\n")
		else:
			elements = line.split("\t")
			token, lemma, tag, morph = elements[:4]
			morph = morph.strip()
			cluster = correspondences.get(token, "0")
			if mode == "atomicfeat":
				f2.write("{}\t{}\t{}\t{}\t{}\n".format(token, lemma, tag, morph, cluster))
			elif mode == "token":
				f2.write("{}\t{}\t{}\t{}\t{}\n".format(cluster, lemma, tag, morph, token))
			elif mode == "compfeat":
				s = []
				for val, letter in zip(cluster, letters):
					s.append(letter+val)
				f2.write("{}\t{}\t{}\t{}\t{}\n".format(token, lemma, tag, morph, "#".join(s)))
			elif mode == "decrfeat":
				s = [cluster]
				for i in range(2, len(cluster), 2):
					s.append(cluster[:i])
				f2.write("{}\t{}\t{}\t{}\t{}\n".format(token, lemma, tag, morph, "#".join(s)))
	f.close()
	f2.close()


def annotateCorpora(id, mode, clusterfile, srcdir, tgtdir, srcdir2=None):
	c = loadCorrespondences(clusterfile)
	for filename in os.listdir(srcdir):
		if filename[:2] in ("pl", "ru", "sk", "uk"):
			if ("gold" in filename) or ("train" in filename):
				if "{}.{}".format(id, filename) in os.listdir(srcdir2):
					print("Use {} for file {}.{}".format(srcdir2, id, filename))
					annotateCorpus("{}/{}.{}".format(srcdir2, id, filename), "{}/{}.{}".format(tgtdir, id, filename), c, mode)
				else:
					annotateCorpus("{}/{}".format(srcdir, filename), "{}/{}.{}".format(tgtdir, id, filename), c, mode)
			else:
				if "{}.{}".format(id, filename) in os.listdir(srcdir2):
					print("Use {} for file {}.{}".format(srcdir2, id, filename))
					annotateRawCorpus("{}/{}.{}".format(srcdir2, id, filename), "{}/{}.{}".format(tgtdir, id, filename), c, mode)
				else:
					annotateRawCorpus("{}/{}".format(srcdir, filename), "{}/{}.{}".format(tgtdir, id, filename), c, mode)
		elif filename == "RUE1000.gold.txt":
			annotateCorpus("{}/{}".format(srcdir, filename), "{}/{}.{}".format(tgtdir, id, filename), c, mode)
		elif filename == "RUE1000.txt" or filename == "RUE80000.txt":
			annotateRawCorpus("{}/{}".format(srcdir, filename), "{}/{}.{}".format(tgtdir, id, filename), c, mode)
	os.system("head -n 89886 {0}/{1}.ru2.train.txt > {0}/{1}.temp.txt".format(tgtdir, id))
	os.system("cat {0}/{1}.pl.train.txt {0}/{1}.sk.train.txt {0}/{1}.uk.train.txt {0}/{1}.ru1.train.txt {0}/{1}.temp.txt > {0}/{1}.all.train.txt".format(tgtdir, id))
	os.remove("{0}/{1}.temp.txt".format(tgtdir, id))


def annotateTransformedCorpora():
	for x in (("", "leven.nolex.filter.alltext-c500-p1.out/paths"), (".1M", "leven.nolex.filter.alltext-c1000-p1.out/paths")):
		c = loadCorrespondences(x[1])

		for f in ("pl", "ru1", "ru2", "sk", "uk"):
			# train
			annotateCorpus("corpus_transformed/leven.nolex.filter.{}.train.txt".format(f), "corpus/brown1{}.leven-nolex-filter.{}.train.txt".format(x[0], f), c, "atomicfeat")
			# dev.gold
			annotateCorpus("corpus/{}.dev.gold.txt".format(f), "corpus/brown1{}.leven-nolex-filter.{}.dev.gold.txt".format(x[0], f), c, "atomicfeat")
			# test.gold
			annotateCorpus("corpus/{}.test.gold.txt".format(f), "corpus/brown1{}.leven-nolex-filter.{}.test.gold.txt".format(x[0], f), c, "atomicfeat")
			# dev
			annotateRawCorpus("corpus/{}.dev.txt".format(f), "corpus/brown1{}.leven-nolex-filter.{}.dev.txt".format(x[0], f), c, "atomicfeat")
			# test
			annotateRawCorpus("corpus/{}.test.txt".format(f), "corpus/brown1{}.leven-nolex-filter.{}.test.txt".format(x[0], f), c, "atomicfeat")

		# RUE1000.gold
		annotateCorpus("corpus/RUE1000.gold.txt", "corpus/brown1{}.leven-nolex-filter.RUE1000.gold.txt".format(x[0]), c, "atomicfeat")
		# RUE1000
		annotateRawCorpus("corpus/RUE1000.txt", "corpus/brown1{}.leven-nolex-filter.RUE1000.txt".format(x[0]), c, "atomicfeat")
		# RUE80000
		annotateRawCorpus("corpus/RUE80000.txt", "corpus/brown1{}.leven-nolex-filter.RUE80000.txt".format(x[0]), c, "atomicfeat")
		# UGTAG
		annotateLexicon("lexicons/wfl-mte-uk.txt", "lexicons/brown1{}.leven-nolex-filter.wfl-mte-uk.txt".format(x[0]), c, "atomicfeat")
	
		os.system("head -n 89886 corpus/brown1{0}.leven-nolex-filter.ru2.train.txt > corpus/brown1{0}.leven-nolex-filter.temp.txt".format(x[0]))
		os.system("cat corpus/brown1{0}.leven-nolex-filter.pl.train.txt corpus/brown1{0}.leven-nolex-filter.sk.train.txt corpus/brown1{0}.leven-nolex-filter.uk.train.txt corpus/brown1{0}.leven-nolex-filter.ru1.train.txt corpus/brown1{0}.leven-nolex-filter.temp.txt > corpus/brown1{0}.leven-nolex-filter.all.train.txt".format(x[0]))
		os.remove("corpus/brown1{0}.leven-nolex-filter.temp.txt".format(x[0]))


if __name__ == "__main__":
	if len(sys.argv) > 6:
		annotateCorpora(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], srcdir2=sys.argv[6])
	else:
		annotateCorpora(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

	#annotateTransformedCorpora()
	