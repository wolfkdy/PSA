#-*- coding: utf-8 -*-

import grammar
from tokens import token_factory as fact
from express import express_factory

LR1_ITEMSET_ID = 0
class Lr1ItemSet(object):
	def __init__(self, item_set):
		self.item_set = item_set

	def __repr__(self):
		lst = [repr(itm) for itm in self.item_set]
		lst.sort()
		s = ' '.join(lst)
		return s + '\n'

itemset_factory = None
class Lr1ItemSetFactory(object):
	def __init__(self):
		self.item_set_dict = {}

	def create_lr1_itemset(self, itms):
		itm_set = Lr1ItemSet(itms)
		key = repr(itm_set)
		if key not in self.item_set_dict:
			self.item_set_dict[key] = itm_set
		return self.item_set_dict[key]

def itemset_factory_init():
	global itemset_factory
	itemset_factory = Lr1ItemSetFactory()

itemset_factory_init()

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
					new_exp = express_factory.create_lr1(token,
						exp.right_tokens_list[0], 0, set([term]))
					if new_exp not in visited:
						visited.add(new_exp)
						q.append(new_exp)
	return itemset_factory.create_lr1_itemset(visited)

def goto(g, itms, trans_token):
	ret = set()
	for itm in itms.item_set:
		if itm.get_token_after_dot() == trans_token:
			new_itm = express_factory.create_lr1(itm.left_token, \
					itm.get_right_tokens(), itm.dot_pos + 1, itm.acc_tokens)
			ret.add(new_itm)	
	retset = itemset_factory.create_lr1_itemset(ret)
	return closure(g, retset)

def get_lr1_items(g):
	exp = g.get_first_express()
	lr1_exp = express_factory.create_lr1(exp.left_token, exp.right_tokens_list[0], 0, \
			set([fact.create_acc()]))
	c = closure(g, itemset_factory.create_lr1_itemset(set([lr1_exp])))
	q = [c]
	visited = set([c])
	all_tokens = fact.get_all_tokens()
	while len(q) > 0:
		tmp = q[0]
		q = q[1: ]
		for token in all_tokens:
			reached = goto(g, tmp, token)
			if len(reached.item_set) > 0 and reached not in visited:
				visited.add(reached)
				q.append(reached)
	return visited
				
'''
# S -> A dot Bc, a/b
# left : S , right : A dot Bc, acc_set : a/b, dot_pos : 1

def build_normal_lr1_item_set(gram):
'''

def main():
	gram_dict = {
		'start' : 'S->CC',
		'other' : ['C->cC|d']
	}
	gram = grammar.Grammar(gram_dict['start'], gram_dict['other'])
	gram.normalize()
	print get_lr1_items(gram)
	return 
	for itm in get_lr1_items(gram):
		print itm
	
if __name__ == '__main__':
	main()
