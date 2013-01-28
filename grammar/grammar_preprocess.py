#-*- coding: utf-8 -*-

#class Grammar describes a grammar which begins with @start@ 

class Token(object):
	def __init__(self, text, is_terminal):
		self.is_terminal = is_terminal
		self.text = text

	def __repr__(self):
		return self.text

class TokenFactory(object):
	def __init__(self):
		self.terminal_tokens = dict()
		self.unterminal_tokens = dict()
		
	def create_terminal_token(self, text):
		if text not in self.terminal_tokens:
			self.terminal_tokens[text] = Token(text, True)
		return self.terminal_tokens[text]
		
	def create_unterminal_token(self, text):
		if text not in self.unterminal_tokens:
			self.unterminal_tokens[text] = Token(text, False)
		return self.unterminal_tokens[text]

g_token_factory = None
def token_factory():
	global g_token_factory
	if g_token_factory is None:
		g_token_factory = TokenFactory()
	return g_token_factory

class Express(object):
	def __init__(self, left_token, right_tokens_list):
		self.left_token = left_token
		self.right_tokens_list = right_tokens_list

	def __repr__(self):
		str_lst = []
		for tokens in self.right_tokens_list:
			str_lst.append(''.join([repr(token) for token in tokens]))
		
		return '%s->%s' % (repr(self.left_token), '|'.join(str_lst), )

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
			self.ut_tokens.add(token_factory().create_unterminal_token(left))
		left, right = start.split('->')
		self.start_token = token_factory().create_unterminal_token(left)
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
						tokens.append(token_factory().create_terminal_token(right_text[i]))
						i += 1
					else :
						tokens.append(token_factory().create_unterminal_token(s))
						i += len(s)
				tokens_list.append(tokens)
			self.expresses.append(Express(token_factory().create_unterminal_token(_), 				tokens_list))

	def __repr__(self):
		lst = [repr(itm) for itm in self.expresses ]
		return '\n'.join(lst)

	def augment(self):
		if self.is_augmented:
			return
		tmp = self.start_token
		self.start_token = token_factory().create_unterminal_token(self.start_token.text + "'")	
		self.expresses.append(Express(self.start_token, [[tmp]]))
		self.is_augmented = True

if __name__ == '__main__':
	gram_dict = {
		'start' : 'S->CC',
		'other' : ['C->cC|d']
	}
	gram = Grammar(gram_dict['start'], gram_dict['other'])	
	gram.augment()
	print repr(gram)
