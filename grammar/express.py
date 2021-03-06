#-*- coding: utf-8 -*-
import tokens
from tokens import token_factory as fact

express_factory = None

class ExpressFactory(object):
	def __init__(self):
		#lr1 express is shared, while simple express is not
		self.lr1_expresses = dict()

	def create_lr1(self, left_token, right_tokens, dot_pos, acc_tokens):
		exp = LR1_Express(left_token, right_tokens, dot_pos, acc_tokens)
		key = repr(exp)
		if self.lr1_expresses.get(key) is None:
			self.lr1_expresses[key] = exp
		return self.lr1_expresses[key]

	def create_simple(self, left_token, right_tokens_list):
		return Express(left_token, right_tokens_list)	

def express_factory_init():
	global express_factory
	express_factory = ExpressFactory()

express_factory_init()

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
			lst.append(express_factory.create_simple(self.left_token, [item]))
		return lst

	def is_expanded(self):
		return len(self.right_tokens_list) == 1

	def is_left_recursive(self):
		for tokens in self.right_tokens_list:
			if tokens[0] == self.left_token:
				return True
		return False	

	def eliminate_left_recursive(self):
		if not self.is_left_recursive():
			return (self, None)
		ill_tokens_list = [itms for itms in self.right_tokens_list \
				if itms[0] == self.left_token]
		healthy_tokens_list = [itms for itms in self.right_tokens_list \
				if itms[0] != self.left_token]			
		if len(ill_tokens_list) > 0:
			assert len(healthy_tokens_list) > 0, 'eliminate left recursive failed'
		owned_tokens_list = []
		new_left_token = fact.create_unterminal(self.left_token.text + "'")		
		for tokens in healthy_tokens_list:
			owned_tokens_list.append(tokens + [new_left_token])
		self_cpy = express_factory.create_simple(self.left_token, owned_tokens_list)

		new_tokens_list = []
		for tokens in ill_tokens_list:
			new_tokens_list.append(tokens[1 : ] + [new_left_token])
		new_tokens_list.append([fact.create_epsilon()])			
		new_exp = express_factory.create_simple(new_left_token, new_tokens_list)
		return (self_cpy, new_exp)

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
		return express_factory.create_simple(self.left_token, self.right_tokens_list)

#every lr1_express is an expanded express
class LR1_Express(Express):
	def __init__(self, left_token, right_tokens, dot_pos, acc_tokens, piority = None):
		super(LR1_Express, self).__init__(left_token, [right_tokens])
		self.dot_pos = dot_pos
		self.acc_tokens = set()
		for token in acc_tokens:
			self.acc_tokens.add(token)
		if piority is not None:
			self.piority = piority
		else :
			right_tokens = self.get_right_tokens()
			piority = 0
			i = len(right_tokens) - 1
			while i >= 0:
				if tokens.is_terminal(right_tokens[i]):
					piority = right_tokens[i].piority
					break
				i -= 1
			self.piority = piority
	
	def get_right_tokens(self):
		return self.right_tokens_list[0]

	def get_token_after_dot(self):
		if self.dot_pos == len(self.right_tokens_list[0]):
			return fact.create_epsilon()
		return self.right_tokens_list[0][self.dot_pos]

	def get_token_lookahead_dot(self):
		if self.dot_pos >= len(self.right_tokens_list[0]) - 1:
			return fact.create_epsilon()
		return self.right_tokens_list[0][self.dot_pos + 1]

	def is_pending_reduce(self):
		if self.dot_pos == len(self.right_tokens_list[0]):
			return True
		#easy to ignore: if all tokens after dot are eps, the exp is also pending reduce
		for i in xrange(self.dot_pos, len(self.right_tokens_list[0])):
			if not tokens.is_epsilon(self.right_tokens_list[0][i]):
				return False
		return True	

	def get_core_repr(self):
		s = ''
		s += repr(self.left_token) + '->'
		for i in xrange(self.dot_pos):
			s += repr(self.right_tokens_list[0][i])
		s += '·'
		for i in xrange(self.dot_pos, len(self.right_tokens_list[0])):
			s += repr(self.right_tokens_list[0][i])
		return s

	def get_simple_repr(self):
		return super(LR1_Express, self).__repr__()

	def __repr__(self):
		s = self.get_core_repr() + ','
		lst = list(self.acc_tokens)
		lst.sort(lambda x, y : cmp(x.text, y.text))
		s += '|'.join([itm.text for itm in lst])
		return s


def is_same_core(exp_a, exp_b):
	if exp_a.dot_pos != exp_b.dot_pos:
		return False
	a_right = exp_a.get_right_tokens()
	b_right = exp_b.get_right_tokens()
	if len(a_right) != len(b_right):
		return False
	for i in xrange(len(a_right)):
		if a_right[i] != b_right[i]:
			return False
	return True


