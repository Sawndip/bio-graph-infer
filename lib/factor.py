import itertools

class Factor:

	'''
		Abstract Class describing a factor object
	'''


	def __init__(self, id, input_variables):
		'''
			-input_variables : a tuple of tuples, of the inputs and dimension:
				(1, 2), (2, 2), (3, 3), ...
			-id : unique id for this factor
		'''
		self.id = id
		self.input_variables = input_variables
		self.tables = self.makeTable()

	def iterateStates(self, variables):
		''' take the first variable, iterate over the possible states of the 
			next variables, in order
		'''
		states = []
		var, dim = variables[-1]

		if len(variables) == 1:
			for value in range(0,dim):
				states.append([value])
			return states

		for value in range(0,dim):
			for state in self.iterateStates(variables[0:len(variables)-1]):
				states.append([state, value])
			
		return states	

	def flatten(self, q):
		"""
		a recursive function that flattens a nested list q
		"""
		flat_q = []
		for x in q:
			# may have nested tuples or lists
			if type(x) in (list, tuple):
				flat_q.extend(self.flatten(x))
			else:
				flat_q.append(x)
		return flat_q
		
	def makeTable(self):
		
		raise Exception("Subclass must implement this method")

	def printFactor(self, fh):

		# print ID
		fh.write(str(self.id)+"\n")
		vars = []
		dims = []
		for (var, dim) in self.input_variables:
			vars.append(var)
			dims.append(dim)
		fh.write(" ".join([str(i) for i in vars])+"\n")
		fh.write(" ".join([str(i) for i in dims])+"\n")
		# the number of states following
		fh.write(str(len(self.states))+"\n")
		# enumerate each state
		index = 0
		for state in self.states:
			prob = self.probs[state]
			fh.write(str(index)+"\t"+str(prob)+"\n")
		fh.write("\n")

class UNIFORM_Factor(Factor):
	'''

	'''
	def makeTable(self):
		'''
		Iterate over all possible states of input variables: set the 
		'''
		UP = 0.1

		states = self.iterateStates(self.input_variables)
		self.states = []
		for state in states:
			self.states.append(tuple(self.flatten(state)))

		self.probs = {}
		for state in self.states:
			self.probs[state] = UP
			#print "\t".join([str(i) for i in self.flatten(state)])
		
		
