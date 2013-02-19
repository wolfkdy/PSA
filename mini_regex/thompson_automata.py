#-*- coding: utf-8 -*-

import nfa2dfa

def trim_blank(text):
	return text.replace(' ', '').replace('\t', '')

def get_match_right_bra(text, idx):
	assert text[idx] == '('
	cnt = 0
	for i in xrange(idx, len(text)):
		if text[i] == '(':
			cnt += 1
		elif text[i] == ')':
			cnt -= 1
		if cnt == 0:
			return i
	return -1

def get_substrs_by_or(text):
	depth = 0
	left = 0
	right = 0
	ret = []
	while right < len(text):
		if text[right] == '(':
			depth += 1
		elif text[right] == ')':
			depth -= 1
		elif text[right] == '|' and depth == 0:
			ret.append(text[left : right])
			left = right + 1
		right += 1
	ret.append(text[left : right])
	return ret

NFA_CNT = 0
class NFA_Node(object):
	def __init__(self):
		global NFA_CNT
		self.edges = dict()
		self.eps_set = set()
		self.index = NFA_CNT
		NFA_CNT += 1

# state of (...)** [ two *] is illegal, but has not yet deal with it
# state of a* is illegal, (a)* is correct, 
class Thompson_AutoMata(object):
	def __init__(self):
		self.start = NFA_Node()
		self.end = NFA_Node()
		self.start.eps_set.add(self.end)

	def unaccept_eps(self):
		self.start.eps_set.remove(self.end)

	def build(self, text):
		text = trim_blank(text)
		self.build_complex(text)

	def build_complex(self, text):
		sub_strs = get_substrs_by_or(text)
		if len(sub_strs) > 1:
			new_end = NFA_Node()
			for s in sub_strs:
				sub_automata = Thompson_AutoMata()
				sub_automata.build_complex(s)
				self.end.eps_set.add(sub_automata.start)
				sub_automata.end.eps_set.add(new_end)
			self.end = new_end
		else :
			self.build_single(sub_strs[0])

	def print_graph(self):
		q = []
		tabu = set()
		q.append(self.start)
		tabu.add(self.start)
		while len(q) != 0:
			tmp = q[0]
			q = q[1 : ]
			for k, v in tmp.edges.iteritems():
				if v in tabu:
					continue
				tabu.add(v)
				q.append(v)	
			for v in tmp.eps_set:
				if v in tabu:
					continue
				tabu.add(v)
				q.append(v)
	
	#the regex @depth 0 is a not with | rule
	def build_single(self, text):
		right = -1
		if len(text) == 0: # null str, eps trans
			return

		if text[0] == '(':
			right = get_match_right_bra(text, 0)
			assert right != -1, 'scan fail @substr %s' % (text, )
			am = Thompson_AutoMata()
			#do not build text[now : right + 1], it leads to a left recurs
			am.build_complex(text[1 : right])
			# (...)*
			if right + 1 < len(text) and text[right + 1] == '*':
				self.start.eps_set.add(am.start)
				am.end.eps_set.add(self.end)
				am.end.eps_set.add(am.start)
				right = right + 2
			#()(...)
			else :
				self.end.eps_set.add(am.start)
				self.end = am.end
				right += 1
		else :
			am = Thompson_AutoMata()
			am.unaccept_eps()
			am.start.edges[text[0]] = am.end
			self.end.eps_set.add(am.start)
			self.end = am.end
			right = 1

		am1 = Thompson_AutoMata()
		am1.build_complex(text[right : ])
		#use an eps trans to merge the end state of cur automata \
		#and the begin state of new automata
		self.end.eps_set.add(am1.start)
		self.end = am1.end

if __name__ == '__main__':
	test_str = '(b)*'
	a = Thompson_AutoMata()	
	a.build(test_str)
	a.print_graph()

