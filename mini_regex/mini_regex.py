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

	def get_dot_string(self):
		if not self.compiled:
			self.compile()
		ret = """digraph "%s" {
			rankdir=LR;
			size="%s,%s"
			node [shape = doublecircle]; %s;
			node [shape = circle];
			%s
			}
		"""	
		trans_list = []
		for k, v in self.dfa['trans'].iteritems():
			for sub_k, sub_v in v.iteritems():
				trans_list.append((str(k), str(sub_v), str(sub_k)))

		
		trans = '\n'.join(['%s -> %s [ label = "%s" ];' % itm for itm in trans_list])
		return ret % (self.raw_regex, 40, 40, ' '.join([str(itm) for itm in self.dfa['end']]), trans)

	def compile(self):
		am = nfa.Thompson_AutoMata()
		am.build(self.raw_regex)
		_, __, ___ = nfa2dfa.construct_subsets(am)	
		dfa, start, end = _simplify(_, __, ___)	
		self.dfa = {'trans' :dfa, "start" : start, "end" : end}
		self.compiled = True

def parse(re_dict, text):
	for k in re_dict.iterkeys():
		re_dict[k] = Regex(re_dict[k]) 
	ret = []
	while text:
		leftmost, key = len(text), None
		for k, v in re_dict.iteritems():
			tmp_ret = v.match(text)
			if leftmost > tmp_ret[1]:
				leftmost = tmp_ret[1]
				key = k
		if leftmost == len(text):
			return False, None
		print ret
		ret.append((key, text[: leftmost + 1]))
		text = text[leftmost + 1: ]
	return True, ret

if __name__ == '__main__':
	r = Regex('a(a|b)*abc')
#	r = Regex('a')
	r.compile()
	print r.get_dot_string()	
