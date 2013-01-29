#-*- coding: utf-8 -*-

from express import Express
from tokens import token_factory as fact

#every lr1_express is an expanded node
class LR1_Express(Express):
	def __init__(self, left_token, right_tokens, dot_pos, receive_chars):
		super(LR1_Express, self).__init__(left_token, [right_tokens])
		self.dot_pos = dot_pos
		self.receive_tokens = set()
		for ch in receive_chars:
			self.receive_tokens.add(fact.create_terminal(ch))

LR1_ITEMSET_ID = 0
class LR1_ItemSet(object):
	def __init__(self):
		self.expresses = list()
		self.edges = dict()



def closure(express_lst):
	
# S -> A dot Bc, a/b
# left : S , right : A dot Bc, acc_set : a/b, dot_pos : 1

def build_normal_lr1_item_set(gram):
	
