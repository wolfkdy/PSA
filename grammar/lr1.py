#-*- coding: utf-8 -*-

import grammar
from tokens import token_factory as fact
from express import express_factory

ACTION_REDUCE = 0
ACTION_SHIFT = 1
ACTION_ACC = 2

LR1_ITEMSET_ID = 0
class Lr1ItemSet(object):
	def __init__(self, item_set):
		self.item_set = item_set
		self.__id = None

	def set_id(id):
		self.__id = id

	def __repr__(self):
		lst = [repr(itm) for itm in self.item_set]
		lst.sort()
		s = ' '.join(lst)
		return s + '\n'

itemset_factory = None
class Lr1ItemSetFactory(object):
	def __init__(self):
		self.item_set_dict = {}
		self.id2item_set = {}
		self.cnt = 0

	def create_lr1_itemset(self, itms):
		itm_set = Lr1ItemSet(itms)
		key = repr(itm_set)
		if key not in self.item_set_dict:
			self.item_set_dict[key] = itm_set
			itm_set.set_id(self.cnt)
			self.id2item_set[self.cnt] = itm_set
			self.cnt += 1

		return self.item_set_dict[key]

	def get_itemset(self, id):
		return self.id2item_set.get(id)
	
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

def get_lr1_relation(g):
	exp = g.get_first_express()
	lr1_exp = express_factory.create_lr1(exp.left_token, exp.right_tokens_list[0], 0, \
			set([fact.create_acc()]))
	c = closure(g, itemset_factory.create_lr1_itemset(set([lr1_exp])))
	q = [c]
	visited = set([c])
	GOTO = dict()
	all_tokens = fact.get_all_tokens()
	while len(q) > 0:
		tmp = q[0]
		q = q[1: ]
		for token in all_tokens:
			reached = goto(g, tmp, token)
			if len(reached.item_set) > 0 and reached not in visited:
				visited.add(reached)
				q.append(reached)
			if tmp not in GOTO:
				GOTO[tmp] = dict()
			GOTO[tmp][token] = reached
	return visited, GOTO

def get_parse_table(g, item_sets, raw_GOTO):
	ACTION = {}
	GOTO = {}
	for itmset in item_sets:
		for exp in itmset.item_set:
			token = exp.get_token_after_dot()
			if not tokens.is_terminal(token):
				continue
			to_state = raw_GOTO.get(itmset, {}).get(token)
			if to_state is None:
				continue
			if itmset not in ACTION:
				ACTION[itmset] = {}
			if token not in ACTION[itmset]:
				ACTION[itmset][token] = set()
			ACTION[itmset][token].add((ACTION_SHIFT, to_state))

	for itmset in item_sets:
		for exp in itmset.item_set:
			if exp.is_pending_reduce():
				left = exp.left_token
				if left != g.start_token:
					if itmset not in ACTION:
						ACTION[itmset] = {}
					#TODO(kdy): grammar is expanded before building lr1 item set, and acc tokens are not merged when building closure, so the for loop gets only one token, may be a bad design ?
					for acc in exp.acc_tokens:
						if acc not in ACTION[itmset]:
							ACTION[itmset][acc] = set()
						ACTION[itmset][acc].add((ACTION_REDUCE, exp))	
				else :
					if itmset not in ACTION:
						ACTION[itmset] = {}
					lst = list(exp.acc_tokens)
					assert (len(lst) == 1 and tokens.is_acc(lst[0]))
					if lst[0] not in ACTION[itmset]:
						ACTION[itmset][lst[0]] = set()
					ACTION[itmset][lst[0]].add((ACTION_ACC, ))
	return ACTION

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
	all_items, raw_goto = get_lr1_items(gram)
	GOTO, ACTION = get_parse_table(gram, all_items, raw_goto)	
	for itm in get_lr1_items(gram):
		print itm
	
if __name__ == '__main__':
	main()
