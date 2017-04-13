leven.1lex.all: leven.1lex leven.1lex.random leven.1lex.filter leven.1lex.random.filter


leven.1lex:
	./levenshtein.py $@ 10

leven.1lex.random:
	./levenshtein.py $@ 10 random

leven.1lex.filter:
	./levenshtein.py $@ 10 filter

leven.1lex.random.filter:
	./levenshtein.py $@ 10 random filter

########

leven.nolex.all: leven.nolex leven.nolex.random leven.nolex.filter leven.nolex.random.filter

leven.nolex:
	./levenshtein.py $@ 10

leven.nolex.random:
	./levenshtein.py $@ 10 random

leven.nolex.filter:
	./levenshtein.py $@ 10 filter

leven.nolex.random.filter:
	./levenshtein.py $@ 10 random filter

########

rules.nolex.all: rules.nolex rules.nolex.random rules.nolex.filter rules.nolex.random.filter

rules.nolex:
	./rules.py $@ 10

rules.nolex.random:
	./rules.py $@ 10 random

rules.nolex.filter:
	./rules.py $@ 10 filter

rules.nolex.random.filter:
	./rules.py $@ 10 random filter
	