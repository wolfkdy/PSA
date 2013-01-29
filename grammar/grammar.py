#-*- coding: utf-8 -*-

from tokens import token_factory as fact
from express import Express

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
		for itm in others:
			_, right = itm.split('->')
			right_text_list = right.split('|')
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
			self.expresses.append(Express(fact.create_unterminal(_),tokens_list))

	def __repr__(self):
		lst = [repr(itm) for itm in self.expresses ]
		return '\n'.join(lst)

	def get_expresses_by_left(self, left):
		lst = []
		for exp in self.expresses:
			if exp.left_token == left:
				lst.append(exp)
		return lst

	def augment(self):
		if self.is_augmented:
			return
		tmp = self.start_token
		self.start_token = fact.create_unterminal(self.start_token.text + "'")	
		self.expresses.append(Express(self.start_token, [[tmp]]))
		self.is_augmented = True

	# expand all expresses concated with '|'
	def expand(self):
		old_lst = self.expresses
		new_lst = []
		for itm in old_lst:
			new_lst.extend(itm.get_expand_form())
		self.expresses = new_lst

if __name__ == '__main__':
	gram_dict = {
		'start' : 'S->CC',
		'other' : ['C->cC|d']
	}
	gram = Grammar(gram_dict['start'], gram_dict['other'])	
	gram.augment()
	gram.expand()
	print repr(gram)
