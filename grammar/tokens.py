#-*- coding: utf-8 -*-

TOKEN_TYPE_TERMINAL = 0
TOKEN_TYPE_UNTERMINAL = 1
TOKEN_TYPE_DOT = 2

ASSOC_LEFT = 'left'
ASSOC_RIGHT = 'right'

class Token(object):
	def __init__(self, text):
		self.text = text

	def __repr__(self):
		return self.text

class Terminal(Token):
	def __init__(self, text, asso, piority):
		super(Terminal, self).__init__(text)
		self.asso = asso
		self.piority = piority
		
class Unterminal(Token):
	def __init__(self, text):
		super(Unterminal, self).__init__(text)

class AccToken(Token):
	def __init__(self):
		super(AccToken, self).__init__('$')
		self.piority = 0
		self.asso = ASSOC_LEFT

# ε can not be used as terminal token at current
class Epsilon(Token):
	def __init__(self):
		super(Epsilon, self).__init__('ε')

class TokenFactory(object):
	def __init__(self):
		self.terminal_tokens = dict()
		self.unterminal_tokens = dict()
		self.shared_epsilon = Epsilon()
		self.shared_acc = AccToken()
		self.spawn_info = dict()

	def set_token_spawn_info(self, left_p, right_p, none_asso = []):
		#todo : deal with none_associate terminal tokens	
		for token, p in left_p:
			self.spawn_info[token] = (ASSOC_LEFT, p)
		for token, p in right_p:
			self.spawn_info[token] = (ASSOC_RIGHT, p)

	def get_all_tokens(self):
		return self.terminal_tokens.values() + self.unterminal_tokens.values()

	def create_terminal(self, text):
		if text not in self.terminal_tokens:
			spawn_info = self.spawn_info.get(text, (ASSOC_LEFT, 0))
			self.terminal_tokens[text] = Terminal(text, spawn_info[0], spawn_info[1])
		return self.terminal_tokens[text]
		
	def create_unterminal(self, text):
		if text not in self.unterminal_tokens:
			self.unterminal_tokens[text] = Unterminal(text)
		return self.unterminal_tokens[text]

	def create_epsilon(self):
		return self.shared_epsilon

	def create_acc(self):
		return self.shared_acc

token_factory = None
def token_factory_init():
	global token_factory
	token_factory = TokenFactory()

def is_terminal(obj):
	return isinstance(obj, (Terminal, AccToken))

def is_unterminal(obj):
	return isinstance(obj, [AccToken, Unterminal])

def is_acc(obj):
	return isinstance(obj, AccToken)

def is_epsilon(obj):
	return isinstance(obj, Epsilon)

def is_token(obj):
	return isinstance(obj, Token)

token_factory_init()
