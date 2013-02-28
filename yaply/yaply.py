#-*- coding: utf-8 -*-
#yet another ply(python yacc&lex)

import sys
import json
sys.path.append('../')

from grammar import lalr
from grammar import grammar
from mini_regex import mini_regex

s_n = '0|1|2|3|4|5|6|7|8|9' #single number
lexical_tbl = {'NUM' : '(%s)(%s)*.(%s)*(%s)(%s)*' % (s_n, s_n, s_n, s_n, s_n),
		'ADD'   : '+',
		'SUB' 	: '-',
		'MUL'   : '!',
		'DIV'	: '/',
		'LP'	: '[',
		'RP'   : ']',
}
syntax_tbl = ('E->E ADD E|E SUB E|E DIV E|E MUL E|LP E RP', 'E->NUM')
left = (('ADD', 0), ('SUB', 0), ('MUL', 1), ('DIV', 1))
if __name__ == '__main__':
	gram_dict = {'start' : syntax_tbl[0], 'other' : syntax_tbl[1 : ], 'left_piority' : left}
	gram = grammar.prepare_gram(gram_dict)
	lalr.gen_parsetbl(gram, './parsetab', './dot_str')	
	parse_tbl = json.load(open('./parsetab'))
	ret, token_list = mini_regex.parse(lexical_tbl, '5+[1/2![3!4]]')
	print token_list
	lalr.parse(token_list, parse_tbl)
