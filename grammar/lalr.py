#-*- coding: utf-8 -*-
import grammar
import express
import tokens
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
		for token, to_state in edges.iteritems():
			if itm.get_id() not in dump_actions:
				dump_actions[itm.get_id()] = dict()
			if to_state[0] == lr1.ACTION_ACC:
				dump_actions[itm.get_id()][repr(token)] = 'ACTION_ACC'
			if to_state[0] == lr1.ACTION_SHIFT:
				dump_actions[itm.get_id()][repr(token)] = \
					('ACTION_SHIFT', to_state[1].get_id())
			if to_state[0] == lr1.ACTION_REDUCE:
				dump_actions[itm.get_id()][repr(token)] = \
					('ACTION_REDUCE', \
					to_state[1].get_simple_repr(), \
					len(to_state[1].get_right_tokens()))

	for itm, edges in gotos.iteritems():
		for token, to_state in edges.iteritems():
			if itm.get_id() not in dump_gotos:
				dump_gotos[itm.get_id()] = dict()
			dump_gotos[itm.get_id()][repr(token)] = to_state.get_id()
	return dump_start, dump_actions, dump_gotos	

#TODO(kdy): add logs
def try_solve_conflect(action_tbl):
	for from_itm, edges in action_tbl.iteritems():
		for token, to_items in edges.iteritems():
			new_to_item = None
			for itm in to_items:
				if new_to_item is None:
					new_to_item = itm
					continue
				#impossible to find a conflict on accept-state
				if itm[0] == lr1.ACTION_ACC:
					new_to_item = (lr1.ACTION_ACC, )
					break
				elif itm[0] == lr1.ACTION_REDUCE: 
					#reduce-reduce conflect
					if new_to_item[0] == lr1.ACTION_REDUCE:
						if new_to_item[1].piority < itm[1].piority:
							new_to_item = itm
					#reduce-shift conflect
					elif new_to_item[0] == lr1.ACTION_SHIFT:
						if token.piority < itm[1].piority:
							new_to_item = itm
						elif token.piority == itm[1].piority:
						#if current token is left asso and meets a 
						#reduce_conflect with a product which has equal
						#piority, use reduce
							if token.asso == tokens.ASSOC_LEFT:
								new_to_item = itm
					else :
						assert False
				elif itm[0] == lr1.ACTION_SHIFT:
					#reduce-shift conflect
					if new_to_item[0] == lr1.ACTION_REDUCE:
						if new_to_item[1].piority < token.piority:
							new_to_item = itm
						elif new_to_item[1].piority == token.piority:	
							if token.asso == tokens.ASSOC_RIGHT:
								new_to_item = itm
					#shift-shift can never gen a conflect
			action_tbl[from_itm][token] = new_to_item
	
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

def dump_dot_string(action_dict, goto_dict, dot_path):
	ret = """digraph "%s" {
			rankdir=LR;
			size="%s,%s"
			node [shape = box];
			%s
			}
	"""	
	trans_list = []
	for k, v in action_dict.iteritems():
		for sub_k, sub_v in v.iteritems():
			if sub_v[0] != lr1.ACTION_SHIFT:
				continue
			frm = '"%s"' % ''.join(['%s\\n' %  repr(itm) for itm in k.get_sorted_items()])
			to = '"%s"' % ''.join(['%s\\n' % repr(itm) for itm in sub_v[1].get_sorted_items()])
			trans_list.append((frm, to, repr(sub_k)))
	for k, v in goto_dict.iteritems():
		for sub_k, sub_v in v.iteritems():
			frm = '"%s"' % ''.join(['%s\\n' %  repr(itm) for itm in k.get_sorted_items()])
			to = '"%s"' % ''.join(['%s\\n' % repr(itm) for itm in sub_v.get_sorted_items()])
			trans_list.append((frm, to, repr(sub_k)))
	trans = '\n'.join(['%s -> %s [ label = %s ];' % itm for itm in trans_list])
	ret = ret % ('LALR1', 40, 40, trans, )
	fd = open(dot_path, 'w')
	fd.write(ret)
	fd.close()	

def gen_parsetbl(gram, fp, dot_path = None):
	all_items, raw_goto = lr1.get_lr1_relation(gram)
	action_dict, goto_dict = lr1.get_parse_table(gram, all_items, raw_goto)	
	m_items, m_a_dict, m_g_dict = merge_lr1(all_items, action_dict, goto_dict)
	try_solve_conflect(m_a_dict)
	if dot_path is not None:
		dump_dot_string(m_a_dict, m_g_dict, dot_path)
	s_start, s_as, s_gs = simplify_lalr(gram, m_items, m_a_dict, m_g_dict)
	dump(s_start, s_as, s_gs, fp)


def parse(text, parse_tbl):
	cnt = 0
	a_tbl = parse_tbl['action_tbl']
	g_tbl = parse_tbl['goto_tbl']
	stk = [str(parse_tbl['start'])]
	while text:
		s = stk[-1]		
		if a_tbl[s][text[0]][0] == 'ACTION_SHIFT':
			stk.append(str(a_tbl[s][text[0]][1]))
			text = text[1 : ]
		elif a_tbl[s][text[0]][0] == 'ACTION_REDUCE':
			token_0, token_1 = a_tbl[s][text[0]][1].split('->')
			token_num = a_tbl[s][text[0]][2]
			stk = stk[ : -token_num]
			stk.append(str(g_tbl[stk[-1]][token_0]))
			print token_0, '->', token_1
		elif a_tbl[s][text[0]][0] == 'ACTION_ACC':
			print 'parse done'
			break
		else :
			print 'error'
			break

