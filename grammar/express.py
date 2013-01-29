#-*- coding: utf-8 -*-

class Express(object):
	def __init__(self, left_token, right_tokens_list):
		self.left_token = left_token
		self.right_tokens_list = right_tokens_list

	def __repr__(self):
		str_lst = []
		for tokens in self.right_tokens_list:
			str_lst.append(''.join([repr(token) for token in tokens]))
		
		return '%s->%s' % (repr(self.left_token), '|'.join(str_lst), )

	def get_expand_form(self):
		lst = []
		for item in self.right_tokens_list:
			lst.append(Express(self.left_token, [item]))
		return lst

	def is_expanded(self):
		return len(self.right_tokens_list) == 1


