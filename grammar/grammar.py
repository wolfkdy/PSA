#-*- coding: utf-8 -*-

import tokens
from tokens import token_factory as fact
from express import express_factory as e_fact


def get_first_set_multi(gram, tokens):
	g = gram.normalized_mode
	ret = set()
	eps_token = fact.create_epsilon()
	for token in tokens:
		token_set = get_first_set(gram, token)
		ret = ret.union(token_set)
		if eps_token not in token_set:
			if eps_token in ret:
				ret.remove(eps_token)
			return ret
	return ret

#get token t's first set in grammar g
def get_first_set(gram, t):
	ret = set()
	g = gram.normalized_mode
	if tokens.is_terminal(t) or tokens.is_epsilon(t):
		ret.add(t)
		return ret
	eps_token = fact.create_epsilon()
	exps = g.get_expresses_by_left(t)
	for exp in exps:
		for _tokens in exp.right_tokens_list:
			tmp = get_first_set_multi(gram, _tokens)
			ret = ret.union(tmp)
	return ret

#leftmost match rule
#TODO(kdy): use aho-corasick automata to speedup this process
def split_text_by_ut_tokens(text, ut_set):
	i = 0
	tokens = []
	while i < len(text):
		left_most = len(text)
		ut_token = None
		for itm in ut_set:
			idx = text[i : ].find(itm.text)
			if idx == -1:
				continue
			idx += i
			if idx >= left_most:
				continue
			left_most = idx
			ut_token = itm
		if i != left_most:
			tokens.append(fact.create_terminal(text[i : left_most]))
		if ut_token != None:
			tokens.append(ut_token)
			i = left_most + len(ut_token.text)
		else :
			i = len(text)
	return tokens	

#class Grammar describes a grammar which begins with @start@ 
class Grammar(object):
	def __init__(self, start, others):
		self.is_augmented = False
		self.is_non_left_rec = False
		self.is_expanded = False
		self.normalized_mode = None
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
				tokens = split_text_by_ut_tokens(right_text, self.ut_tokens)
				tokens_list.append(tokens)
			self.expresses.append( \
					e_fact.create_simple( \
						fact.create_unterminal(left), tokens_list))

	#to a non-ambigous grammar, eliminate left recursive is ok, 
	#however, to an ambigous one, original information is lost when 
	#eliminating ambigous by priority of terminal tokens
	def eliminate_left_recursive(self):
		if self.is_non_left_rec:
			return
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
		self.is_non_left_rec = True

	def __repr__(self):
		lst = [repr(itm) for itm in self.expresses ]
		return '\n'.join(lst)

	def get_expresses_by_left(self, left):
		lst = []
		for exp in self.expresses:
			if exp.left_token == left:
				lst.append(exp)
		return lst

	#return the first express of a expanded grammar
	def get_first_express(self):
		assert self.is_expanded, 'get first express of a non-expanded grammar is meaningless'
		exps = self.get_expresses_by_left(self.start_token)
		return exps[0]

	def augment(self):
		if self.is_augmented:
			return
		tmp = self.start_token
		#create a different token for new start state
		self.start_token = fact.create_unterminal(self.start_token.text + "__S")	
		self.expresses.append(e_fact.create_simple(self.start_token, [[tmp]]))
		self.is_augmented = True

	def set_normalized_mode(self, gram):
		self.normalized_mode = gram

	# expand all expresses concated with '|'
	def expand(self):
		if self.is_expanded:
			return
		old_lst = self.expresses
		new_lst = []
		for itm in old_lst:
			new_lst.extend(itm.get_expand_form())
		self.expresses = new_lst
		self.is_expanded = True

	#prepare self for constructin lr(1)
	def normalize(self):
		self.augment()
		self.eliminate_left_recursive()
		self.expand()

def prepare_gram(gram_dict):
	fact.set_token_spawn_info( \
		gram_dict.get('left_piority', []), gram_dict.get('right_piority', []))
	n_gram = Grammar(gram_dict['start'], gram_dict['other'])
	n_gram.normalize()
	gram = Grammar(gram_dict['start'], gram_dict['other'])
	gram.augment()
	gram.expand()
	gram.set_normalized_mode(n_gram)
	return gram

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
	gram = prepare_gram(gram_dict)
	print gram
#	print get_first_set_multi(gram, [fact.create_unterminal('C'), fact.create_acc()])
	return
	for t in gram.ut_tokens:
		print t, get_first_set(gram, t)

if __name__ == '__main__':
	main()
