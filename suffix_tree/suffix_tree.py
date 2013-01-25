#an implementation of ukkonen's algorithm http://en.wikipedia.org/wiki/Ukkonen%27s_algorithm
class SuffixTreeNode(object):
	def __init__(self):
		self.descendants = {}
		self.suffixLink = None
		self.left = {}
		self.right = {}

class UkkonenSuffixTree(object):
	def __init__(self):
		self.root = SuffixTreeNode()
		self.Lt = 1
		self.root.suffixLink = self.root
		self.endPoint = False
		self.text = None
		self.len = None

	def printTree(self, pos):
		self._printTree(self.root, 0, 0, 0, pos)

	#text pos ranges in [lt, rt]
	def _printTree(self, p, lvl, lt, rt, pos):
		blank = ''.join(['\t' for i in xrange(lvl)])
		if p != 0:  #if a none leaf
			if p == self.root:
				print blank, id(p)
			elif p.suffixLink != 0:
				print blank, self.text[lt : rt + 1], id(p), id(p.suffixLink), '[', lt, rt, ']'
			else:
				print blank, self.text[lt : pos + 1], id(p)
			for k, v in p.left.iteritems():
				self._printTree(p.descendants.get(k, 0), lvl + 1, p.left[k], p.right[k], pos)
		else :
			print blank, self.text[lt: rt + 1], '[', lt, rt ,']'

	def testAndSplit(self, p, i):
		Rt = i - 1
		if self.Lt <= Rt:
			pos = self.text[self.Lt]
			pp = p.descendants.get(pos, 0)
			lt = p.left[pos]
			rt = p.right[pos]
			if self.text[i] == self.text[lt + Rt - self.Lt + 1]:  # if test[lt ..rt] is an extension of text [Lt .. i]
				self.endPoint = True
				return p
			else :
				# insert a new node r between s and ss by splitting
				# edge(p, pp) = text[lt .. rt] into
				# edge(p, r) = text[lt, lt + Rt -Lt] and
				# edge(r, pp) = text[lt + Rt - Lt + 1 ..rt]
				pos = self.text[lt]
				p.descendants[pos] = SuffixTreeNode()
				r = p.descendants[pos]
				p.right[pos] = lt + Rt - self.Lt
				pos = self.text[lt + Rt - self.Lt + 1]
				r.descendants[pos] = pp
				r.left[pos] = lt + Rt - self.Lt + 1
				r.right[pos] = rt
				self.endPoint = False
				return r
		elif p.left.get(self.text[i]) is None:
			self.endPoint = False
		else :
			self.endPoint = True
		return p

	def findCanonicalNode(self, p, Rt):
		if Rt >= self.Lt:
			pos = self.text[self.Lt]
			pp = p.descendants.get(pos, 0)
			lt = p.left[pos]
			rt = p.right[pos]
			while rt - lt <= Rt - self.Lt:
				self.Lt = self.Lt + rt - lt + 1
				p = pp
				if self.Lt <= Rt:
					pos = self.text[self.Lt]
					pp = p.descendants.get(pos, 0)
					lt = p.left[pos]
					rt = p.right[pos]
					if p == self.root:
						pp = self.root
		return p

	def update(self, p, i):
		prev = 0
		r = self.testAndSplit(p, i)
		while not self.endPoint:
			pos = self.text[i]
			r.left[pos] = i
			r.right[pos] = self.len - 1
			if prev != 0:
				prev.suffixLink = r
			prev = r
			if p == self.root:
				self.Lt += 1
			else :
				p = p.suffixLink
			p = self.findCanonicalNode(p, i-1)
			r = self.testAndSplit(p, i)
		if prev != 0:
			prev.suffixLink = p
		return p

	def run(self, text):
		self.text = text
		self.len = len(text)
		pos = text[0]
		canonicalNodeAP = self.root
		self.root.left[pos] = 0
		self.root.right[pos] = self.len - 1
		for i in xrange(1, self.len):
			canonicalNodeEP = self.update(canonicalNodeAP, i)
			canonicalNodeAP = self.findCanonicalNode(canonicalNodeEP, i)


