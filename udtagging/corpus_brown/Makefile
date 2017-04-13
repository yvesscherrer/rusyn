origdata:
	./mergeData.py
	../../brown/wcluster --text alltext.txt --c 500
	./annotateBrown.py brown_atomicfeat_500 atomicfeat alltext-c500-p1.out/paths ../../harmonizeddata/corpus_ud .
	./annotateBrown.py brown_token_500 token alltext-c500-p1.out/paths ../../harmonizeddata/corpus_ud .
	./annotateBrown.py brown_compfeat_500 compfeat alltext-c500-p1.out/paths ../../harmonizeddata/corpus_ud .
	./annotateBrown.py brown_decrfeat_500 decrfeat alltext-c500-p1.out/paths ../../harmonizeddata/corpus_ud .
	
	../../brown/wcluster --text alltext.txt --c 1000
	./annotateBrown.py brown_atomicfeat_1000 atomicfeat alltext-c1000-p1.out/paths ../../harmonizeddata/corpus_ud .
	./annotateBrown.py brown_token_1000 token alltext-c1000-p1.out/paths ../../harmonizeddata/corpus_ud .
	./annotateBrown.py brown_compfeat_1000 compfeat alltext-c1000-p1.out/paths ../../harmonizeddata/corpus_ud .
	./annotateBrown.py brown_decrfeat_1000 decrfeat alltext-c1000-p1.out/paths ../../harmonizeddata/corpus_ud .

levendata:
	./mergeDataLeven.py leven.nolex.filter
	../../brown/wcluster --text leven.nolex.filter.alltext.txt --c 500
	./annotateBrown.py leven_brown_atomicfeat_500 atomicfeat leven.nolex.filter.alltext-c500-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed
	./annotateBrown.py leven_brown_token_500 token leven.nolex.filter.alltext-c500-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed
	./annotateBrown.py leven_brown_compfeat_500 compfeat leven.nolex.filter.alltext-c500-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed
	./annotateBrown.py leven_brown_decrfeat_500 decrfeat leven.nolex.filter.alltext-c500-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed
	
	../../brown/wcluster --text leven.nolex.filter.alltext.txt --c 1000
	./annotateBrown.py leven_brown_atomicfeat_1000 atomicfeat leven.nolex.filter.alltext-c1000-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed
	./annotateBrown.py leven_brown_token_1000 token leven.nolex.filter.alltext-c1000-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed
	./annotateBrown.py leven_brown_compfeat_1000 compfeat leven.nolex.filter.alltext-c1000-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed
	./annotateBrown.py leven_brown_decrfeat_1000 decrfeat leven.nolex.filter.alltext-c1000-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed


rulesdata:
	#./mergeDataLeven.py rules.nolex.filter
	#../../brown/wcluster --text rules.nolex.filter.alltext.txt --c 1000
	./annotateBrown.py rules_brown_atomicfeat_1000 atomicfeat rules.nolex.filter.alltext-c1000-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed
	./annotateBrown.py rules_brown_token_1000 token rules.nolex.filter.alltext-c1000-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed
	./annotateBrown.py rules_brown_compfeat_1000 compfeat rules.nolex.filter.alltext-c1000-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed
	./annotateBrown.py rules_brown_decrfeat_1000 decrfeat rules.nolex.filter.alltext-c1000-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed


all100:
	../../brown/wcluster --text alltext.txt --c 100
	./annotateBrown.py brown_atomicfeat_100 atomicfeat alltext-c100-p1.out/paths ../../harmonizeddata/corpus_ud .
	./annotateBrown.py brown_decrfeat_100 decrfeat alltext-c100-p1.out/paths ../../harmonizeddata/corpus_ud .
	
	../../brown/wcluster --text leven.nolex.filter.alltext.txt --c 100
	./annotateBrown.py leven_brown_atomicfeat_100 atomicfeat leven.nolex.filter.alltext-c100-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed
	./annotateBrown.py leven_brown_decrfeat_100 decrfeat leven.nolex.filter.alltext-c100-p1.out/paths ../../harmonizeddata/corpus_ud . ../corpus_transformed
	