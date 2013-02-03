#-*- coding: utf-8 -*-
import grammar
import express
import lr1
from lr1 import itemset_factory
from express import express_factory

#receive two lr1 item_sets and judge if same core
def is_same_core(itm_a, itm_b):
	itm_lst_a = itm_a.to_acc_merged_form().get_sorted_items()
	itm_lst_b = itm_b.to_acc_merged_form().get_sorted_items()
	if len(itm_lst_a) != len(itm_lst_b):
		return False
	for i in xrange(len(itm_lst_a)):
		if not express.is_same_core(itm_lst_a[i], itm_lst_b[i]):
			return False
	return True


def merge(item_list):
	#TODO: debug mode assert item_list are same_core ?		
	item_list_sample = item_list[0].to_acc_merged_form().get_sorted_items()
	item_list_merged = [item.to_acc_merged_form().get_sorted_items() for item in item_list]
	new_item_set = set()
	for i in xrange(len(item_list_sample)):
		acc_tokens_set = set()
		for j in xrange(len(item_list_merged)):
			acc_tokens_set = acc_tokens_set.union(item_list_merged[j][i].acc_tokens)
		new_item_set.add(express_factory.create_lr1(item_list_sample[i].left_token, \
			item_list_sample[i].get_right_tokens(), \
			item_list_sample[i].dot_pos, \
			acc_tokens_set))
	ret = itemset_factory.create_lr1_itemset(new_item_set)
	return ret

def merge_lr1(all_items, action_tbl, goto_tbl):
	itm2newitm = dict()	
	merged = set()
	all_item_list = list(all_items)

	new_all_items = set()
	new_action_tbl = dict()
	new_goto_tbl = dict()
	for i in xrange(len(all_item_list)):
		if all_item_list[i] in merged:
			continue
		lst = [all_item_list[i]]
		for j in xrange(i + 1, len(all_item_list)):
			'''
			print all_item_list[i]
			print all_item_list[j]
			print is_same_core(all_item_list[i], \
				all_item_list[j])
			'''
			if is_same_core(all_item_list[j], all_item_list[i]):
				lst.append(all_item_list[j])
		merged_item = merge(lst)
		for itm in lst:
			itm2newitm[itm] = merged_item
			merged.add(itm)
		new_all_items.add(merged_item)
	for from_item, edges in action_tbl.iteritems():
		new_from_item = itm2newitm[from_item]
		for token, to_item_set in edges.iteritems():
			for to_item in to_item_set:
				if to_item[0] == lr1.ACTION_SHIFT:
					new_to_item = itm2newitm[to_item[1]]
					if new_from_item not in new_action_tbl:
						new_action_tbl[new_from_item] = dict()
					if token not in new_action_tbl[new_from_item]:
						new_action_tbl[new_from_item][token] = set()
					new_action_tbl[new_from_item][token].add((lr1.ACTION_SHIFT, new_to_item))
				elif to_item[0] == lr1.ACTION_REDUCE:
					if new_from_item not in new_action_tbl:
						new_action_tbl[new_from_item] = dict()
					if token not in new_action_tbl[new_from_item]:
						new_action_tbl[new_from_item][token] = set()
					new_action_tbl[new_from_item][token].add((lr1.ACTION_REDUCE, to_item[1]))
				elif to_item[0] == lr1.ACTION_ACC:
					if new_from_item not in new_action_tbl:
						new_action_tbl[new_from_item] = dict()
					if token not in new_action_tbl[new_from_item]:
						new_action_tbl[new_from_item][token] = set()
					new_action_tbl[new_from_item][token].add((lr1.ACTION_ACC, ))

	for from_item, edges in goto_tbl.iteritems():
		new_from_item = itm2newitm[from_item]
		for token, to_item in edges.iteritems():
			new_to_item = itm2newitm[to_item]
			if new_from_item not in new_goto_tbl:
				new_goto_tbl[new_from_item] = dict()
			new_goto_tbl[new_from_item][token] = new_to_item
	return new_all_items, new_action_tbl, new_goto_tbl

def simplify_lalr(gram, all_items, actions, gotos):
	dump_start = None
	dump_actions = dict()
	dump_gotos = dict()
	def get_start_state():
		for itm in all_items:
			for exp in itm.item_set:	
				if exp.left_token == gram.start_token and exp.dot_pos == 0:
					return itm.get_id()
	dump_start = get_start_state()
	for itm, edges in actions.iteritems():
		for token, to_states in edges.iteritems():
			if itm.get_id() not in dump_actions:
				dump_actions[itm.get_id()] = dict()
			if repr(token) not in dump_actions[itm.get_id()]:
				dump_actions[itm.get_id()][repr(token)] = []
			for to_state in to_states:
				if to_state[0] == lr1.ACTION_ACC:
					dump_actions[itm.get_id()][repr(token)]. \
						append(('ACTION_ACC'))
				if to_state[0] == lr1.ACTION_SHIFT:
					append_itm = ('ACTION_SHIFT', to_state[1].get_id())
					if append_itm not in dump_actions[itm.get_id()][repr(token)]:
						dump_actions[itm.get_id()][repr(token)]. \
							append(append_itm)
				if to_state[0] == lr1.ACTION_REDUCE:
					append_itm = ('ACTION_REDUCE', to_state[1].get_simple_repr())
					dump_actions[itm.get_id()][repr(token)]. \
						append(append_itm)
	for itm, edges in gotos.iteritems():
		for token, to_state in edges.iteritems():
			if itm.get_id() not in dump_gotos:
				dump_gotos[itm.get_id()] = dict()
			dump_gotos[itm.get_id()][repr(token)] = to_state.get_id()
	return dump_start, dump_actions, dump_gotos	

def dump(start, actions, gotos, fp):
	import json
	fd = open(fp, 'w')
	json.dump({ \
		'TABLE_TYPE' : 'LALR1',
		'start' : start, \
		'action_tbl' : actions, 
		'goto_tbl' : gotos}, 
		fd, 
		indent = 8)

def gen_parsetbl(gram, fp):
	all_items, raw_goto = lr1.get_lr1_relation(gram)
	action_dict, goto_dict = lr1.get_parse_table(gram, all_items, raw_goto)	
	m_items, m_a_dict, m_g_dict = merge_lr1(all_items, action_dict, goto_dict)
	for m_item in m_items:
		print m_item
	print '\n'
	print m_a_dict
	s_start, s_as, s_gs = simplify_lalr(gram, m_items, m_a_dict, m_g_dict)
	dump(s_start, s_as, s_gs, fp)

def main():
	gram_dict = {
		'start' : 'S->CC',
		'other' : ['C->cC|d']
	}
	'''
	gram_dict = {
		'start' : 'S->L=R|R',
		'other' : ['L->*R|d', 'R->L']
	}
	gram_dict = {
		'start' : 'S->SS+|SS*|a',
		'other' : [],
	}
	'''
	gram = grammar.Grammar(gram_dict['start'], gram_dict['other'])
	gram.normalize()
	all_items, raw_goto = lr1.get_lr1_relation(gram)
	action_dict, goto_dict = lr1.get_parse_table(gram, all_items, raw_goto)	
	print action_dict
	print '?????'
	m_items, m_a_dict, m_g_dict = merge_lr1(all_items, action_dict, goto_dict)
	s_start, s_as, s_gs = simplify_lalr(gram, m_items, m_a_dict, m_g_dict)
	dump(s_start, s_as, s_gs, './parsetab')
	print d_items
	print d_as
	print d_gs

if __name__ == '__main__':
	main()


