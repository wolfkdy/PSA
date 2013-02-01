#-*- coding: utf-8 -*-
import grammar
import express
import lr1
from lr1 import itemset_factory
from express import express_factory

def is_same_core(itm_a, itm_b):
	itm_lst_a = itm_a.get_sorted_items()
	itm_lst_b = itm_b.get_sorted_items()
	if len(itm_lst_a) != len(itm_lst_b):
		return False
	for i in xrange(len(itm_lst_a)):
		if not express.is_same_core(itm_lst_a[i], itm_lst_b[i]):
			return False
	return True

def merge(item_list):
	#TODO: debug mode assert item_list are same_core ?		
	item = item_list[0]
	sample = set()
	for exp in item.item_set:
		tmp = express_factory.create_lr1(exp.left_token, exp.get_right_tokens(), \
				exp.dot_pos, exp.acc_tokens)
		sample.add(tmp)
	new_itmset = itemset_factory.create_lr1_itemset(sample)	
	new_itmset_list = new_itmset.get_sorted_items()
	for i in xrange(len(new_itmset_list)):
		acc_tokens = new_itmset_list[i].acc_tokens
		for _item in item_list:
			acc_tokens = acc_tokens.union(_item.get_sorted_items()[i].acc_tokens)
		new_itmset_list[i].acc_tokens = acc_tokens
	print item_list
	print new_itmset
	print 'debug'
	return new_itmset

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

def main():
	gram_dict = {
		'start' : 'S->CC',
		'other' : ['C->cC|d']
	}
	gram = grammar.Grammar(gram_dict['start'], gram_dict['other'])
	gram.normalize()
	all_items, raw_goto = lr1.get_lr1_relation(gram)
	action_dict, goto_dict = lr1.get_parse_table(gram, all_items, raw_goto)	
	m_items, m_a_dict, m_g_dict = merge_lr1(all_items, action_dict, goto_dict)
	for item in m_items:
		print item
	return
	print m_items, m_a_dict, m_g_dict

if __name__ == '__main__':
	main()


