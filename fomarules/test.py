#! /usr/bin/env python
# -*- coding: utf-8 -*-

import foma, codecs, csv


def test(language, wordlist):
	f = codecs.open("test_{}.txt".format(language), "w", "utf-8")
	#fsmA = foma.read_binary("removeA.fsm")
	#fsmB = foma.read_binary("removeB.fsm")
	fsmA = foma.read_binary("{}rulesA.fsm".format(language))
	fsmB = foma.read_binary("{}rulesB.fsm".format(language))
	fsmC = foma.read_binary("{}rulesC.fsm".format(language))
	for word in wordlist:
		f.write(word + "\n")
		f.write("--- {}A --->\n".format(language.upper()))
		for result in fsmA.apply_down(word):
			f.write(result + "\n")
		f.write("--- {}B --->\n".format(language.upper()))
		for result in fsmB.apply_down(word):
			f.write(result + "\n")
		f.write("--- {}C --->\n".format(language.upper()))
		for result in fsmC.apply_down(word):
			f.write(result + "\n")
		f.write("==============\n")
	f.close()


if __name__ == "__main__":
	test("ru", [u"американские", u"жилистый", u"озвучивают", u"высококвалифицированные"])#, u"политико-философско-психологического"])
	test("uk", [u"американськеє", u"випереджаєш", u"почервонілий", u"староукраїнськії"])
	test("sk", [u"найнерозгоднейшиу", u"дроздих", u"данайскыми", u"самовзниетивейшоу"])
	