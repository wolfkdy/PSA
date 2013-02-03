#-*- coding: utf-8 -*-

import os
import json
import nfa2dfa
import thompson_automata as nfa

def _simplify(dfa, s_set, e_set):
	str2id = dict()
	cnt = 1
	for k, v in dfa.iteritems():
		if k not in str2id:
			str2id[k] = cnt
			cnt += 1
		for trans, to_state in v.iteritems():
			if to_state not in str2id:
				str2id[to_state] = cnt
				cnt += 1

	simple_dfa = dict()
	for k, v in dfa.iteritems():
		simple_dfa[str2id[k]] = dict()
		for trans, to_state in v.iteritems():
			simple_dfa[str2id[k]][trans] = str2id[to_state]
	return simple_dfa, str2id[s_set], [str2id[itm] for itm in e_set]
	
class Regex(object):
	def __init__(self, text):
		self.compiled = False
		self.raw_regex = text
		self.dfa = None

	#greedy strategy match,
	#return True, len(text) - 1 if matches succ
	#return False, right most match char if matches fail
	def match(self, text):
		if not self.compiled:
			self.compile()
		i = 0
		now = self.dfa['start']
		dfa = self.dfa['trans']
		while i < len(text):
			to_state = dfa[now].get(text[i])
			if to_state is None:
				break
			i += 1
			now = to_state

		if i == len(text):
			if now in self.dfa['end']:
				return True, i - 1
			else :
				return False, i - 1
		return False, i	

	def minimize(self):
		assert False, 'not implemented'

	#dump a regex with json fmt
	def dump(self, path):
		if not self.compiled:
			self.compile()
		fd = open(path, 'w')
		json.dump(self.dfa, fd, indent = 8)

	def compile(self):
		am = nfa.Thompson_AutoMata()
		am.build(self.raw_regex)
		_, __, ___ = nfa2dfa.construct_subsets(am)	
		dfa, start, end = _simplify(_, __, ___)	
		print 'after simplify', dfa, start, end
		self.dfa = {'trans' :dfa, "start" : start, "end" : end}
		self.compiled = True

if __name__ == '__main__':
	r = Regex('a(a|b)*abc')
#	r = Regex('a')
	r.compile()
	
