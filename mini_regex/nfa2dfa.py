#-*- coding: utf-8 -*-

DFA_CNT = 0
class DFA_Node(object):
	def __init__(self, nfa_nodes):
		global DFA_CNT
		self.nfa_nodes = nfa_nodes
		self.index = DFA_CNT
		DFA_CNT += 1

	def __repr__(self):
		lst = list(self.nfa_nodes)
		lst.sort()
		ret_lst = []
		for itm in lst:
			ret_lst.append(str(itm.index))
			ret_lst.append(',')
		return ''.join(ret_lst)

	def get_identity(self):
		return self.__repr__()

#given the start state of thompson automata, return the dfa
def construct_subsets(s):
	s.print_graph()
	s_eps_closure = DFA_Node(get_eps_closure_single(s.start))
	tabu = set()
	tabu.add(s_eps_closure.get_identity())
	q = []
	q.append(s_eps_closure)
	graph = dict()
	#start state is unique, while end state can be diversity
	dfa_start, dfa_end = None, set()
	while len(q) != 0:
		tmp = q[0]
		q = q[1 : ]
		if s.start in tmp.nfa_nodes:
			dfa_start = tmp.get_identity()
		if s.end in tmp.nfa_nodes:
			dfa_end.add(tmp.get_identity())
		for input in get_input_multi(tmp):
			goto_states = DFA_Node(get_eps_closure_multi(get_move_multi(tmp, input)))
			if goto_states.get_identity() not in tabu:
				q.append(goto_states)
				tabu.add(goto_states.get_identity())
				if goto_states.get_identity() not in graph:
					graph[goto_states.get_identity()] = dict()
			if tmp.get_identity() not in graph:
				graph[tmp.get_identity()] = dict()
			graph[tmp.get_identity()][input] = goto_states.get_identity()
	return graph, dfa_start, dfa_end

# get the eps closure of a nfa state
def get_eps_closure_single(s):
	tabu = set()
	tabu.add(s)
	q = []
	q.append(s)
	while len(q) > 0:
		tmp = q[0]
		q = q[1 : ]
		for itm in tmp.eps_set:
			if itm in tabu:
				continue
			tabu.add(itm)
			q.append(itm)
	return tabu

#this is a slow implement, 
#a better way is to do push all states of s into a queue, then search
def get_eps_closure_multi(s):
	ret = set()
	for itm in s:
		ret = ret.union(get_eps_closure_single(itm))
	return ret

#receive a dfa,
#return a set of terminal chars that it can receive
def get_input_multi(s):
	ret = set()
	for itm in s.nfa_nodes:
		ret = ret.union(itm.edges.keys())
	return ret

#receive a dfa_node and a terminal char
#return a set of nfa_nodes which can be reached by a trans from s
def get_move_multi(s, a):
	lst = []
	for itm in s.nfa_nodes:
		t = itm.edges.get(a)
		if t is not None:
			lst.append(t)
	return lst


