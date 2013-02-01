#-*- coding: utf-8 -*-

import tokens
from tokens import token_factory as fact
from express import express_factory as e_fact


def get_first_set_multi(g, tokens):
	ret = set()
	eps_token = fact.create_epsilon()
	for token in tokens:
		token_set = get_first_set(g, token)
		ret = ret.union(token_set)
		if eps_token not in token_set:
			if eps_token in ret:
				ret.remove(eps_token)
			return ret
	return ret

#get token t's first set in grammar g
def get_first_set(g, t):
	ret = set()
	if tokens.is_terminal(t) or tokens.is_epsilon(t):
		ret.add(t)
		return ret
	eps_token = fact.create_epsilon()
	exps = g.get_expresses_by_left(t)
	for exp in exps:
		for _tokens in exp.right_tokens_list:
			tmp = get_first_set_multi(g, _tokens)
			ret = ret.union(tmp)
	return ret


#better to put trie_node and trie otherwhere
class TrieNode(object):
	def __init__(self):
		self.next = {}
		self.represent = None

class Trie(object):
	def __init__(self, sample_list):
		self.root = TrieNode()
		for sample in sample_list:
			self._insert_sample(sample)

	def _insert_sample(self, text):
		p = self.root
		for ch in text:
			if p.next.get(ch, -1) == -1:
				p.next[ch] = TrieNode()
			p = p.next[ch]
		p.represent = text

	# return the prefix of text which matches trie at the first time
	def leftmost_match(self, text):
		p = self.root
		for ch in text:
			if p.represent != None:
				return p.represent
			if p.next.get(ch, -1) == -1:
				return
			p = p.next[ch]
		return p.represent	

#class Grammar describes a grammar which begins with @start@ 
class Grammar(object):
	def __init__(self, start, others):
		self.is_normalized = False
		#undeterminal tokens
		self.ut_tokens = set()
		self.expresses = list()
		start = start.replace(' ', '')
		others = [itm.replace(' ', '') for itm in others]
		for itm in others:
			left, right = itm.split('->')
			self.ut_tokens.add(fact.create_unterminal(left))
		left, right = start.split('->')
		self.start_token = fact.create_unterminal(left)
		self.ut_tokens.add(self.start_token)

		others.append(start)
		trie = Trie([ut_token.text for ut_token in self.ut_tokens])

		#merge express whch uses the same left part
		left_right_dict = {}
		for itm in others:
			left, right = itm.split('->')
			right_text_list = right.split('|')
			if left not in left_right_dict:
				left_right_dict[left] = []
			left_right_dict[left].extend(right_text_list)

		for left, right_text_list in left_right_dict.iteritems():
			tokens_list = []
			for right_text in right_text_list:
				i =  0
				tokens = []
				while i < len(right_text):
					s = trie.leftmost_match(right_text[i:])
					if s is None:
						tokens.append(fact.create_terminal(right_text[i]))
						assert right_text[i] != 'C', right_text
						i += 1
					else :
						tokens.append(fact.create_unterminal(s))
						i += len(s)
				tokens_list.append(tokens)
			self.expresses.append( \
					e_fact.create_simple( \
						fact.create_unterminal(left), tokens_list))

	def _eliminate_left_recursive(self):
		old_ut_tokens = list(self.ut_tokens)
		new_ut_tokens = list()

		def get_idx_by_left(left):
			for i in xrange(len(self.expresses)):
				if self.expresses[i].left_token == left:
					return i
			return -1
		#new exps generated when eliminating the  immiate left recursive
		new_exps = []
		for i in xrange(len(old_ut_tokens)):
			i_exp_idx = get_idx_by_left(old_ut_tokens[i])
			assert (i_exp_idx != -1)
			for j in xrange(i - 1):
				exp_i = self.expresses[i_exp_idx]
				j_exp_idx = get_idx_by_left(old_ut_tokens[j])
				assert (j_exp_idx != -1)
				exp_j = self.expresses[j_exp_idx]
				#_eliminate_left_recursive is called before _expand,
				# so, use an assert to make sure logic is correct
				# notice, exps with same left part is merged in __init__
				new_exp_i = exp_i.replace_leftmost_token(exp_j)
				self.expresses[i_exp_idx] = new_exp_i
			if self.expresses[i_exp_idx].is_left_recursive():
				i_exp_cpy, new_exp = \
					self.expresses[i_exp_idx].eliminate_left_recursive()
				self.expresses[i_exp_idx] = i_exp_cpy
				new_exps.append(new_exp)
		for new_exp in new_exps:
			self.ut_tokens.add(new_exp.left_token)
			self.expresses.append(new_exp)

	def __repr__(self):
		lst = [repr(itm) for itm in self.expresses ]
		return '\n'.join(lst)

	def get_expresses_by_left(self, left):
		lst = []
		for exp in self.expresses:
			if exp.left_token == left:
				lst.append(exp)
		return lst

	#return the first express of a normalized grammar
	def get_first_express(self):
		assert self.is_normalized, 'get first express of a non-normalized grammar is meaningless'
		exps = self.get_expresses_by_left(self.start_token)
		return exps[0]

	def _augment(self):
		tmp = self.start_token
		#create a different token for new start state
		self.start_token = fact.create_unterminal(self.start_token.text + "__S")	
		self.expresses.append(e_fact.create_simple(self.start_token, [[tmp]]))

	# expand all expresses concated with '|'
	def _expand(self):
		old_lst = self.expresses
		new_lst = []
		for itm in old_lst:
			new_lst.extend(itm.get_expand_form())
		self.expresses = new_lst

	#prepare self for constructin lr(1)
	def normalize(self):
		if self.is_normalized:
			return
		self._augment()
		self._eliminate_left_recursive()
		self._expand()
		self.is_normalized = True

def main():
	gram_dict = {
		'start' : 'S->CC',
		'other' : ['C->cC|d']
	}
	gram_dict = {
		'start' : 'A->Aa|b',
		'other' : [],
	}
	'''
	gram_dict = {
		'start' : 'A->Aa1|Aa2|Aa3|Aa4|Aa5|b1|b2|b3|b4|b5',
		'other' : [],
	}
	'''
	gram = Grammar(gram_dict['start'], gram_dict['other'])	
	gram.normalize()
	print gram
#	print get_first_set_multi(gram, [fact.create_unterminal('C'), fact.create_acc()])
	return
	for t in gram.ut_tokens:
		print t, get_first_set(gram, t)

if __name__ == '__main__':
	main()
