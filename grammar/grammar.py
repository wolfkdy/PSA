#-*- coding: utf-8 -*-

from tokens import token_factory as fact
from express import Express


#get token list's first set in grammar g
def get_first_set_multi(g, token_lst):
	pass

#get token t's first set in grammar g
def get_first_set(g, t):
	pass

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
	
#class Grammar describes a grammar which begins with @start@ 
class Grammar(object):
	def __init__(self, start, others):
		self.is_augmented = False
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
						i += 1
					else :
						tokens.append(fact.create_unterminal(s))
						i += len(s)
				tokens_list.append(tokens)
			self.expresses.append(Express(fact.create_unterminal(left), tokens_list))

	def _eliminate_left_recursive(self):
		old_ut_tokens = list(self.ut_tokens)
		new_ut_tokens = list()

		#new exps generated when eliminating the  immiate left recursive
		new_exps = []
		for i in xrange(len(old_ut_tokens)):
			exp_i = self.get_expresses_by_left(old_ut_tokens[i])
			assert len(exp_i) == 1
			exp_i = exp_i[0]
			for j in xrange(i - 1):
				exp_j = self.get_expresses_by_left(old_ut_tokens[j])
				#_eliminate_left_recursive is called before _expand,
				# so, use an assert to make sure logic is correct
				# notice, exps with same left part is merged in __init__
				assert len(exp_j) == 1
				exp_i.replace_leftmost_token(exp_j[0])
			if exp_i.is_left_recursive():
				new_exps.append(exp_i.eliminate_left_recursive())
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

	def _augment(self):
		if self.is_augmented:
			return
		tmp = self.start_token
		#create a different token for new start state
		self.start_token = fact.create_unterminal(self.start_token.text + "__S")	
		self.expresses.append(Express(self.start_token, [[tmp]]))
		self.is_augmented = True

	# expand all expresses concated with '|'
	def _expand(self):
		old_lst = self.expresses
		new_lst = []
		for itm in old_lst:
			new_lst.extend(itm.get_expand_form())
		self.expresses = new_lst

	#prepare self for constructin lr(1)
	def normalize(self):
		self._augment()
		self._eliminate_left_recursive()
#		self._expand()


if __name__ == '__main__':
	gram_dict = {
		'start' : 'S->CC',
		'other' : ['C->cC|d|Cc']
	}
	gram_dict = {
		'start' : 'A->Aa|b',
		'other' : [],
	}
	gram_dict = {
		'start' : 'A->Aa1|Aa2|Aa3|Aa4|Aa5|b1|b2|b3|b4|b5',
		'other' : [],
	}
	gram = Grammar(gram_dict['start'], gram_dict['other'])	
	gram.normalize()
	print repr(gram)
