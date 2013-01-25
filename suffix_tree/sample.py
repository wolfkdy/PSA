# sample : find the longest common substring of str a and str b in linear time of len(a + b)
import suffix_tree

s1 = ''
s2 = '' 
gl_max = 0

def traverse(root, lt, leng, whichEdges):
	global s1, s2, gl_max
	f = [False, False]
	for k, v in root.left.iteritems():
		if root.descendants.get(k, 0) == 0:
			if root.left[k] <= len(s1):
				f[0] = True
				whichEdges[0] = True
			else :
				f[1] = True
				whichEdges[1] = True
		else :
			traverse(root.descendants[k], v, leng + (root.right[k] - root.left[k] + 1), f)
			if f[0]:
				whichEdges[0] = True
			if f[1]:
				whichEdges[1] = True
		if f[0] and f[1] and leng > gl_max:
			gl_max = leng

if __name__ == '__main__':
	global s1, s2
	tree = suffix_tree.UkkonenSuffixTree()
	s1 = 'yeshowmuchiloveyoumydearmotherreallyicannotbelieveit'
	s2 = 'yeaphowmuchiloveyoumydearmother'
	s1_s2 =  s1 + '{'  +  s2 + '|'
	tree.run(s1_s2)
	print s1_s2
	tree.printTree(0)
	f = [False, False]
	traverse(tree.root, 0, 0, f)
	print gl_max
