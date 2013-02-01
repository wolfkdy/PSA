#-*- coding: utf-8 -*-
import express

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
	accs = set()
	pass

def merge_lr1(all_items, action_tbl, goto_tbl):
	itm2newitm = dict()	
	merged = set()
	all_items_list = list(all_items)
	for i in xrange(len(all_item_list)):
		if all_item_list[i] in merged:
			continue
		lst = [all_item_list[i]]
		for j in xrange(i + 1, len(all_item_list)):
			if is_same_core(all_item_list[j], all_item_list[i]):
				lst.append(all_item_list[j])
		merged_item = merge(lst)

	'''
	for item in all_items:
		if item in merged:
			continue
		lst = [item]
		for
	'''

def main():
	gram_dict = {
		'start' : 'S->CC',
		'other' : ['C->cC|d']
	}
	gram = grammar.Grammar(gram_dict['start'], gram_dict['other'])
	gram.normalize()
	all_items, raw_goto = get_lr1_relation(gram)
	action_dict, goto_dict = get_parse_table(gram, all_items, raw_goto)	
	m_items, m_a_dict, m_g_dict = merge_lr1(all_items, action_dict, goto_dict)

if __name__ == '__main__':
	main()


