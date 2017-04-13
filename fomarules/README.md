The file `rules.txt` contains the descriptions of the rules. It has to be compiled using the following command:
	foma -f rules.txt

Compilation creates `*rules[ABC].fsm` files for each language. The A and B transducers contain rules for vowel removal, the C transducers don't.
