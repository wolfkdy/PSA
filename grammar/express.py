#-*- coding: utf-8 -*-

from tokens import token_factory as fact

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

	def is_left_recursive(self):
		for tokens in self.right_tokens_list:
			if tokens[0] == self.left_token:
				return True
		return False	

	def eliminate_left_recursive(self):
		ill_tokens_list = [itms for itms in self.right_tokens_list \
				if itms[0] == self.left_token]
		healthy_tokens_list = [itms for itms in self.right_tokens_list \
				if itms[0] != self.left_token]			
		if len(ill_tokens_list) > 0:
			assert len(healthy_tokens_list) > 0, 'eliminate left recursive failed'
		else :
			return
		owned_tokens_list = []
		new_left_token = fact.create_unterminal(self.left_token.text + "'")		
		for tokens in healthy_tokens_list:
			owned_tokens_list.append(tokens + [new_left_token])
		self.right_tokens_list = owned_tokens_list

		new_tokens_list = []
		for tokens in ill_tokens_list:
			new_tokens_list.append(tokens[1 : ] + [new_left_token])
		new_tokens_list.append([fact.create_epsilon()])			
		new_exp = Express(new_left_token, new_tokens_list)
		return new_exp

	#replace every exp(Ai->Aj gama) with Ai -> delta1 gama | delta2 gama | delta3 gama ...
	#where Aj-> delta1 | delta2 | delta3 ... | deltak 
	def replace_leftmost_token(self, express):
		replace_token = express.left_token
		new_tokens_list = []
		for tokens in self.right_tokens_list:
			if tokens[0] != replace_token:
				new_tokens_list.append(tokens)
				continue
			for replace_tokens in express.right_tokens_list:
				new_tokens_list.append(replace_tokens + tokens[1 : ])	
		self.right_tokens_list = new_tokens_list
