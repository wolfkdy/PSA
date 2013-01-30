#-*- coding: utf-8 -*-

from express import Express
from tokens import token_factory as fact

LR1_ITEMSET_ID = 0
class LR1_ItemSet(object):
	def __init__(self):
		self.expresses = list()
		self.edges = dict()



#receive a lr1_express_list
def closure(express_lst):
	pass

'''
# S -> A dot Bc, a/b
# left : S , right : A dot Bc, acc_set : a/b, dot_pos : 1

def build_normal_lr1_item_set(gram):
'''	
