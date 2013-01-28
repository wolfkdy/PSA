
# S -> A dot Bc, a/b
# left : S , right : A dot Bc, acc_set : a/b, dot_pos : 1

LR1_NODE_CNT = 0
class LR1_Node(object):
	def __init__(self):
		global LR1_NODE_CNT
		self.left = None
		self.right = list()
		self.dot_pos = None
		self.acc_set = set()
		self.idx = LR1_NODE_CNT
		LR1_NODE_CNT += 1
