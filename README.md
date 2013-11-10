PSA
===

Python String Automata

some experimental implemention of string automations written in python

Contains a fully implemented LALR(1) compiler frontend( may be imaged as ply or lex&yacc)

(AhoCorasick AutoMata, 
Ukkonen's suffixTree, 
MYT's automata for compiling regex and lexical analysis
LR1 and LALR(1) syntax parse table
)

most of the implementions are with low time complexity, 

however, with the slow speed of python, the overall performance is not very good

the best practise is implementing it with c/c++ 
