#-*- coding: utf-8 -*-
#yet another ply(python yacc&lex)

import sys
sys.path.append('../')

from grammar import lalr
from grammar import grammar
from mini_regex import mini_regex

s_n = '0|1|2|3|4|5|6|7|8|9' #single number
lexical_tbl = {'number' : '(%s)(%s)*.(%s)*(%s)(%s)*' % (s_n, s_n, s_n, s_n, s_n),
		'+'   : '+',
		'-' 	: '-',
		'*'   : '*',
		'/'	: '/',
		'('	: '(',
		')'   : ')',
}
#syntax_tbl = ('e->e+t|t', 't->t*f|f', 'f->id')
syntax_tbl = ( 'e->e*e|e+e|n',)#, 'e->e+e', 'e->n')
#syntax_tbl = ('S->iSeS|iS|a', )
#syntax_tbl = ('S->S*S+S|n', )
#syntax_tbl = ('S->CC', 'C->cC|d')
left = (('+', 0), ('*', 1))
'''
syntax_tbl = ('exp->exp mul exp', 'exp->exp add exp', 'exp->exp chu exp', 'exp->exp sub exp',
		'exp->sub exp', 'exp->lbr exp rbr', 'exp->number')
'''
if __name__ == '__main__':
	gram_dict = {'start' : syntax_tbl[0], 'other' : syntax_tbl[1 : ], 'left_piority' : left}
	gram = grammar.prepare_gram(gram_dict)
	print gram.normalized_mode,'???'
	print '\n'
	lalr.gen_parsetbl(gram, './parsetab')	

