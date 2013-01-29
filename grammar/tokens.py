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

class Dot(Token):
	def __init__(self):
		super(Dot, self).__init__('.')

class TokenFactory(object):
	def __init__(self):
		self.terminal_tokens = dict()
		self.unterminal_tokens = dict()
		self.shared_dot = Dot()		

	def create_terminal(self, text):
		if text not in self.terminal_tokens:
			self.terminal_tokens[text] = Terminal(text)
		return self.terminal_tokens[text]
		
	def create_unterminal(self, text):
		if text not in self.unterminal_tokens:
			self.unterminal_tokens[text] = Unterminal(text)
		return self.unterminal_tokens[text]

	def create_dot(self):
		return self.shared_dot

token_factory = None
def token_factory_init():
	global token_factory
	token_factory = TokenFactory()

def is_terminal(obj):
	return isinstance(obj, Terminal)

def is_unterminal(obj):
	return isinstance(obj, Unterminal)

def is_dot(obj):
	return isinstance(obj, Dot)

def is_token(obj):
	return isinstance(obj, Token)

token_factory_init()
