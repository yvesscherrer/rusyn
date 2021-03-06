#!/bin/bash

# the following commands require the uk2.train.txt file, generated by convertMTE2UD.py
# cat corpus_ud/uk1.train.txt corpus_ud/uk2.train.txt > corpus_ud/uk.train.txt	# uk.train = uk1.train + uk2.train
# cat corpus_ud/uk1.dev.txt corpus_ud/uk1.test.txt > corpus_ud/uk.dev.txt		# uk.dev = uk1.dev + uk1.test
# cat corpus_ud/uk1.dev.gold.txt corpus_ud/uk1.test.gold.txt > corpus_ud/uk.dev.gold.txt		# uk.dev = uk1.dev + uk1.test
	
# head -n 89886 corpus_ud/ru2.train.txt > corpus_ud/ru2_short.train.txt
# cat corpus_ud/pl.train.txt corpus_ud/sk.train.txt corpus_ud/uk.train.txt corpus_ud/ru1.train.txt corpus_ud/ru2_short.train.txt > corpus_ud/all.train.txt

# head -n 124386 corpus_ud/cs.train.txt > corpus_ud/cs_short.train.txt
# cat corpus_ud/pl.train.txt corpus_ud/sk.train.txt corpus_ud/cs_short.train.txt corpus_ud/uk.train.txt corpus_ud/ru1.train.txt corpus_ud/ru2_short.train.txt > corpus_ud/all6.downsample.train.txt
# UPS1=corpus_ud/pl.train.txt corpus_ud/sk.train.txt corpus_ud/uk.train.txt corpus_ud/ru1.train.txt
# cat $UPS1 $UPS1 $UPS1 $UPS1 $UPS1 $UPS1 $UPS1 $UPS1 $UPS1 $UPS1 corpus_ud/cs.train.txt corpus_ud/ru2.train.txt > corpus_ud/all6.upsample.train.txt
UPS2="corpus_ud/pl.train.txt corpus_ud/sk.train.txt corpus_ud/uk.train.txt corpus_ud/ru1.train.txt"
cat $UPS2 $UPS2 $UPS2 $UPS2 $UPS2 $UPS2 $UPS2 $UPS2 $UPS2 $UPS2 corpus_ud/cs.train.txt corpus_ud/ru2.train.txt corpus_ud/ukwiki1M.train.txt > corpus_ud/all7.upsample.train.txt

# cat corpus_ud/pl.train.txt corpus_ud/sk.train.txt corpus_ud/uk.train.txt corpus_ud/ru1.train.txt > corpus_ud/all-ru2.train.txt
# cat corpus_ud/pl.train.txt corpus_ud/sk.train.txt corpus_ud/uk.train.txt corpus_ud/ru2_short.train.txt > corpus_ud/all-ru1.train.txt
# cat corpus_ud/pl.train.txt corpus_ud/sk.train.txt corpus_ud/ru1.train.txt corpus_ud/ru2_short.train.txt > corpus_ud/all-uk.train.txt
# cat corpus_ud/pl.train.txt corpus_ud/uk.train.txt corpus_ud/ru1.train.txt corpus_ud/ru2_short.train.txt > corpus_ud/all-sk.train.txt
# cat corpus_ud/sk.train.txt corpus_ud/uk.train.txt corpus_ud/ru1.train.txt corpus_ud/ru2_short.train.txt > corpus_ud/all-pl.train.txt
# cut -f 1 ../data/rusyndata_2016_12_22/rusinfull_2016_11_11.txt > corpus_ud/RUE80000.txt
