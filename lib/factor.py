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
		self.generateStates()
		self.tables = self.makeTable()

	def generateStates(self):

		states = self.iterateStates(self.input_variables)
		self.states = []
		for state in states:
			self.states.append(tuple(self.flatten(state)))

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

		# print the number of input_variables on which this factor depends
		fh.write(str(len(self.input_variables))+"\n")
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
			fh.write(str(index)+" "+str(prob)+"\n")
			index += 1
		fh.write("\n")

class AC_Factor(Factor):
	'''
	Represents an activating link for two nodes, with 3 states each: -1, 0, 1
	'''
	def makeTable(self):
		'''
		Iterate over all possible states of input variables: set the 
		'''
		MAJOR = 0.6
		INT = 0.2
		MINOR = 0.1

		self.probs = {}
		for state in self.states:
			if state[0] == 1 and state[1] == 1:
				# this is the neutral state: 
				# set to no effect state
				self.probs[state] = INT
			elif state[0] == state[1]:
				# activating, inactivating
				self.probs[state] = MAJOR
			else:
				self.probs[state] = MINOR

class IA_Factor(Factor):
	'''
	Represents an in-activating link for two nodes, with 3 states each: -1, 0, 1
	'''
	def makeTable(self):
		'''
		Iterate over all possible states of input variables: set the 
		'''
		MAJOR = 0.6
		INT = 0.2
		MINOR = 0.1

		self.probs = {}
		for state in self.states:
			if state[0] == 1 and state[1] == 1:
				# this is the neutral state: 
				# set to no effect state
				self.probs[state] = INT
			elif state[0] != state[1]:
				# activating, inactivating
				self.probs[state] = MAJOR
			else:
				self.probs[state] = MINOR

		
class UNIFORM_Factor(Factor):
	'''

	'''
	def makeTable(self):
		'''
		Iterate over all possible states of input variables: set the 
		'''
		UP = 0.5

		self.probs = {}
		for state in self.states:
			self.probs[state] = UP
			#print "\t".join([str(i) for i in self.flatten(state)])
		
		
