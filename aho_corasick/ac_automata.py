
# Node represents a state, Node.next represents the edges, 
class Node(object):
	def __init__(self):
		self.next = {} # stores the edges to its children,
		self.f = 0 #the total number of samples which ends at this point
		self.fail = -1

class AC_AutoMata(object):
	def __init__(self):
		self.root = Node()	

	#no more than building a trie tree
	def insert_sample(self, text):
		p = self.root
		for ch in text:
			if p.next.get(ch, -1) == -1:
				p.next[ch] = Node()
			p = p.next[ch]
		p.f += 1	

	#use the broad first method to build the fail translation of each node, which can accumulate the
	#searching process
	def build_graph(self):
		q = []
		q.append(self.root)
		while len(q) > 0:
			t = q[0]
			q = q[1 : ]
			for k, v in t.next.iteritems():
				father = t.fail
				while father != -1 and father.next.get(k, -1) == -1:
					father = father.fail
				if father != -1:
					v.fail = father.next.get(k, -1)
				else :
					v.fail = self.root
				q.append(v)

	#visuallize the trie tree with fail translation
	def _print_tree(self, node, lvl, node_tag):
		blank = ['\t' for i in xrange(lvl)]
		print ''.join(blank), node_tag, '(self:', id(self), 'fail_ptr:', id(node.fail), ')'
		for k, v in node.next.iteritems():
			self._print_tree(v, lvl + 1, node_tag + k)
	
	def print_graph(self):
		self._print_tree(self.root, 0, '')

	# given a long text, calc how many samples occurs in it
	def find_occurs(self, text):
		father = self.root
		visited = set()
		i = 0
		while i < len(text):
			ch = text[i]
			p = father.next.get(ch, -1)
			if p != -1:
				visited.add(p)
				father = p
				i += 1
			else :
				while father != -1 and father.next.get(ch, -1) == -1:
					father = father.fail
					if father != -1 and father.f:
						visited.add(father)
				if father == -1:
					father = self.root
					i += 1
		cnt = 0
		for node in visited:
			cnt += node.f
		return cnt
				

	
