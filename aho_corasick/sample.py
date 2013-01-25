#given several short strings, find how many of them occurs in the longer one
# the sample below shows five small strs [she he say shr her], and a longer one: yasherhs,
# you may figout out that she, he her occurs in yasherhs, but say, shr do not

if __name__ == '__main__':
	samples = ['she', 'he', 'say', 'shr', 'her']
	automata =  AC_AutoMata()
	for sample in samples:
		automata.insert_sample(sample)
	automata.build_graph()
	automata.print_graph()
	print automata.find_occurs('yasherhs')







