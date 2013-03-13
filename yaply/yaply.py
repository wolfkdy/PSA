#-*- coding: utf-8 -*-
#yet another ply(python yacc&lex)

import sys
import json
sys.path.append('../')

from grammar import lalr
from grammar import grammar
from mini_regex import mini_regex
'''
s_n = '0|1|2|3|4|5|6|7|8|9' #single number
lexical_tbl = {'NUM' : '(%s)(%s)*.(%s)*(%s)(%s)*' % (s_n, s_n, s_n, s_n, s_n),
		'ADD'   : '+',
		'SUB' 	: '-',
		'MUL'   : '\*',
		'DIV'	: '/',
		'LP'	: '\(',
		'RP'   : '\)',
}
syntax_tbl = ('E->E ADD E|E SUB E|E DIV E|E MUL E|LP E RP', 'E->NUM')
left = (('ADD', 0), ('SUB', 0), ('MUL', 1), ('DIV', 1))
'''

s_n = '0|1|2|3|4|5|6|7|8|9' #single number

#字符串不支持转意
#string literal
def gen_s_s():
	return '|'.join([chr(ord('a') + i) for i in xrange(27)])
	# 额，自己写的 regex 对枚举式正则处理效率很慢的。所以，字符串就先定义为小写字母组成吧
	return '|'.join([chr(i) for i in xrange(256) if chr(i) != "'"])

#name literal
def gen_n_s():
	s = '|'.join([chr(ord('a') + i) for i in xrange(27)])
	print s
	return '(%s)(%s)*' % (s, s, )
 
lexical_tbl = {'NUM' : '(%s)(%s)*.(%s)*(%s)(%s)*' % (s_n, s_n, s_n, s_n, s_n),
		'ADD'   : '+',
		'SUB' 	: '-',
		'MUL'   : '\*',
		'DIV'	: '/',
		'LP'	: '\(',
		'RP'   : '\)',
		'IF'    : 'if',
		'THEN'  : 'then',
		'ELSE'  : 'else',
		'ELSEIF' : 'elif',
		'WHILE' : 'while',
		'DO'    : 'do',
		'END'   : 'end',
		'RETURN' : 'return',
		'FUNCTION' : 'function',
		'STRING' : "'(%s)*'" % gen_s_s(),
		'NOT'    : 'not',
		'AND'	 : 'and',
		'OR'     : 'or',
		'EQ'	 : '=',
		'GT'	: '>',
		'GE'	: '>=',
		'LT' 	: '<',
		'LE' 	: '<=',
		'MOD'	: '%',
		'QUOT'  : ',',
		'NAME'  : gen_n_s(),
}
syntax_tbl = (  'expr->LP expr RP',
		'expr->expr EQ expr',
		'expr->expr LT expr',
		'expr->expr GT expr',
		'expr->expr GE expr',
		'expr->expr LE expr',
		'expr->expr ADD expr',
		'expr->expr SUB expr',
		'expr->expr MUL expr',
		'expr->expr DIV expr',
		'expr->NUM',
		'expr->STRING',	
		'expr->NAME',
		'expr->function_list',
		'expr->expr function_list expr',
		'expr->function_list expr',
		'expr->expr function_list',
		'expr->statlist',
		'function_list->function_list function', \
		'function_list->function', \
		'function->FUNCTION NAME LP parlist RP function_block END', \
		'parlist->NAME',\
		'parlist->parlist QUOT NAME',\
		'function_block->statlist ret',\
		'ret-> RETURN expr',\
		'statlist->statlist stat',
		'statlist->stat',
		'stat->IF expr THEN statlist elsepart END',
		'stat->NAME init',
		'elsepart->ELSE statlist',
		'elsepart->ELSEIF expr THEN statlist elsepart',
		'init->EQ expr',
)	

left = (('EQ', 0), ('ADD', 1), ('SUB', 1), ('MUL', 2), ('DIV', 2))
if __name__ == '__main__':
	gram_dict = {'start' : syntax_tbl[0], 'other' : syntax_tbl[1 : ], 'left_piority' : left}
	gram = grammar.prepare_gram(gram_dict)
#	lalr.gen_parsetbl(gram, './parsetab', './dot_str')	
	parse_tbl = json.load(open('./parsetab'))
	text = "tmp=5.13+(1.11/2.2*(3.1*4))"
	text = '''
	function func(a, b, c)
		d = b + c
		return d
	end
'''
	ret, token_list = mini_regex.parse(lexical_tbl, text)
	print ret, token_list
	lalr.parse(token_list, parse_tbl)
