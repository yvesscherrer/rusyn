#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import collections, csv, os

pl_dict = {'a': 'а', 'e': 'е', 'y': 'ы', 'o': 'о', 'ó': 'у', 'u': 'у', 'ą': 'у', 'ę': 'у', 'ia': 'я', 'ja': 'я', 'ie': 'е', 'je': 'є', 'i': 'и', 'ii': 'иї', 'ji': 'и', 'io': 'ьо', 'jo': 'ьо', 'ió': 'ю', 'jó': 'ю', 'iu': 'ю', 'ju': 'ю', 'ią': 'я', 'ją': 'я', 'ię': 'я', 'ję': 'я', 'p': 'п', 'b': 'б', 'f': 'ф', 'w': 'в', 'v': 'в', 't': 'т', 'ć': 'ть', 'd': 'д', 'dź': 'дь', 's': 'с', 'ś': 'сь', 'z': 'з', 'ź': 'зь', 'k': 'к', 'g': 'г', 'ch': 'x', 'h': 'x', 'sz': 'ш', 'ż': 'ж', 'cz': 'ч', 'szcz': 'щ', 'c': 'ц', 'm': 'м', 'n': 'н', 'ń': 'нь', 'ł': 'л', 'l': 'л', 'r': 'р', 'rz': 'р', 'j': 'й', 'x': 'кс', 'q': 'кв'}

sk_dict = {'ďa': 'дя', 'ľa': 'ля', 'ťa': 'тя', 'ďu': 'дю', 'ľu': 'лю', 'ťu': 'тю', 'ď': 'дь', 'ľ': 'ль', 'ť': 'ть', 'ňa': 'ня', 'ňu': 'ню', 'ň': 'нь', '’u': 'ю', '’e': 'є', 'je': 'є', 'ie': 'ие', 'jo': 'ьо', 'ji': 'ї', 'jí': 'ї', 'ch': 'х', 'šč': 'щ', '”': 'ъ', 'ju': 'ю', 'jú': 'ю', 'ja': 'я', 'já': 'я', 'ä': 'я', 'a': 'а', 'á': 'а', 'b': 'б', 'v': 'в', 'w': 'в', 'h': 'г', 'g': 'ґ', 'd': 'д', 'e': 'е', 'é': 'е', 'ž': 'ж', 'z': 'з', 'y': 'ы', 'j': 'й', 'i': 'и', 'í': 'и', 'k': 'к', 'l': 'л', 'ĺ': 'ол', 'm': 'м', 'n': 'н', 'o': 'о', 'ó': 'о', 'ô': 'о', 'p': 'п', 'q': 'кв', 'r': 'р', 'ŕ': 'ер', 's': 'с', 't': 'т', 'u': 'у', 'ú': 'у', 'f': 'ф', 'c': 'ц', 'č': 'ч', 'š': 'ш', 'ŷ': 'ы', 'ý': 'ы', 'y': 'ы', '’': 'ь', 'ė': 'э', 'ŭ': 'ў', 'ö': 'ë'}

cs_dict = {'ďa': 'дя', 'ľa': 'ля', 'ťa': 'тя', 'ďu': 'дю', 'ľu': 'лю', 'ťu': 'тю', 'ď': 'дь', 'ľ': 'ль', 'ť': 'ть', 'ňa': 'ня', 'ňu': 'ню', 'ň': 'нь', '’u': 'ю', '’e': 'є', 'je': 'є', 'ie': 'ие', 'jo': 'ьо', 'ji': 'ї', 'jí': 'ї', 'ch': 'х', 'šč': 'щ', 'řa': 'ря', '”': 'ъ', 'ju': 'ю', 'jú': 'ю', 'ja': 'я', 'já': 'я', 'ä': 'я', 'a': 'а', 'á': 'а', 'b': 'б', 'v': 'в', 'w': 'в', 'h': 'г', 'g': 'ґ', 'd': 'д', 'e': 'е', 'é': 'е', 'ě': 'і', 'ž': 'ж', 'z': 'з', 'y': 'ы', 'j': 'й', 'i': 'и', 'í': 'и', 'k': 'к', 'l': 'л', 'ĺ': 'ол', 'm': 'м', 'n': 'н', 'o': 'о', 'ó': 'о', 'ô': 'о', 'p': 'п', 'q': 'кв', 'r': 'р', 'ŕ': 'р', 'ř': 'р', 's': 'с', 't': 'т', 'u': 'у', 'ú': 'у', 'ů': 'у', 'f': 'ф', 'x': 'кс', 'c': 'ц', 'č': 'ч', 'š': 'ш', 'ŷ': 'ы', 'ý': 'ы', 'y': 'ы', '’': 'ь', 'ė': 'э', 'ŭ': 'ў', 'ö': 'ë'}



unknown = collections.defaultdict(int)
changes = collections.defaultdict(int)

def loadFeatures():
	features = set()
	f = open("tagcorrespUD-2017-02.csv", 'r')
	r = csv.reader(f, delimiter=";")
	for line in r:
		if line[5] != "":
			features.add(line[5])
	f.close()
	return features


def transliterateWord(w, d):
	for lat, cyr in sorted(d.items(), key=lambda x: len(x[0]), reverse=True):
		w = w.replace(lat, cyr)
	return w


def reformat(name1, name2, language, addRaw=False):
	global unknown
	print(name1, "===>", name2)
	features = loadFeatures()
	
	f1 = open(name1, "r", encoding="utf-8")
	f2 = open(name2, "w", encoding="utf-8")
	if addRaw:
		f3 = open(addRaw, "w", encoding="utf-8")
	for line in f1:
		if line.startswith("#"):
			continue
		elements = line.strip().split("\t")
		if len(elements) < 10:
			f2.write("\n")
			if addRaw:
				f3.write("\n")
		else:
			token = elements[1].lower()
			lemma = elements[2].lower()
			if language == "PL":
				token = transliterateWord(token, pl_dict)
				lemma = transliterateWord(lemma, pl_dict)
			elif language == "SK":
				token = transliterateWord(token, sk_dict)
				lemma = transliterateWord(lemma, sk_dict)
			elif language == "CS":
				token = transliterateWord(token, cs_dict)
				lemma = transliterateWord(lemma, cs_dict)
			postag = elements[3]
			morphstr = elements[5]
			if morphstr == "":
				morphstr = "_"
			if morphstr != "_":
				morphelements = set(morphstr.split("|"))
				if "Aspect=Imp" in morphelements:
					morphelements.add("Aspect=Prog")
					morphelements.discard("Aspect=Imp")
					changes["Aspect=Imp"] += 1
				if "Aspect=Imp,Perf" in morphelements:
					morphelements.add("Aspect=Perf")
					morphelements.add("Aspect=Prog")
					morphelements.discard("Aspect=Imp,Perf")
					changes["Aspect=Imp,Perf"] += 1
				if "PronType=Int,Rel" in morphelements:
					morphelements.add("PronType=Rel")
					morphelements.discard("PronType=Int,Rel")
					changes["PronType=Int,Rel"] += 1
				if "VerbForm=Trans" in morphelements:
					morphelements.add("VerbForm=Ger")
					morphelements.discard("VerbForm=Trans")
					changes["VerbForm=Trans"] += 1
				if "VerbForm=Part" in morphelements and postag == "ADJ":
					postag = "VERB"
					changes["VerbForm=Part"] += 1
				if "Variant=Brev" in morphelements:
					morphelements.add("Variant=Short")
					morphelements.discard("Variant=Brev")
					changes["Variant=Brev"] += 1
				if "Variant=Full" in morphelements:
					morphelements.add("Variant=Long")
					morphelements.discard("Variant=Full")
					changes["Variant=Full"] += 1
				# cannot interpret the following - just discard them:
				morphelements.discard("PrepCase=Npr")
				morphelements.discard("PrepCase=Pre")
				morphelements.discard("Case=Par")
				morphelements.discard("AdpType=Voc")
				morphelements.discard("AdpType=Preppron")
				
				for me in morphelements:
					if me not in features:
						unknown[me] += 1
				morphstr = "|".join(sorted(morphelements))
			if morphstr == "":
				morphstr = "_"
			f2.write("\t".join([elements[0], token, lemma, postag, "{}|{}".format(postag, morphstr), morphstr] + elements[6:]) + "\n")
			if addRaw:
				f3.write(token + "\n")
	f1.close()
	f2.close()
	if addRaw:
		f3.close()


def displayUnknown():
	global unknown, changes
	print("Unknown assignments:")
	for item in sorted(unknown, key=unknown.get, reverse=True):
		print(item, unknown[item])
	print("Assignment changes:")
	for item in sorted(changes, key=changes.get, reverse=True):
		print(item, changes[item])


if __name__ == "__main__":
	if "corpus_ud" not in os.listdir("."):
		os.mkdir("corpus_ud")

	# reformat("../data/ud-treebanks-v1.4/UD_Polish/pl-ud-train.conllu", "corpus_ud/pl.train.txt", "PL")
	# reformat("../data/ud-treebanks-v1.4/UD_Polish/pl-ud-dev.conllu", "corpus_ud/pl.dev.gold.txt", "PL", addRaw="corpus_ud/pl.dev.txt")
	# reformat("../data/ud-treebanks-v1.4/UD_Polish/pl-ud-test.conllu", "corpus_ud/pl.test.gold.txt", "PL", addRaw="corpus_ud/pl.test.txt")
	
	# reformat("../data/ud-treebanks-v1.4/UD_Slovak/sk-ud-train.conllu", "corpus_ud/sk.train.txt", "SK")
	# reformat("../data/ud-treebanks-v1.4/UD_Slovak/sk-ud-dev.conllu", "corpus_ud/sk.dev.gold.txt", "SK", addRaw="corpus_ud/sk.dev.txt")
	# reformat("../data/ud-treebanks-v1.4/UD_Slovak/sk-ud-test.conllu", "corpus_ud/sk.test.gold.txt", "SK", addRaw="corpus_ud/sk.test.txt")
	
	# reformat("../data/ud-treebanks-v1.4/UD_Ukrainian/uk-ud-train.conllu", "corpus_ud/uk1.train.txt", "UK")
	# reformat("../data/ud-treebanks-v1.4/UD_Ukrainian/uk-ud-dev.conllu", "corpus_ud/uk1.dev.gold.txt", "UK", addRaw="corpus_ud/uk1.dev.txt")
	# reformat("../data/ud-treebanks-v1.4/UD_Ukrainian/uk-ud-test.conllu", "corpus_ud/uk1.test.gold.txt", "UK", addRaw="corpus_ud/uk1.test.txt")
	
	# reformat("../data/ud-treebanks-v1.4/UD_Russian/ru-ud-train.conllu", "corpus_ud/ru1.train.txt", "RU")
	# reformat("../data/ud-treebanks-v1.4/UD_Russian/ru-ud-dev.conllu", "corpus_ud/ru1.dev.gold.txt", "RU", addRaw="corpus_ud/ru1.dev.txt")
	# reformat("../data/ud-treebanks-v1.4/UD_Russian/ru-ud-test.conllu", "corpus_ud/ru1.test.gold.txt", "RU", addRaw="corpus_ud/ru1.test.txt")
	
	# reformat("../data/ud-treebanks-v1.4/UD_Russian-SynTagRus/ru_syntagrus-ud-train.conllu", "corpus_ud/ru2.train.txt", "RU")
	# reformat("../data/ud-treebanks-v1.4/UD_Russian-SynTagRus/ru_syntagrus-ud-dev.conllu", "corpus_ud/ru2.dev.gold.txt", "RU", addRaw="corpus_ud/ru2.dev.txt")
	# reformat("../data/ud-treebanks-v1.4/UD_Russian-SynTagRus/ru_syntagrus-ud-test.conllu", "corpus_ud/ru2.test.gold.txt", "RU", addRaw="corpus_ud/ru2.test.txt")

	reformat("../data/ud-treebanks-v1.4/UD_Czech/cs-ud-train.conllu", "corpus_ud/cs.train.txt", "CS")
	reformat("../data/ud-treebanks-v1.4/UD_Czech/cs-ud-dev.conllu", "corpus_ud/cs.dev.gold.txt", "CS", addRaw="corpus_ud/cs.dev.txt")
	reformat("../data/ud-treebanks-v1.4/UD_Czech/cs-ud-test.conllu", "corpus_ud/cs.test.gold.txt", "CS", addRaw="corpus_ud/cs.test.txt")
	
	displayUnknown()


