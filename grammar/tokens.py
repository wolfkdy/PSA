#-*- coding: utf-8 -*-

TOKEN_TYPE_TERMINAL = 0
TOKEN_TYPE_UNTERMINAL = 1
TOKEN_TYPE_DOT = 2

class Token(object):
	def __init__(self, text):
		self.text = text

	def __repr__(self):
		return self.text

class Terminal(Token):
	def __init__(self, text):
		super(Terminal, self).__init__(text)

class Unterminal(Token):
	def __init__(self, text):
		super(Unterminal, self).__init__(text)

# ε can not be used as terminal token at current
class Epsilon(Token):
	def __init__(self):
		super(Eps, self).__init__('ε')

class TokenFactory(object):
	def __init__(self):
		self.terminal_tokens = dict()
		self.unterminal_tokens = dict()
		self.shared_epsilon = Epsilon()

	def create_terminal(self, text):
		if text not in self.terminal_tokens:
			self.terminal_tokens[text] = Terminal(text)
		return self.terminal_tokens[text]
		
	def create_unterminal(self, text):
		if text not in self.unterminal_tokens:
			self.unterminal_tokens[text] = Unterminal(text)
		return self.unterminal_tokens[text]

	def create_epsilon(self):
		return self.shared_epsilon

token_factory = None
def token_factory_init():
	global token_factory
	token_factory = TokenFactory()

def is_terminal(obj):
	return isinstance(obj, Terminal)

def is_unterminal(obj):
	return isinstance(obj, Unterminal)

def is_epsilon(obj):
	return isinstance(obj, Epsilon)

def is_token(obj):
	return isinstance(obj, Token)

token_factory_init()
