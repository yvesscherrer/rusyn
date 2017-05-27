#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, collections


marmotpath = "../marmot/marmot.jar"
trainingpath = "../harmonizeddata/corpus_ud"
lexiconpath = "../harmonizeddata/lexicons_ud"
testpath = "../harmonizeddata/corpus_ud"
modelpath = "models"
outputpath = "output"
resultfile = "results.txt"


def trainModel(modelid, trainingcorpus, lexicon, features=False):
	global marmotpath, trainingpath, lexiconpath, modelpath

	if modelid+".marmot" in os.listdir(modelpath):
		print("Model {} already exists, not retraining".format(modelid))
	else:
		print("Training model {}".format(modelid))
		if trainingcorpus+".txt" not in os.listdir(trainingpath):
			print("Training corpus not found at {}/{}.txt".format(trainingpath, trainingcorpus))
			return
		if lexicon and (lexicon+".txt" not in os.listdir(lexiconpath)):
			print("Lexicon not found at {}/{}.txt".format(lexiconpath, lexicon))
			return

		if features:
			featureStr = ",token-feature-index=6"
		else:
			featureStr = ""

		if lexicon:
			os.system("java -Xmx5G -cp {} marmot.morph.cmd.Trainer -train-file form-index=1,tag-index=3,morph-index=5{},{}/{}.txt -tag-morph true -type-dict {}/{}.txt,indexes=[2,3] -model-file {}/{}.marmot".format(marmotpath, featureStr, trainingpath, trainingcorpus, lexiconpath, lexicon, modelpath, modelid))
		else:
			os.system("java -Xmx5G -cp {} marmot.morph.cmd.Trainer -train-file form-index=1,tag-index=3,morph-index=5{},{}/{}.txt -tag-morph true -model-file {}/{}.marmot".format(marmotpath, featureStr, trainingpath, trainingcorpus, modelpath, modelid))
		print("Finished training model {}".format(modelid))


def runModel(modelid, fileid, features=False):
	global marmotpath, modelpath, testpath, outputpath

	print("Annotating {} with model {}".format(fileid, modelid), features)
	if features:
		featureString = ",token-feature-index=1"
	else:
		featureString = ""
	if fileid+".txt" not in os.listdir(testpath):
		print("Test corpus not found at {}/{}.txt".format(testpath, fileid))
		return

	os.system("java -cp {} marmot.morph.cmd.Annotator --model-file {}/{}.marmot --test-file form-index=0{},{}/{}.txt --pred-file {}/{}-{}.txt".format(marmotpath, modelpath, modelid, featureString, testpath, fileid, outputpath, modelid, fileid))
	print("Finished annotating {}".format(fileid))


def unifyMorph(listOfMorphStrings, listOfWeights):
	morphDict = {}
	for morphStr, weight in zip(listOfMorphStrings, listOfWeights):
		if morphStr != "_":
			for element in morphStr.split("|"):
				k, v = element.split("=")
				if k not in morphDict:
					morphDict[k] = collections.defaultdict(float)
				morphDict[k][v] += weight
	unifiedMorph = {}
	for k in morphDict:
		unifiedMorph[k] = max(morphDict[k], key=morphDict[k].get)
	return unifiedMorph


def runMajorityVote(modelids, fileid, outid, weights=None):
	if not weights:
		weights = [1 for x in modelids]
	print("Annotating", fileid, "with models:", modelids, "and weights:", weights)
	files = [open("{}/{}-{}.txt".format(outputpath, modelid, fileid), 'r', encoding="utf-8") for modelid in modelids]
	of = open("{}/{}-{}.txt".format(outputpath, outid, fileid), 'w', encoding="utf-8")
	for lines in zip(*files):
		empty = [x.strip() == "" for x in lines]
		if all(empty):
			of.write("\n")
			continue
		elements = [x.strip().split("\t") for x in lines]
		numbers = [x[0] for x in elements]
		tokens = [x[1] for x in elements]
		if len(set(tokens)) > 1:
			print("Token mismatch", tokens)
			continue
		number = list(set(numbers))[0]
		token = list(set(tokens))[0]
		poses = [x[5] for x in elements]
		posDict = collections.defaultdict(float)
		for pos, weight in zip(poses, weights):
			posDict[pos] += weight
		mostCommonPos = max(posDict, key=posDict.get)
		morph = unifyMorph([x[7] if x[5] == mostCommonPos else "_" for x in elements], weights)
		if morph == {}:
			morphStr = "_"
		else:
			morphStr = "|".join(sorted(["{}={}".format(x, morph[x]) for x in morph]))
		of.write("{}\t{}\t_\t_\t_\t{}\t_\t{}\n".format(number, token, mostCommonPos, morphStr))
	of.close()
	print("Finished annotating {}".format(fileid))


def evaluate(modelid, fileid, goldtokenpos=1, goldtagpos=3, goldmorphpos=5, systokenpos=1, systagpos=5, sysmorphpos=7, lenient=False):
	global testpath, outputpath
	results = collections.defaultdict(int)
	if "{}.gold.txt".format(fileid) not in os.listdir(testpath):
		return results

	print("Evaluating {}-{} with {}.gold".format(modelid, fileid, fileid))
	goldfile = open("{}/{}.gold.txt".format(testpath, fileid), 'r', encoding="utf-8")
	sysfile = open("{}/{}-{}.txt".format(outputpath, modelid, fileid), 'r', encoding="utf-8")
	for goldline in goldfile:
		if goldline.startswith("#") or goldline.strip() == "":
			continue
		sysline = sysfile.readline()
		while sysline.startswith("#") or sysline.strip() == "":
			sysline = sysfile.readline()

		goldelem = goldline.strip().split("\t")
		syselem = sysline.strip().split("\t")
		if goldelem[goldtokenpos] != syselem[systokenpos]:
			print("Word mismatch:", goldelem[goldtokenpos], syselem[systokenpos])
			continue
		else:
			results["comparedTokens"] += 1
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
				results["PosCorrect"] += 1
				if len(goldmorph) > 0:
					results["comparedMorph"] += 1
					notpredicted, predictionerror, correct = 0, 0, 0
					for k in goldmorph:
						if k not in sysmorph:
							notpredicted += 1
						elif goldmorph[k] != sysmorph[k]:
							predictionerror += 1
						else:
							correct += 1
					results["MorphCorrect1"] += correct / (correct + notpredicted + predictionerror)
					results["MorphCorrect2"] += (correct + notpredicted) / (correct + notpredicted + predictionerror)
					if predictionerror == 0:
						results["PosMorphCorrect"] += 1
				else:
					results["PosMorphCorrect"] += 1
	goldfile.close()
	sysfile.close()
	print("Finished evaluating")
	return results


def computeOOV(modelid, trainingcorpus, lexicon, testcorpus):
	global trainingpath, lexiconpath, testpath, oovfile
	results = collections.defaultdict(int)

	print("Computing OOV rate for model {} on corpus {}".format(modelid, testcorpus))
	vocabulary = set()
	tc = open("{}/{}.txt".format(trainingpath, trainingcorpus), 'r', encoding='utf-8')
	for line in tc:
		if line.strip() == "":
			continue
		elements = line.strip().split("\t")
		vocabulary.add(elements[1])
	tc.close()

	if lexicon:
		tl = open("{}/{}.txt".format(lexiconpath, lexicon), 'r', encoding='utf-8')
		for line in tl:
			if line.strip() == "":
				continue
			elements = line.strip().split("\t")
			vocabulary.add(elements[0].lower())
		tl.close()

	tec = open("{}/{}.txt".format(testpath, testcorpus), 'r', encoding='utf-8')
	for line in tec:
		if line.strip() == "":
			continue
		token = line.strip().split("\t")[0]
		results["totalTokens"] += 1
		if token in vocabulary:
			results["foundTokens"] += 1
	tec.close()
	results["oovTokens"] = results["totalTokens"] - results["foundTokens"]
	print("Finished computing OOV rate")
	return results


def writeHeader(exp):
	global resultfile
	rf = open(resultfile, 'a')
	rf.write("\n*** {} ***\n".format(exp.upper()))
	row = ["CONFIG", "Tokens", "PosCorrect", "%", "PosMorphCorrect", "%", "CorrectMorphRatio1", "CorrectMorphRatio2", "Tokens", "Found", "NotFound", "OOVrate"]
	rf.write("\t".join(row) + "\n")
	rf.close()


def writeResults(modelid, fileid, res, oovres):
	global resultfile
	if len(res) > 0:
		row = ["{} > {}".format(modelid.upper(), fileid.upper()), "{}".format(res["comparedTokens"]), "{}".format(res["PosCorrect"]), "{:.2f}%".format(100*res["PosCorrect"]/res["comparedTokens"]), "{}".format(res["PosMorphCorrect"]), "{:.2f}%".format(100*res["PosMorphCorrect"]/res["comparedTokens"]), "{:.2f}%".format(100*res["MorphCorrect1"]/res["comparedMorph"]), "{:.2f}%".format(100*res["MorphCorrect2"]/res["comparedMorph"])]
	else:
		row = ["{} > {}".format(modelid.upper(), fileid.upper()), "", "", "", "", "", "", ""]

	if len(oovres) > 0:
		row2 = ["{}".format(oovres["totalTokens"]), "{}".format(oovres["foundTokens"]), "{}".format(oovres["oovTokens"]), "{:.2f}%".format(100*oovres["oovTokens"]/oovres["totalTokens"])]
	else:
		row2 = ["", "", "", ""]

	rf = open(resultfile, 'a')
	rf.write("\t".join(row) + "\t" + "\t".join(row2) + "\n")
	rf.close()


def experiment(expid, models, testsets, features=False):
	writeHeader(expid)
	for m in sorted(models):
		trainModel(m, models[m][0], models[m][1], features)
		for t in testsets:
			runModel(m, t, features)
			results = evaluate(m, t, lenient=("RUE" in t))
			oovresults = computeOOV(m, models[m][0], models[m][1], t)
			writeResults(m, t, results, oovresults)


# single-language models, no lexicons
def exp1():
	experiment(
		"exp1",
		{"pl.nolex": ("pl.train", None), "sk.nolex": ("sk.train", None), "uk.nolex": ("uk.train", None), "ru1.nolex": ("ru1.train", None), "ru2.nolex": ("ru2.train", None)},
		("pl.dev", "sk.dev", "uk.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000")
	)


# single-language models, with lexicons
def exp2():
	global lexiconpath
	if "uk-mte+ugtag.txt" not in os.listdir(lexiconpath):
		os.system("cat {0}/uk-mte.txt {0}/uk-ugtag.txt > {0}/uk-mte+ugtag.txt".format(lexiconpath))
	if "ru-mte+tnt.txt" not in os.listdir(lexiconpath):
		os.system("cat {0}/ru-mte.txt {0}/ru-tnt.txt > {0}/ru-mte+tnt.txt".format(lexiconpath))

	experiment(
		"exp2",
		{"pl.lex": ("pl.train", "pl-mte-cy"), "sk.lex": ("sk.train", "sk-mte-cy"), "uk.lex1": ("uk.train", "uk-mte"), "uk.lex2": ("uk.train", "uk-ugtag"), "uk.lex12": ("uk.train", "uk-mte+ugtag"), "ru1.lex1": ("ru1.train", "ru-mte"), "ru1.lex2": ("ru1.train", "ru-tnt"), "ru1.lex12": ("ru1.train", "ru-mte+tnt"), "ru2.lex1": ("ru2.train", "ru-mte"), "ru2.lex2": ("ru2.train", "ru-tnt"), "ru2.lex12": ("ru2.train", "ru-mte+tnt")},
		("pl.dev", "sk.dev", "uk.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000")
	)


# merged models, with and without lexicons
def exp3():
	global lexiconpath
	if "pl+sk+uk-ugtag+ru-mte.txt" not in os.listdir(lexiconpath):
		os.system("cat {0}/pl-mte.txt {0}/sk-mte.txt {0}/uk-ugtag.txt {0}/ru-mte.txt > {0}/pl+sk+uk-ugtag+ru-mte.txt".format(lexiconpath))

	experiment(
		"exp3",
		{"all.nolex": ("all.train", None), "all.1lex": ("all.train", "uk-ugtag"), "all.4lex": ("all.train", "pl+sk+uk-ugtag+ru-mte")},
		("pl.dev", "sk.dev", "uk.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000")
	)


# merged models with additional Czech data, without lexicon
def exp3b():
	experiment(
		"exp3b",
		{"all6.downsample": ("all6.downsample.train", None), "all6.upsample": ("all6.upsample.train", None)},
		("pl.dev", "sk.dev", "uk.dev", "cs.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000")
	)


# merged models with additional TnT-tagged Ukrainian data and Czech
def exp3c():
	experiment(
		"exp3c",
		{"all7.upsample": ("all7.upsample.train", None)},
		("pl.dev", "sk.dev", "uk.dev", "cs.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000")
	)


# merged nolex model with induced lexicons
def exp4():
	global lexiconpath
	lexiconpath = "../harmonizeddata/inducedlexicons_ud"
	experiment(
		"exp4",
		{"all.l.nolex": ("all.train", "levenshtein"), "all.r.nolex": ("all.train", "rules"), "all.rl.nolex": ("all.train", "rules_leven"), "all.lr.nolex": ("all.train", "leven_rules")},
		("pl.dev", "sk.dev", "uk.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000")
	)
	global trainingpath, testpath
	trainingpath = "corpus_rulefeat"
	testpath = "corpus_rulefeat"
	experiment(
		"exp4",
		{"all.rfeat.nolex": ("feat.all.train", None)},
		("feat.pl.dev", "feat.sk.dev", "feat.uk.dev", "feat.ru1.dev", "feat.ru2.dev", "feat.RUE1000", "feat.RUE80000"),
		features=True
	)


# exp5a: Marmot with atomic tags
def exp5a():
	global trainingpath, modelpath, testpath
	modelid = "atomtags.all.nolex"
	trainingcorpus = "all.train"
	writeHeader("exp5a")

	# training
	if modelid+".marmot" in os.listdir(modelpath):
		print("Model {} already exists, not retraining".format(modelid))
	else:
		print("Training model {}".format(modelid))
		if trainingcorpus+".txt" not in os.listdir(trainingpath):
			print("Training corpus not found at {}/{}.txt".format(trainingpath, trainingcorpus))
			return
		os.system("java -Xmx5G -cp {} marmot.morph.cmd.Trainer -train-file form-index=1,tag-index=4,{}/{}.txt -tag-morph false -model-file {}/{}.marmot".format(marmotpath, trainingpath, trainingcorpus, modelpath, modelid))
		print("Finished training model {}".format(modelid))

	# run + evaluate
	for fileid in ("pl.dev", "sk.dev", "uk.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000"):
		print("Annotating {} with model {}".format(fileid, modelid))
		if fileid+".txt" not in os.listdir(testpath):
			print("Test corpus not found at {}/{}.txt".format(testpath, fileid))
			return
		os.system("java -cp {} marmot.morph.cmd.Annotator --model-file {}/{}.marmot --test-file form-index=0,{}/{}.txt --pred-file {}/{}-{}.txt".format(marmotpath, modelpath, modelid, testpath, fileid, outputpath, modelid, fileid))
		print("Finished annotating {}".format(fileid))
		results = evaluate(modelid, fileid, goldtagpos=4, goldmorphpos=4, systagpos=5, sysmorphpos=5, lenient=("RUE" in fileid))
		oovresults = computeOOV(modelid, trainingcorpus, None, fileid)
		writeResults(modelid, fileid, results, oovresults)


def reformatTrainingData(infile, outfile, openclassfile):
	f1 = open(infile, 'r', encoding="utf-8")
	f2 = open(outfile, 'w', encoding="utf-8")
	openclasstags = set()
	for line in f1:
		if line.strip() == "":
			f2.write(line)
		else:
			elements = line.strip().split("\t")
			token = elements[1]
			lemma = elements[2]
			tag = elements[4]

			tag = tag.replace("NUM|Animacy=Anim|Case=Loc", "NUM|Case=Loc").replace("NUM|Animacy=Anim|Case=Acc|Gender=Fem", "NUM|Case=Acc|Gender=Fem")
			if tag.split("|")[0] in ("ADJ", "ADV", "NOUN", "PROPN", "NUM", "VERB", "X", "Y"):
				if "VerbForm=Part" not in tag.split("|"):		# segfaults on some of the participle forms
					openclasstags.add(tag)
			f2.write("{}\t{}\t{}\n".format(token, tag, lemma))
	f1.close()
	f2.close()

	f3 = open(openclassfile, 'w', encoding="utf-8")
	for t in sorted(openclasstags):
		f3.write(t + "\n")
	f3.close()


# TreeTagger with atomic tags
def exp5b():
	global modelpath, testpath
	modelid = "all.tt"
	newtrainingpath = "corpus_tt"
	writeHeader("exp5b")

	# training
	if newtrainingpath not in os.listdir("."):
		os.mkdir(newtrainingpath)
	if "all.train.tt" not in os.listdir(newtrainingpath):
		reformatTrainingData(trainingpath + "/all.train.txt", newtrainingpath + "/all.train.tt", newtrainingpath + "/all.open.tt")
		os.system("/usr/local/treetagger/cmd/make-lex.perl {0}/all.train.tt > {0}/all.lexicon.tt".format(newtrainingpath))
	if modelid in os.listdir(modelpath):
		print("Model {} already exists, not retraining".format(modelid))
	else:
		print("Training model {}".format(modelid))
		os.system('train-tree-tagger -st "PUNCT|_" -utf8 {0}/all.lexicon.tt {0}/all.open.tt {0}/all.train.tt {1}/{2}'.format(newtrainingpath, modelpath, modelid))
		print("Finished training model {}".format(modelid))

	# run + evaluate
	for fileid in ("pl.dev", "sk.dev", "uk.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000"):
		print("Annotating {} with model {}".format(fileid, modelid))
		if fileid+".txt" not in os.listdir(testpath):
			print("Test corpus not found at {}/{}.txt".format(testpath, fileid))
			return
		os.system("tree-tagger -token {}/{} < {}/{}.txt > {}/{}-{}.txt".format(modelpath, modelid, testpath, fileid, outputpath, modelid, fileid))
		print("Finished annotating {}".format(fileid))
		results = evaluate(modelid, fileid, goldtagpos=4, goldmorphpos=4, systokenpos=0, systagpos=1, sysmorphpos=1, lenient=("RUE" in fileid))
		oovresults = computeOOV(modelid, "all.train", None, fileid)
		writeResults(modelid, fileid, results, oovresults)


# merged model on transformed training data
def exp6():
	global trainingpath
	trainingpath = "corpus_transformed"
	experiment("exp6",
		{"trans.leven": ("leven.nolex.all.train", None), "trans.leven-random": ("leven.nolex.random.all.train", None),
		"trans.leven-filter": ("leven.nolex.filter.all.train", None), "trans.leven-random-filter": ("leven.nolex.random.filter.all.train", None),
		"trans.rules-filter": ("rules.nolex.filter.all.train", None), "trans.rules-random-filter": ("rules.nolex.random.filter.all.train", None)
		},
		("pl.dev", "sk.dev", "uk.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000")
	)


# majority vote and majority self training
def exp7():
	global trainingpath
	writeHeader("exp7")
	# needed for oov computation
	if "pl+sk+uk+ru1+ru2.txt" not in os.listdir(trainingpath):
		os.system("cat {0}/pl.train.txt {0}/sk.train.txt {0}/uk.train.txt {0}/ru1.train.txt {0}/ru2.train.txt > {0}/pl+sk+uk+ru1+ru2.txt".format(trainingpath))
	train = ("pl.nolex", "sk.nolex", "uk.nolex", "ru1.nolex", "ru2.nolex")
	for t in ("pl.dev", "sk.dev", "uk.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000"):
		oovresults = computeOOV("maj.nolex", "pl+sk+uk+ru1+ru2", None, t)

		runMajorityVote(train, t, "maj-random.nolex")
		results = evaluate("maj-random.nolex", t, lenient=("RUE" in t))
		writeResults("maj-random.nolex", t, results, oovresults)

		runMajorityVote(train, t, "maj-weighted0.nolex", weights=(1.5, 3, 3.5, 1, 1))
		results = evaluate("maj-weighted0.nolex", t, lenient=("RUE" in t))
		writeResults("maj-weighted0.nolex", t, results, oovresults)

		runMajorityVote(train, t, "maj-weighted1.nolex", weights=(1.5, 3, 4, 1, 1))
		results = evaluate("maj-weighted1.nolex", t, lenient=("RUE" in t))
		writeResults("maj-weighted1.nolex", t, results, oovresults)

	trainingpath = "corpus_self"
	if trainingpath not in os.listdir("."):
		os.mkdir(trainingpath)
	os.system("cut -f 1-3,6-8 {}/maj-random.nolex-RUE80000.txt > {}/maj-random.nolex-RUE80000.txt".format(outputpath, trainingpath))
	os.system("cut -f 1-3,6-8 {}/maj-weighted0.nolex-RUE80000.txt > {}/maj-weighted0.nolex-RUE80000.txt".format(outputpath, trainingpath))
	os.system("cut -f 1-3,6-8 {}/maj-weighted1.nolex-RUE80000.txt > {}/maj-weighted1.nolex-RUE80000.txt".format(outputpath, trainingpath))
	experiment(
		"exp7",
		{"self-maj-random.nolex": ("maj-random.nolex-RUE80000", None), "self-maj-weighted0.nolex": ("maj-weighted0.nolex-RUE80000", None), "self-maj-weighted1.nolex": ("maj-weighted1.nolex-RUE80000", None)},
		("pl.dev", "sk.dev", "uk.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000")
	)


# brown clustering
def exp8():
	global trainingpath, testpath
	trainingpath = "corpus_brown"
	testpath = "corpus_brown"
	writeHeader("exp8")
	testitems = ("pl.dev", "sk.dev", "uk.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000")
	models = ("brown_atomicfeat_500", "brown_token_500", "brown_compfeat_500", "brown_decrfeat_500", "brown_atomicfeat_1000", "brown_token_1000", "brown_compfeat_1000", "brown_decrfeat_1000", "leven_brown_atomicfeat_500", "leven_brown_compfeat_500", "leven_brown_decrfeat_500", "leven_brown_atomicfeat_1000", "leven_brown_compfeat_1000", "leven_brown_decrfeat_1000", "rules_brown_atomicfeat_1000", "rules_brown_compfeat_1000", "rules_brown_decrfeat_1000")
	for m in models:
		trainModel("{}.all.nolex".format(m), "{}.all.train".format(m), None, features=not ("token" in m))
		for t in testitems:
			runModel("{}.all.nolex".format(m), "{}.{}".format(m, t), features=not ("token" in m))
			results = evaluate("{}.all.nolex".format(m), "{}.{}".format(m, t), lenient=("RUE" in t))
			oovresults = computeOOV("{}.all.nolex".format(m), "{}.all.train".format(m), None, "{}.{}".format(m, t))
			writeResults("{}.all.nolex".format(m), "{}.{}".format(m, t), results, oovresults)

def exp8b():
	global trainingpath, testpath
	trainingpath = "corpus_brown"
	testpath = "corpus_brown"
	writeHeader("exp8b")
	testitems = ("pl.dev", "sk.dev", "uk.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000")
	models = ("brown_atomicfeat_100", "brown_decrfeat_100", "leven_brown_atomicfeat_100", "leven_brown_decrfeat_100")
	for m in models:
		trainModel("{}.all.nolex".format(m), "{}.all.train".format(m), None, features=not ("token" in m))
		for t in testitems:
			runModel("{}.all.nolex".format(m), "{}.{}".format(m, t), features=not ("token" in m))
			results = evaluate("{}.all.nolex".format(m), "{}.{}".format(m, t), lenient=("RUE" in t))
			oovresults = computeOOV("{}.all.nolex".format(m), "{}.all.train".format(m), None, "{}.{}".format(m, t))
			writeResults("{}.all.nolex".format(m), "{}.{}".format(m, t), results, oovresults)


# corpus ablation
def exp9():
	experiment(
		"exp9",
		{"all-pl.nolex": ("all-pl.train", None), "all-sk.nolex": ("all-sk.train", None), "all-uk.nolex": ("all-uk.train", None), "all-ru1.nolex": ("all-ru1.train", None), "all-ru2.nolex": ("all-ru2.train", None)},
		("pl.dev", "sk.dev", "uk.dev", "ru1.dev", "ru2.dev", "RUE1000", "RUE80000")
	)





if __name__ == "__main__":
	if modelpath not in os.listdir("."):
		os.mkdir(modelpath)
	if outputpath not in os.listdir("."):
		os.mkdir(outputpath)

	globals()[sys.argv[1]]()
