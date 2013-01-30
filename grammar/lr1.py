#-*- coding: utf-8 -*-

import grammar
from express import express_factory

LR1_ITEMSET_ID = 0
class Lr1ItemSet(object):
	def __init__(self, item_set):
		self.item_set = item_set


itemset_factory = None
class Lr1ItemSetFactory(object):
	def __init__(self):
		pass

	def create_lr1_itemset(self, itms):
		return Lr1ItemSet(itms)

def itemset_factory_init():
	global itemset_factory
	itemset_factory = Lr1ItemSetFactory()

#receive a lr1_express_list
def closure(g, itms):
	visited = set()
	q = list()
	for itm in itms.item_set:
		visited.add(itm)
		q.append(itm)
	while len(q) > 0:
		tmp = q[0]
		q = q[1 : ]
		token = tmp.get_token_after_dot()	
		look_ahead = tmp.get_token_lookahead_dot()
		exps = g.get_expresses_by_left(token)
		for exp in exps:
			for acc in tmp.acc_tokens:
				terminal_tokens = grammar.get_first_set_multi(g, [look_ahead, acc])
				for term in terminal_tokens:
					new_exp = express_factory.create_lr1(tmp.left_token,
						exp.right_tokens_list[0], 0, set(term))
					if new_exp not in visited:
						visited.add(new_exp)
						g.append(new_exp)
	return itemset_factory.create_lr1_itemset(visited)


'''
# S -> A dot Bc, a/b
# left : S , right : A dot Bc, acc_set : a/b, dot_pos : 1

def build_normal_lr1_item_set(gram):
'''	
